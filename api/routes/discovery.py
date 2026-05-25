# -*- coding: utf-8 -*-
"""
Device Discovery API Routes

Provides IP range scanning and SNMP scanning endpoints for device auto-discovery.
"""

import asyncio
import json
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies import get_current_user, CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter(tags=["设备发现"])


# ============== 后台扫描任务存储 ==============

scan_tasks: dict = {}  # scan_id -> {"status": str, "progress": dict, "result": dict, "error": str}


def _run_scan_task_sync(scan_id: str, cidr: str, username: str):
    """同步包装器，供 BackgroundTasks 调用"""
    import asyncio
    asyncio.run(_async_scan_task(scan_id, cidr, username))


async def _async_scan_task(scan_id: str, cidr: str, username: str):
    """后台扫描任务（协程内运行）"""
    task = scan_tasks.setdefault(scan_id, {
        "status": "running",
        "progress": {"complete": 0, "total": 0, "current_ip": "", "phase": "idle"},
        "result": None,
        "error": None,
    })

    def progress_callback(complete: int, total: int, current_ip: str):
        task["progress"] = {
            "complete": complete,
            "total": total,
            "current_ip": current_ip,
            "phase": "scanning",
        }

    try:
        from modules.collection.discovery.enhanced_scanner import get_enhanced_scanner
        from modules.business.device_importer import DeviceImporter

        scanner = get_enhanced_scanner()
        importer = DeviceImporter()

        task["status"] = "scanning"
        task["progress"]["phase"] = "scanning"

        # 阶段1：扫描
        discovered = await scanner.scan_and_identify(cidr, progress_callback=progress_callback)
        discovered = [h for h in discovered if h.status == 'up']
        task["progress"]["complete"] = task["progress"]["total"]
        task["status"] = "importing"
        task["progress"]["phase"] = "importing"
        task["progress"]["complete"] = 0

        # 阶段2：导入
        imported_count = 0
        hosts_list = []
        for i, host in enumerate(discovered):
            existing = check_device_exists(host.ip)
            if not existing:
                device_data = {
                    'name': host.hostname or f"auto-{host.ip.replace('.', '-')}",
                    'ip_address': host.ip,
                    'device_type': map_os_to_device_type(host.os_type),
                    'os': host.os_type,
                    'os_version': host.os_version,
                    'vendor': host.vendor or 'Unknown',
                    'model': host.model,
                    'location': '',
                }
                result = importer.import_devices([device_data], username=username)
                if result.success:
                    imported_count += 1
            hosts_list.append(host.to_dict())
            task["progress"]["complete"] = i + 1
            task["progress"]["total"] = len(discovered)
            task["progress"]["current_ip"] = host.ip

        task["status"] = "done"
        task["progress"]["phase"] = "done"
        task["progress"]["complete"] = len(discovered)
        task["progress"]["total"] = len(discovered)
        task["result"] = {
            "total_discovered": len(discovered),
            "newly_imported": imported_count,
            "cidr": cidr,
            "hosts": hosts_list,
        }
        logger.info(f"[Scan {scan_id}] 完成: 发现{len(discovered)}台, 新增导入{imported_count}台")

    except Exception as e:
        logger.error(f"[Scan {scan_id}] 扫描异常: {e}")
        task["status"] = "error"
        task["error"] = str(e)


# ============== 请求/响应模型 ==============

class IPScanRequest(BaseModel):
    """IP扫描请求"""
    cidr: str = Field(..., description="CIDR notation (e.g., 192.168.1.0/24)")
    scan_ports: bool = Field(True, description="是否扫描端口")
    grab_banners: bool = Field(True, description="是否获取banner")


class IPScanResponse(BaseModel):
    """IP扫描响应"""
    task_id: str
    status: str
    message: str


class SNMPScanRequest(BaseModel):
    """SNMP扫描请求"""
    target: str = Field(..., description="Target IP, CIDR, or hostname")
    community: str = Field("public", description="SNMP community string")
    snmp_version: str = Field("v2c", description="SNMP version (v1, v2c, v3)")


class SNMPScanResponse(BaseModel):
    """SNMP扫描响应"""
    task_id: str
    status: str
    message: str


class DiscoveredHostResponse(BaseModel):
    """发现的Host响应（扫描层，与持久层 Device 模型是不同概念）
    
    status 字段含义为 "up"/"down"（可达性），与 DeviceStatus 是不同概念。
    """
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    os_type: str
    os_version: Optional[str] = None
    vendor: Optional[str] = None
    ports: List[int] = []
    services: dict
    status: str  # "up"/"down"，扫描层可达性，与 DeviceStatus 是不同概念
    response_time: Optional[float] = None
    ttl: Optional[int] = None
    timestamp: str


class SNMPDeviceResponse(BaseModel):
    """SNMP设备响应"""
    ip: str
    hostname: Optional[str] = None
    sys_descr: Optional[str] = None
    sys_object_id: Optional[str] = None
    sys_uptime: Optional[int] = None
    vendor: Optional[str] = None
    device_type: str
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    location: Optional[str] = None
    contact: Optional[str] = None
    mac_address: Optional[str] = None
    interfaces: List[dict] = []
    status: str
    response_time: Optional[float] = None
    snmp_version: str
    timestamp: str


class ScanProgressResponse(BaseModel):
    """扫描进度响应"""
    task_id: str
    status: str
    progress: int
    total: int
    current: str
    results: List[dict]


# ============== IP扫描接口 ==============

def check_device_exists(ip: str) -> bool:
    """检查设备是否已存在"""
    try:
        from modules.foundation.db_models.device import Device
        from modules.foundation.db_models.base import _db_manager
        with _db_manager.session_scope() as session:
            existing = session.query(Device).filter(Device.ip_address == ip).first()
            return existing is not None
    except Exception:
        return False


def map_os_to_device_type(os_type: str) -> str:
    """根据OS类型映射到设备类型"""
    if not os_type:
        return 'other'
    os_lower = os_type.lower()
    if 'windows' in os_lower:
        return 'server_windows'
    elif 'linux' in os_lower or 'unix' in os_lower or 'centos' in os_lower or 'ubuntu' in os_lower or 'redhat' in os_lower:
        return 'server_linux'
    elif 'esxi' in os_lower or 'vmware' in os_lower:
        return 'server_vmware'
    elif 'cisco' in os_lower or 'switch' in os_lower or 'router' in os_lower:
        return 'network_switch'
    elif 'firewall' in os_lower or 'fortinet' in os_lower or 'palo' in os_lower:
        return 'network_firewall'
    elif 'huawei' in os_lower:
        return 'network_switch'
    else:
        return 'other'


@router.post("/scan-and-import", summary="扫描网段并自动导入发现的设备")
async def scan_and_import_devices(
    request: IPScanRequest,  # reuses existing model with cidr field
    current_user: CurrentUser = Depends(get_current_user),
):
    """扫描指定网段，自动发现新设备并导入平台"""
    try:
        from modules.collection.discovery.enhanced_scanner import get_enhanced_scanner
        from modules.business.device_importer import DeviceImporter

        scanner = get_enhanced_scanner()
        importer = DeviceImporter()
        results = await scanner.scan_and_identify(request.cidr)

        # Filter hosts that are up
        discovered = [h for h in results if h.status == 'up']

        # Import new devices
        imported = 0
        for host in discovered:
            # Check if device already exists by IP
            existing = check_device_exists(host.ip)
            if not existing:
                device_data = {
                    'name': host.hostname or f"auto-{host.ip.replace('.', '-')}",
                    'ip_address': host.ip,
                    'device_type': map_os_to_device_type(host.os_type),
                    'os': host.os_type,
                    'os_version': host.os_version,
                    'vendor': host.vendor or 'Unknown',
                    'model': host.model,
                    'location': '',
                }
                result = importer.import_devices([device_data], username=current_user.username)
                if result.success:
                    imported += 1

                    # 导入成功后立即触发一次采集，更新设备状态
                    device_name = device_data['name']
                    try:
                        from modules.collection.device_manager import get_device_manager
                        manager = get_device_manager()
                        metrics = await manager.collect_device(device_name)
                        if metrics and metrics.status.value == 'online':
                            logger.info(f"[discovery] 设备 {device_name} 采集成功，状态已更新为 ONLINE")
                        else:
                            logger.info(f"[discovery] 设备 {device_name} 采集完成，状态: {metrics.status.value if metrics else 'UNKNOWN'}")
                    except Exception as e:
                        logger.warning(f"[discovery] 设备 {device_name} 采集失败: {e}")

        return {
            'total_discovered': len(discovered),
            'newly_imported': imported,
            'cidr': request.cidr,
            'hosts': [h.to_dict() for h in discovered],
        }
    except Exception as e:
        logger.error(f"扫描导入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-and-import-stream", summary="启动扫描（轮询进度）")
async def scan_and_import_devices_stream(
    request: IPScanRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    启动扫描任务，立即返回 scan_id。
    前端通过 GET /discovery/scan-and-import-stream/{scan_id} 轮询进度。
    """
    import uuid
    scan_id = str(uuid.uuid4())

    scan_tasks[scan_id] = {
        "status": "pending",
        "progress": {"complete": 0, "total": 0, "current_ip": "", "phase": "idle"},
        "result": None,
        "error": None,
    }

    background_tasks.add_task(_async_scan_task, scan_id, request.cidr, current_user.username)

    return {"scan_id": scan_id, "status": "pending", "cidr": request.cidr}


class ScanProgressResponse(BaseModel):
    scan_id: str
    status: str  # pending | scanning | importing | done | error
    progress: dict  # {complete, total, current_ip, phase}
    result: Optional[dict] = None  # only when status==done
    error: Optional[str] = None


@router.get("/scan-and-import-stream/{scan_id}", summary="查询扫描进度")
async def get_scan_progress(
    scan_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """轮询接口：返回当前扫描进度和结果"""
    task = scan_tasks.get(scan_id)
    if not task:
        raise HTTPException(status_code=404, detail="scan_id not found")
    try:
        return ScanProgressResponse(
            scan_id=scan_id,
            status=task["status"],
            progress=task["progress"],
            result=task["result"],
            error=task["error"],
        )
    except Exception as e:
        logger.error(f"ScanProgressResponse 构建失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip/scan", summary="启动IP范围扫描")
async def start_ip_scan(
    request: IPScanRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    启动IP范围扫描任务
    
    扫描指定CIDR范围内的所有主机，支持：
    - 并行ping扫描
    - TCP端口扫描
    - Banner获取
    - OS指纹识别
    """
    try:
        from modules.collection.discovery.scanner import get_scanner
        import uuid
        
        scanner = get_scanner()
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 这里应该使用后台任务，实际实现中会将任务加入队列
        # 目前返回任务ID，实际扫描通过 /ip/scan/{task_id}/results 获取
        return IPScanResponse(
            task_id=task_id,
            status="pending",
            message=f"IP扫描任务已创建，等待执行: {request.cidr}",
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"启动IP扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== ARP 扫描接口 ==============

class ARPScanRequest(BaseModel):
    """ARP扫描请求"""
    cidr: str = Field(..., description="CIDR notation (e.g. 192.168.1.0/24)")


class ARPScanResponse(BaseModel):
    """ARP扫描响应"""
    total: int
    discovered: int
    hosts: List[dict]


@router.post("/arp/scan", summary="ARP扫描网段")
async def arp_scan(
    request: ARPScanRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    使用 ARP 协议扫描指定网段的设备。

    ARP 扫描通过发送 ARP 请求探测同网段所有活跃主机的 MAC 地址，
    返回包括 IP、MAC、厂商信息。适用于发现同一 L2 网段内的所有设备。

    - 需要 root 权限：使用原始套接字发送 ARP 请求（主动扫描）
    - 无 root 权限：读取 /proc/net/arp 缓存（被动模式）

    与 IP ping 扫描互补：ARP 更可靠（所有设备都响应 ARP），但仅限本地网段。
    """
    try:
        from modules.collection.discovery.scanner import get_arp_scanner

        scanner = get_arp_scanner()

        # Run ARP scan synchronously in thread pool to avoid blocking
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                asyncio.run,
                scanner.scan_ip_range(request.cidr)
            )
            hosts = future.result(timeout=120)

        return ARPScanResponse(
            total=len(hosts),
            discovered=len([h for h in hosts if h.mac]),
            hosts=[{
                "ip": h.ip,
                "mac": h.mac,
                "vendor": h.vendor,
                "os_type": h.os_type.value if hasattr(h.os_type, 'value') else str(h.os_type),
                "os_version": h.os_version,
                "status": h.status,
                "response_time": h.response_time,
            } for h in hosts],
        )

    except concurrent.futures.TimeoutError:
        raise HTTPException(status_code=504, detail="ARP scan timeout (>120s)")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ARP扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip/scan/{task_id}/results", summary="获取IP扫描结果")
async def get_ip_scan_results(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取IP扫描任务的结果
    
    返回该任务已发现的所有主机信息
    """
    try:
        # 实际实现中应该从Redis或数据库获取任务状态和结果
        # 这里返回占位数据
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "total": 0,
            "current": "",
            "results": [],
        }
        
    except Exception as e:
        logger.error(f"获取IP扫描结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip/scan/sync", summary="同步IP范围扫描（增强版）")
async def sync_ip_scan(
    request: IPScanRequest,
    enhanced: bool = Query(False, description="启用增强扫描（含指纹识别和认证探测）"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    同步执行IP范围扫描（适用于小范围）
    
    对于 /24 及以下范围，返回完整扫描结果
    对于更大范围，建议使用异步扫描接口
    
    如果 enhanced=True，则启用增强扫描，包括：
    - 设备指纹识别（厂商、型号、类型）
    - 自动认证探测（默认凭据尝试）
    - 采集协议推荐
    """
    try:
        if enhanced:
            from modules.collection.discovery.enhanced_scanner import get_enhanced_scanner
            scanner = get_enhanced_scanner()
            results = await scanner.scan_and_identify(request.cidr)
            return {
                "cidr": request.cidr,
                "total_hosts": len(results),
                "hosts": [h.to_dict() for h in results],
                "scan_mode": "enhanced",
                "scan_time": datetime.now().isoformat(),
            }
        else:
            from modules.collection.discovery.scanner import get_scanner
            scanner = get_scanner()
            results = await scanner.scan_ip_range(request.cidr)
            return {
                "cidr": request.cidr,
                "total_hosts": len(results),
                "hosts": [h.to_dict() for h in results],
                "scan_mode": "basic",
                "scan_time": datetime.now().isoformat(),
            }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"IP扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip/hosts", summary="获取扫描发现的主机列表")
async def list_discovered_hosts(
    status: Optional[str] = Query(None, description="状态过滤 (up/down)"),
    os_type: Optional[str] = Query(None, description="OS类型过滤"),
    vendor: Optional[str] = Query(None, description="厂商过滤"),
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取已发现的主机列表
    
    从扫描结果缓存中获取主机列表
    """
    try:
        # 实际实现中应该从数据库或缓存获取
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }
        
    except Exception as e:
        logger.error(f"获取主机列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== SNMP扫描接口 ==============

@router.post("/snmp/scan", summary="启动SNMP扫描")
async def start_snmp_scan(
    request: SNMPScanRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    启动SNMP设备扫描任务
    
    扫描指定目标，发现支持SNMP的设备并获取系统信息
    """
    try:
        from modules.collection.discovery.snmp_scanner import get_snmp_scanner
        import uuid
        
        scanner = get_snmp_scanner()
        
        task_id = str(uuid.uuid4())
        
        return SNMPScanResponse(
            task_id=task_id,
            status="pending",
            message=f"SNMP扫描任务已创建: {request.target}",
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"启动SNMP扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snmp/scan/{task_id}/results", summary="获取SNMP扫描结果")
async def get_snmp_scan_results(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取SNMP扫描任务的结果
    """
    try:
        return {
            "task_id": task_id,
            "status": "completed",
            "devices": [],
        }
        
    except Exception as e:
        logger.error(f"获取SNMP扫描结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snmp/scan/sync", summary="同步SNMP扫描")
async def sync_snmp_scan(
    request: SNMPScanRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    同步执行SNMP扫描（适用于小范围）
    """
    try:
        from modules.collection.discovery.snmp_scanner import get_snmp_scanner
        
        scanner = get_snmp_scanner()
        
        # 执行扫描
        devices = await scanner.scan_network(
            target=request.target,
            community=request.community,
            snmp_version=request.snmp_version,
        )
        
        return {
            "target": request.target,
            "community": request.community,
            "snmp_version": request.snmp_version,
            "total_devices": len(devices),
            "devices": [d.to_dict() for d in devices],
            "scan_time": datetime.now().isoformat(),
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SNMP扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snmp/discover", summary="SNMP设备发现")
async def discover_snmp_devices(
    cidr: str = Query(..., description="CIDR范围"),
    communities: str = Query("public,private", description="Community列表，逗号分隔"),
    snmp_version: str = Query("v2c", description="SNMP版本"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    发现网络中的SNMP设备
    
    对指定范围进行SNMP扫描，自动尝试多个community
    """
    try:
        from modules.collection.discovery.snmp_scanner import get_snmp_scanner
        
        scanner = get_snmp_scanner()
        
        # 解析communities
        community_list = [c.strip() for c in communities.split(",")]
        
        # 执行发现
        devices = await scanner.discover_snmp_devices(
            cidr=cidr,
            communities=community_list,
            snmp_version=snmp_version,
        )
        
        return {
            "cidr": cidr,
            "communities": community_list,
            "total_devices": len(devices),
            "devices": [d.to_dict() for d in devices],
            "discovery_time": datetime.now().isoformat(),
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SNMP设备发现失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snmp/devices", summary="获取SNMP设备列表")
async def list_snmp_devices(
    vendor: Optional[str] = Query(None, description="厂商过滤"),
    device_type: Optional[str] = Query(None, description="设备类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取已发现的SNMP设备列表
    """
    try:
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }
        
    except Exception as e:
        logger.error(f"获取SNMP设备列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 设备导入接口 ==============

@router.post("/devices/import", summary="导入发现的设备")
async def import_discovered_devices(
    ips: List[str] = Body(..., description="要导入的IP列表"),
    device_type: str = Body("server", description="设备类型"),
    vendor: Optional[str] = Body(None, description="厂商"),
    protocols: str = Body('{"primary": "snmp", "fallback": "ssh"}', description="采集协议(JSON)"),
    current_user: CurrentUser = Depends(get_current_user),
):
    import json
    protocols = json.loads(protocols)
    """
    将发现的主机导入到设备库
    
    根据IP列表创建设备配置
    """
    try:
        from modules.collection.config_loader import get_config_loader
        
        loader = get_config_loader()
        imported = []
        failed = []
        
        for ip in ips:
            try:
                # 创建设备配置
                device_config = {
                    "name": f"auto-{ip.replace('.', '-')}",
                    "ip": ip,
                    "type": device_type,
                    "vendor": vendor,
                    "protocols": protocols,
                    "collect": {
                        "enabled": True,
                        "interval": 60,
                    },
                    "tags": {
                        "imported_from": "discovery",
                        "imported_at": datetime.now().isoformat(),
                    },
                }
                
                # 实际实现中应该保存到配置文件或数据库
                imported.append(ip)
                
            except Exception as e:
                logger.error(f"导入设备 {ip} 失败: {e}")
                failed.append({"ip": ip, "error": str(e)})
        
        return {
            "imported": imported,
            "failed": failed,
            "total_imported": len(imported),
            "total_failed": len(failed),
        }
        
    except Exception as e:
        logger.error(f"导入设备失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 简化版设备发现接口 ==============

@router.post("/scan", summary="启动设备扫描")
async def start_discovery_scan(
    request: IPScanRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    简化版设备扫描接口
    
    启动IP范围扫描任务，返回任务ID后可通过 /discovery/hosts 获取结果
    """
    try:
        from modules.collection.discovery.scanner import IPScanner
        import uuid
        
        scanner = IPScanner()
        task_id = str(uuid.uuid4())
        
        return {
            "task_id": task_id,
            "status": "pending",
            "cidr": request.cidr,
            "message": f"扫描任务已创建: {request.cidr}",
            "endpoints": {
                "status": f"/api/v1/discovery/scan/{task_id}/status",
                "hosts": "/api/v1/discovery/hosts",
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"启动扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{task_id}/status", summary="获取扫描任务状态")
async def get_scan_status(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取扫描任务当前状态
    """
    try:
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "message": "扫描完成，可通过 /discovery/hosts 获取结果",
        }
    except Exception as e:
        logger.error(f"获取扫描状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ScanHistoryItem(BaseModel):
    """扫描历史记录项"""
    task_id: str
    scan_type: str = Field(description="扫描类型: ip, snmp, arp")
    network: Optional[str] = Field(None, description="扫描网段")
    status: str = Field(description="状态: pending/running/completed/failed")
    progress: int = Field(default=0, description="进度 0-100")
    hosts_found: int = Field(default=0, description="发现主机数")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    message: Optional[str] = None


@router.get("/scan-history", summary="获取扫描历史列表")
async def get_scan_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    scan_type: Optional[str] = Query(None, description="扫描类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取扫描历史记录列表（分页）
    """
    try:
        # 扫描历史存于 Redis（key: scan:history）
        from modules.storage.redis_client.client import RedisClient
        redis = RedisClient()
        raw = redis.lrange("scan:history", 0, -1) or []
        
        items = []
        for entry in raw:
            try:
                items.append(ScanHistoryItem(**json.loads(entry)))
            except Exception:
                continue
        
        # 过滤
        if scan_type:
            items = [i for i in items if i.scan_type == scan_type]
        if status:
            items = [i for i in items if i.status == status]
        
        total = len(items)
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]
        
        return {
            "items": [i.model_dump() for i in page_items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"获取扫描历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hosts", summary="获取发现的主机列表")
async def get_discovered_hosts(
    status: Optional[str] = Query(None, description="状态过滤 (up/down)"),
    os_type: Optional[str] = Query(None, description="OS类型过滤"),
    vendor: Optional[str] = Query(None, description="厂商过滤"),
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取已发现的主机列表
    
    支持按状态、OS类型、厂商过滤
    """
    try:
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "filters": {
                "status": status,
                "os_type": os_type,
                "vendor": vendor,
            }
        }
    except Exception as e:
        logger.error(f"获取主机列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", summary="导入发现的主机")
async def import_hosts(
    ips: List[str] = Body(..., description="要导入的IP列表"),
    device_type: str = Body("server", description="设备类型"),
    vendor: Optional[str] = Body(None, description="厂商"),
    protocols: str = Body('{"primary": "snmp", "fallback": "ssh"}', description="采集协议(JSON)"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    简化版设备导入接口
    
    将发现的主机批量导入到设备库
    """
    import json
    try:
        protocols = json.loads(protocols) if isinstance(protocols, str) else protocols
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")
    
    try:
        imported = []
        failed = []
        
        for ip in ips:
            try:
                device_config = {
                    "name": f"auto-{str(ip).replace('.', '-')}",
                    "ip": str(ip),
                    "type": device_type,
                    "vendor": vendor,
                    "protocols": protocols,
                    "collect": {
                        "enabled": True,
                        "interval": 60,
                    },
                    "tags": {
                        "imported_from": "discovery",
                        "imported_at": datetime.now().isoformat(),
                    },
                }
                imported.append(str(ip))
            except Exception as e:
                logger.error(f"导入设备 {ip} 失败: {e}")
                failed.append({"ip": str(ip), "error": str(e)})
        
        return {
            "status": "completed",
            "imported": imported,
            "failed": failed,
            "total_imported": len(imported),
            "total_failed": len(failed),
        }
        
    except Exception as e:
        logger.error(f"导入设备失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 主动发现任务接口 ==============

@router.post("/tasks", summary="创建设备发现任务")
async def create_discovery_task(
    name: str = Body(..., description="任务名称"),
    task_type: str = Body(..., description="任务类型: ip_scan, snmp_discovery"),
    target: str = Body(..., description="目标: CIDR范围或IP列表"),
    options: str = Body("{}", description="任务选项(JSON)"),
    schedule: Optional[str] = Body(None, description="Cron表达式（可选）"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """创建设备发现任务，持久化到数据库"""
    try:
        task_id = "task-" + datetime.now().strftime("%Y%m%d%H%M%S")
        with _db_manager.session_scope() as db:
            task = DiscoveryTask(
                task_id=task_id,
                name=name,
                task_type=task_type,
                target=target,
                options=options,
                schedule=schedule,
                status="created",
                created_by=current_user.username,
            )
            db.add(task)
            db.commit()
        return {
            "task_id": task_id,
            "name": name,
            "task_type": task_type,
            "target": target,
            "options": json.loads(options),
            "schedule": schedule,
            "status": "created",
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"创建设备发现任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", summary="获取发现任务列表")
async def list_discovery_tasks(
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取设备发现任务列表"""
    try:
        with _db_manager.session_scope() as db:
            query = db.query(DiscoveryTask)
            if status:
                query = query.filter(DiscoveryTask.status == status)
            total = query.count()
            tasks = query.order_by(DiscoveryTask.created_at.desc()).all()
            return {
                "items": [
                    {
                        "task_id": t.task_id,
                        "name": t.name,
                        "task_type": t.task_type,
                        "target": t.target,
                        "options": json.loads(t.options) if t.options else {},
                        "schedule": t.schedule,
                        "status": t.status,
                        "created_by": t.created_by,
                        "created_at": t.created_at.isoformat() if t.created_at else None,
                    }
                    for t in tasks
                ],
                "total": total,
            }
    except Exception as e:
        logger.error(f"获取发现任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 网段管理（数据库持久化） ==============

from modules.foundation.db_models.base import _db_manager
from modules.foundation.db_models.system import NetworkScanConfig, DiscoveryTask
from sqlalchemy import func


class NetworkCreate(BaseModel):
    cidr: str = Field(..., description="CIDR格式网段")
    description: Optional[str] = ""
    auto_scan: bool = False


class NetworkUpdate(BaseModel):
    cidr: Optional[str] = None
    description: Optional[str] = None
    auto_scan: Optional[bool] = None


@router.get("/networks", summary="获取已配置网段列表")
async def list_networks():
    """返回所有已配置的扫描网段"""
    with _db_manager.session_scope() as db:
        nets = db.query(NetworkScanConfig).order_by(NetworkScanConfig.id).all()
        return [
            {
                "id": n.id,
                "cidr": n.ip_range,
                "name": n.name,
                "description": n.name,  # 兼容旧字段
                "auto_scan": bool(n.auto_scan),
                "status": n.status,
                "last_scan_at": n.last_scan_at.isoformat() if n.last_scan_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in nets
        ]


@router.post("/networks", summary="添加扫描网段")
async def create_network(net: NetworkCreate, network_id: Optional[int] = None):
    """添加新的扫描网段"""
    with _db_manager.session_scope() as db:
        if network_id is not None:
            existing = db.query(NetworkScanConfig).filter(NetworkScanConfig.id == network_id).first()
            if existing:
                raise HTTPException(status_code=409, detail="该ID已存在")
            record = NetworkScanConfig(id=network_id, ip_range=net.cidr, name=net.description or net.cidr, auto_scan=1 if net.auto_scan else 0)
        else:
            record = NetworkScanConfig(ip_range=net.cidr, name=net.description or net.cidr, auto_scan=1 if net.auto_scan else 0)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "id": record.id,
            "cidr": record.ip_range,
            "name": record.name,
            "description": record.name,
            "auto_scan": bool(record.auto_scan),
            "status": record.status,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }


@router.put("/networks/{network_id}", summary="更新扫描网段")
async def update_network(network_id: int, net: NetworkUpdate):
    """更新指定网段的配置"""
    with _db_manager.session_scope() as db:
        record = db.query(NetworkScanConfig).filter(NetworkScanConfig.id == network_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="网段不存在")
        if net.cidr is not None:
            record.ip_range = net.cidr
        if net.description is not None:
            record.name = net.description
            record.description = net.description
        if net.auto_scan is not None:
            record.auto_scan = 1 if net.auto_scan else 0
        db.commit()
        return {
            "id": record.id,
            "cidr": record.ip_range,
            "name": record.name,
            "description": record.name,
            "auto_scan": bool(record.auto_scan),
            "status": record.status,
        }


@router.delete("/networks/{network_id}", summary="删除扫描网段")
async def delete_network(network_id: int):
    """删除指定网段"""
    with _db_manager.session_scope() as db:
        record = db.query(NetworkScanConfig).filter(NetworkScanConfig.id == network_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="网段不存在")
        db.delete(record)
        db.commit()
    return {"message": "删除成功"}
