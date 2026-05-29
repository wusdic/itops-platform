"""
资产管理API路由
提供资产信息管理、配置管理等接口
"""

import asyncio
from typing import Optional, List
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from api.dependencies import get_db, get_current_user, CurrentUser, PaginationParams
from modules.foundation.db_models.device import Device, DeviceGroup, BusinessSystem, DeviceType as DBDeviceType, DeviceStatus as DBDeviceStatus


router = APIRouter()


# ============== 枚举定义 ==============

class DeviceType(str, Enum):
    """设备类型"""
    SERVER = "server"
    NETWORK = "network"
    STORAGE = "storage"
    SECURITY = "security"
    VIRTUAL = "virtual"
    CLOUD = "cloud"
    OTHER = "other"


class DeviceStatus(str, Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


# ============== 请求/响应模型 ==============

class DeviceCreate(BaseModel):
    """创建设备"""
    hostname: str = Field(..., description="主机名")
    ip_address: str = Field(..., description="IP地址")
    device_type: str = Field(..., description="设备类型")
    os_type: Optional[str] = Field(None, description="操作系统类型")
    os_version: Optional[str] = Field(None, description="操作系统版本")
    manufacturer: Optional[str] = Field(None, description="制造商")
    model: Optional[str] = Field(None, description="型号")
    serial_number: Optional[str] = Field(None, description="序列号")
    cpu: Optional[str] = Field(None, description="CPU信息")
    memory: Optional[str] = Field(None, description="内存信息")
    disk: Optional[str] = Field(None, description="磁盘信息")
    network_interfaces: Optional[dict] = Field(None, description="网络接口")
    location: Optional[str] = Field(None, description="位置")
    idc: Optional[str] = Field(None, description="机房")
    cabinet: Optional[str] = Field(None, description="机柜")
    business_id: Optional[int] = Field(None, description="业务系统ID")
    tags: Optional[str] = Field(None, description="标签")
    status: Optional[str] = Field("offline", description="状态")


class DeviceUpdate(BaseModel):
    """更新设备"""
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    idc: Optional[str] = None
    cabinet: Optional[str] = None
    business_id: Optional[int] = None
    tags: Optional[str] = None
    remark: Optional[str] = None


class DeviceResponse(BaseModel):
    """设备响应"""
    id: int
    hostname: str
    ip_address: str
    device_type: str
    status: str
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    idc: Optional[str] = None
    cabinet: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== 设备管理接口 ==============

def _map_device_type(device_type: str) -> DBDeviceType:
    """映射前端设备类型到数据库枚举"""
    mapping = {
        'server': DBDeviceType.SERVER_LINUX,
        'network': DBDeviceType.NETWORK_SWITCH,
        'storage': DBDeviceType.STORAGE_NAS,
        'security': DBDeviceType.SECURITY_IPS,
        'virtual': DBDeviceType.SERVER_VMWARE,
        'cloud': DBDeviceType.OTHER,
        'other': DBDeviceType.OTHER,
    }
    return mapping.get(device_type, DBDeviceType.OTHER)


def _map_device_status(status: str) -> DBDeviceStatus:
    """映射前端设备状态到数据库枚举"""
    mapping = {
        'online': DBDeviceStatus.ONLINE,
        'offline': DBDeviceStatus.OFFLINE,
        'warning': DBDeviceStatus.WARNING,
        'critical': DBDeviceStatus.CRITICAL,
        'maintenance': DBDeviceStatus.MAINTENANCE,
        'unknown': DBDeviceStatus.UNKNOWN,
    }
    return mapping.get(status.lower(), DBDeviceStatus.OFFLINE)


def _device_to_dict(device: Device) -> dict:
    """设备模型转字典"""
    # DB 存的是大写 ENUM 值（'SERVER_LINUX', 'OFFLINE'），API 响应用小写（'server', 'offline'）
    def _to_api_device_type(val):
        if not val:
            return 'other'
        v = str(val).lower()
        # 'server_linux' / 'server_windows' / 'server_vmware' → 'server'
        if v.startswith('server'):
            return 'server'
        if v.startswith('network'):
            return 'network'
        if v.startswith('storage'):
            return 'storage'
        if v.startswith('security'):
            return 'security'
        return v

    def _to_api_status(val):
        if not val:
            return 'offline'
        v = str(val).lower()
        if v in ('online', 'offline', 'warning', 'critical', 'maintenance', 'unknown'):
            return v
        return 'unknown'

    return {
        'id': device.id,
        'name': device.name,
        'hostname': device.hostname,
        'ip_address': device.ip_address,
        'device_type': _to_api_device_type(device.device_type),
        'status': _to_api_status(device.status),
        'os_type': device.os_type,
        'os_version': device.os_version,
        'manufacturer': device.manufacturer,
        'model': device.model,
        'serial_number': device.serial_number,
        'cpu': device.cpu,
        'memory': device.memory,
        'disk': device.disk,
        'network_interfaces': device.network_interfaces,
        'location': device.location,
        'idc': device.idc,
        'cabinet': device.cabinet,
        'business_id': device.business_id,
        'tags': device.tags,
        'created_at': device.created_at.isoformat() if device.created_at else None,
        'updated_at': device.updated_at.isoformat() if device.updated_at else None,
    }


async def _trigger_bg_collect(manager, device_name: str):
    """
    后台触发设备采集（不阻塞 API 响应）。
    采集完成后自动更新数据库状态，状态变更时会写日志。
    """
    try:
        metrics = await manager.collect_device(device_name)
        status = metrics.status.value if metrics and metrics.status else 'UNKNOWN'
        logger.info(f"[asset] 后台采集 {device_name} 完成，状态: {status}")
    except Exception as e:
        logger.warning(f"[asset] 后台采集 {device_name} 失败: {e}")


@router.get("/device", summary="获取设备列表")
async def get_devices(
    device_type: Optional[str] = Query(None, description="设备类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    idc: Optional[str] = Query(None, description="机房过滤"),
    business_id: Optional[int] = Query(None, description="业务系统ID过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    pagination: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db),
):
    """获取设备列表"""
    query = db.query(Device)
    
    # 应用过滤条件
    if device_type:
        db_device_type = _map_device_type(device_type)
        query = query.filter(Device.device_type == db_device_type)
    
    if status:
        db_status = _map_device_status(status)
        query = query.filter(Device.status == db_status)
    
    if idc:
        query = query.filter(Device.idc == idc)
    
    if business_id:
        query = query.filter(Device.business_id == business_id)
    
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Device.hostname.ilike(keyword_filter),
                Device.ip_address.ilike(keyword_filter),
                Device.manufacturer.ilike(keyword_filter),
                Device.model.ilike(keyword_filter),
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 分页
    devices = query.offset(pagination.offset).limit(pagination.limit).all()
    
    # 从DeviceManager获取实时状态
    from modules.collection.device_manager import get_device_manager
    manager = get_device_manager()

    # 转换设备列表，合并实时状态
    items = []
    for d in devices:
        device_dict = _device_to_dict(d)
        # hostname为空时fallback到name字段
        device_dict['hostname'] = device_dict['hostname'] or device_dict.get('name') or ''
        # 获取实时状态
        real_status = manager.get_device_status(d.name)
        last_metrics = manager.get_last_metrics(d.name)

        # 状态为 UNKNOWN 时，触发一次后台采集
        if str(real_status) == 'unknown' or str(real_status) == 'UNKNOWN':
            asyncio.create_task(_trigger_bg_collect(manager, d.name))

        device_dict['status'] = real_status.value if real_status else str(d.status)
        device_dict['last_collect_time'] = last_metrics.timestamp.isoformat() if last_metrics and last_metrics.timestamp else None
        # 从采集数据中获取更多字段（metrics为空时fallback到Device表字段）
        if last_metrics and last_metrics.metrics:
            m = last_metrics.metrics
            sys_info = m.get('system', {})
            cpu_info = m.get('cpu', {})
            mem_info = m.get('memory', {})
            network_info = m.get('network', []) or []
            disks_info = m.get('disks', []) or []
            hardware_info = m.get('hardware', {})
            containers_info = m.get('containers', {})
            packages_info = m.get('packages', {})

            device_dict['distro'] = m.get('distro') or ''
            device_dict['os_name'] = sys_info.get('os_name') or ''
            device_dict['kernel'] = sys_info.get('kernel') or ''
            device_dict['uptime'] = sys_info.get('uptime') or ''
            device_dict['cpu_model'] = cpu_info.get('model') or ''
            device_dict['cpu_cores'] = cpu_info.get('cores') or 0
            device_dict['cpu_usage'] = cpu_info.get('usage') or 0
            device_dict['cpu_load'] = cpu_info.get('load_avg_1m') or 0
            device_dict['memory_total_mb'] = mem_info.get('total_mb') or 0
            device_dict['memory_usage_percent'] = mem_info.get('usage_percent') or 0
            disk_usage = ''
            for disk in disks_info:
                if not isinstance(disk, dict):
                    continue
                if disk.get('mounted_on') == '/':
                    disk_usage = disk.get('usage_percent', '0%')
                    break
            device_dict['disk_usage'] = disk_usage
            # 主网络接口
            for iface in network_info:
                if not isinstance(iface, dict):
                    continue
                ip = iface.get('ip_address', '')
                if ip and ip not in ('N/A', '127.0.0.1', '::1'):
                    device_dict['primary_ip'] = ip
                    device_dict['primary_mac'] = iface.get('mac_address') or ''
                    break
            # 硬件/容器/包信息（完整对象供详情页使用）
            device_dict['hardware'] = hardware_info
            device_dict['containers'] = containers_info
            device_dict['packages'] = packages_info
            # 指纹信息
            device_dict['fingerprint_vendor'] = hardware_info.get('vendor') or last_metrics.vendor or ''
            device_dict['fingerprint_model'] = m.get('fingerprint_model') or ''
            device_dict['fingerprint_category'] = m.get('fingerprint_category') or ''
            device_dict['fingerprint_confidence'] = m.get('fingerprint_confidence') or 0.0
            device_dict['fingerprint_matched_by'] = m.get('fingerprint_matched_by') or []
            device_dict['fingerprint_suggested_protocols'] = m.get('fingerprint_suggested_protocols') or []
            device_dict['fingerprint_possible_creds'] = m.get('fingerprint_possible_creds') or []
            # 从metrics覆盖DB字段（os_type/manufacturer已在_device_to_dict中取DB值）
            if m.get('distro'):
                device_dict['os_type'] = m['distro'].capitalize()
            if hardware_info.get('vendor'):
                device_dict['manufacturer'] = hardware_info['vendor']
        else:
            # 无metrics时，使用Device表已有字段
            # 解析CPU字符串如 "Intel i7-13620H (10C/16T) @ 4.9GHz"
            cpu_str = d.cpu or ''
            cpu_model_str = ''
            cpu_cores_num = 0
            if cpu_str:
                import re
                # 提取核心数: 先尝试 "(NC/NT)" 格式
                cores_match = re.search(r'\((\d+)C/\d+T\)', cpu_str)
                if not cores_match:
                    cores_match = re.search(r'(\d+)\s*Cores?', cpu_str, re.I)
                if cores_match:
                    cpu_cores_num = int(cores_match.group(1))
                # 提取型号名（取括号前的主名称部分，去掉 @ 频率后缀）
                model_part = cpu_str.split('(')[0].strip()
                model_part = re.sub(r'\s*@\s*[\d.]+GHz\s*$', '', model_part, flags=re.I).strip()
                cpu_model_str = model_part
            device_dict['cpu_model'] = cpu_model_str
            device_dict['cpu_cores'] = cpu_cores_num
            # 解析内存字符串如 "64GB DDR5" → MB
            mem_mb = 0
            if d.memory:
                import re
                g = re.search(r'(\d+)\s*GB', d.memory, re.I)
                if g:
                    mem_mb = int(g.group(1)) * 1024
                else:
                    m = re.search(r'(\d+)\s*MB', d.memory, re.I)
                    if m:
                        mem_mb = int(m.group(1))
            device_dict['memory_total_mb'] = mem_mb
            device_dict['distro'] = d.os_type or ''
            device_dict['os_name'] = d.os_type or ''
            device_dict['manufacturer'] = d.manufacturer or ''
            device_dict['model'] = d.model or ''
            device_dict['cpu_usage'] = 0
            device_dict['cpu_load'] = 0
            device_dict['memory_usage_percent'] = 0
            device_dict['uptime'] = ''
            device_dict['kernel'] = ''
            device_dict['disk_usage'] = ''
            device_dict['primary_ip'] = d.ip_address
            device_dict['primary_mac'] = ''
            device_dict['hardware'] = {}
            device_dict['containers'] = {}
            device_dict['packages'] = {}
            device_dict['fingerprint_vendor'] = ''
            device_dict['fingerprint_model'] = ''
            device_dict['fingerprint_category'] = ''
            device_dict['fingerprint_confidence'] = 0.0
            device_dict['fingerprint_matched_by'] = []
            device_dict['fingerprint_suggested_protocols'] = []
            device_dict['fingerprint_possible_creds'] = []
        items.append(device_dict)
    
    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/device", summary="创建设备")
async def create_device(
    device: DeviceCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建设备记录"""
    db_device = Device(
        name=device.hostname,
        hostname=device.hostname,
        ip_address=device.ip_address,
        device_type=_map_device_type(device.device_type).value.upper(),  # 'server' → 'SERVER_LINUX'
        os_type=device.os_type,
        os_version=device.os_version,
        manufacturer=device.manufacturer,
        model=device.model,
        serial_number=device.serial_number,
        cpu=device.cpu,
        memory=device.memory,
        disk=device.disk,
        network_interfaces=device.network_interfaces,
        location=device.location,
        idc=device.idc,
        cabinet=device.cabinet,
        business_id=device.business_id,
        tags=device.tags,
        status=_map_device_status(device.status).value.upper() if device.status else 'OFFLINE',  # 'offline' → 'OFFLINE'
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return _device_to_dict(db_device)


@router.get("/device/{device_id}", summary="获取设备详情")
async def get_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    """获取设备的详细信息"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    device_dict = _device_to_dict(device)
    
    # 获取实时状态和指标
    from modules.collection.device_manager import get_device_manager
    manager = get_device_manager()
    real_status = manager.get_device_status(device.name)
    last_metrics = manager.get_last_metrics(device.name)
    device_dict['status'] = str(real_status) if real_status else str(device.status)
    device_dict['last_collect_time'] = last_metrics.timestamp.isoformat() if last_metrics and last_metrics.timestamp else None
    
    # 从采集数据中获取更多字段
    if last_metrics and last_metrics.metrics:
        m = last_metrics.metrics
        device_dict['os_type'] = m.get('os_type') or device.os_type
        device_dict['manufacturer'] = m.get('manufacturer') or device.manufacturer
        # 扩展字段
        device_dict['distro'] = m.get('distro')
        device_dict['os_name'] = m.get('os_name')
        device_dict['kernel'] = m.get('kernel')
        device_dict['uptime'] = m.get('uptime')
        device_dict['cpu_model'] = m.get('cpu_model')
        device_dict['cpu_cores'] = m.get('cpu_cores')
        device_dict['cpu_usage'] = m.get('cpu_usage')
        device_dict['cpu_load'] = m.get('cpu_load')
        device_dict['memory_total_mb'] = m.get('memory_total_mb')
        device_dict['memory_usage_percent'] = m.get('memory_usage_percent')
        device_dict['disk_usage'] = m.get('disk_usage')
        device_dict['primary_ip'] = m.get('primary_ip')
        device_dict['primary_mac'] = m.get('primary_mac')
        # 指纹信息
        device_dict['fingerprint_vendor'] = m.get('fingerprint_vendor') or last_metrics.vendor or ''
        device_dict['fingerprint_model'] = m.get('fingerprint_model') or ''
        device_dict['fingerprint_category'] = m.get('fingerprint_category') or ''
        device_dict['fingerprint_confidence'] = m.get('fingerprint_confidence') or 0.0
        device_dict['fingerprint_matched_by'] = m.get('fingerprint_matched_by') or []
        device_dict['fingerprint_suggested_protocols'] = m.get('fingerprint_suggested_protocols') or []
        device_dict['fingerprint_possible_creds'] = m.get('fingerprint_possible_creds') or []
    else:
        # 无metrics时的指纹默认值
        device_dict['fingerprint_vendor'] = ''
        device_dict['fingerprint_model'] = ''
        device_dict['fingerprint_category'] = ''
        device_dict['fingerprint_confidence'] = 0.0
        device_dict['fingerprint_matched_by'] = []
        device_dict['fingerprint_suggested_protocols'] = []
        device_dict['fingerprint_possible_creds'] = []

    return device_dict


@router.put("/device/{device_id}", summary="更新设备")
async def update_device(
    device_id: int,
    device: DeviceUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新设备信息"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新字段
    update_data = device.model_dump(exclude_unset=True)
    
    if 'device_type' in update_data:
        update_data['device_type'] = _map_device_type(update_data['device_type'])
    if 'status' in update_data:
        update_data['status'] = _map_device_status(update_data['status'])
    
    for key, value in update_data.items():
        setattr(db_device, key, value)
    
    db_device.updated_at = datetime.now()
    db.commit()
    db.refresh(db_device)
    
    return _device_to_dict(db_device)


@router.delete("/device/{device_id}", summary="删除设备")
async def delete_device(
    device_id: int,
    force: bool = Query(False, description="强制删除（高危操作）"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除设备（force=False 软删除[退役]；force=True 硬删除）"""
    db_device = db.query(Device).filter(Device.id == device_id).first()

    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")

    if force:
        # 硬删除：彻底删除设备及其关联数据
        db.delete(db_device)
        logger.warning(f"[HIGH-RISK] Force-deleted device {device_id} by {current_user.username}")
    else:
        # 软删除：设置为退役状态
        db_device.status = DBDeviceStatus.DECOMMISSIONED
        db_device.updated_at = datetime.now()
        logger.info(f"Decommissioned device {device_id} by {current_user.username}")

    db.commit()
    action = "force-deleted" if force else "decommissioned"
    return {"status": "success", "message": f"设备已{action}"}


@router.post("/device/{device_id}/maintain", summary="设置设备维护状态")
async def set_device_maintenance(
    device_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置设备为维护状态"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db_device.status = DBDeviceStatus.MAINTENANCE
    db_device.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "设备已进入维护模式"}


@router.post("/device/{device_id}/decommission", summary="退役设备")
async def decommission_device(
    device_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """退役设备"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db_device.status = DBDeviceStatus.DECOMMISSIONED
    db_device.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "设备已退役"}


# ============== 设备分组接口 ==============

@router.get("/group", summary="获取设备分组列表")
async def get_device_groups(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取设备分组列表"""
    groups = db.query(DeviceGroup).all()
    
    return {
        "items": [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "device_count": db.query(Device).filter(Device.group_id == g.id).count(),
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in groups
        ],
        "total": len(groups),
    }


@router.get("/group/{group_id}/devices", summary="获取分组下的设备列表")
async def get_group_devices(
    group_id: int,
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取分组下的设备列表"""
    query = db.query(Device).filter(Device.group_id == group_id)
    total = query.count()
    devices = query.offset(pagination.offset).limit(pagination.limit).all()
    
    return {
        "items": [_device_to_dict(d) for d in devices],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


# ============== 配置项接口 ==============

class ConfigItemCreate(BaseModel):
    """创建配置项"""
    key: str = Field(..., description="配置键")
    value: str = Field(..., description="配置值")
    category: str = Field(..., description="分类")
    device_id: Optional[int] = Field(None, description="关联设备")
    description: Optional[str] = Field(None, description="描述")


class ConfigSnapshotRequest(BaseModel):
    """创建设备配置快照请求"""
    device_id: int = Field(..., description="设备ID")
    description: Optional[str] = Field(None, description="快照描述")


@router.get("/config", summary="获取配置项列表")
async def get_config_items(
    category: Optional[str] = Query(None, description="分类过滤"),
    device_id: Optional[int] = Query(None, description="设备ID过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取配置项列表"""
    # 配置项存储在 Device 表的 extra_info JSON 字段中
    # 这里简化处理，返回空列表，实际应创建独立的配置项表
    return {
        "items": [],
        "total": 0,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/config/snapshot", summary="创建设备配置快照")
async def create_config_snapshot(
    request: ConfigSnapshotRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建设备配置快照 - 使用DeviceManager采集设备当前状态"""
    device = db.query(Device).filter(Device.id == request.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 使用DeviceManager采集当前配置
    from modules.collection.device_manager import DeviceManager

    try:
        manager = DeviceManager()
        result = await manager.collect_device(device.hostname or device.name)

        if result and result.status.value == 'online':
            return {
                "id": request.device_id,
                "device_id": request.device_id,
                "device_name": device.name,
                "key": f"config_snapshot_{device.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "value": json.dumps({
                    "hostname": result.hostname,
                    "os_type": result.os_type,
                    "os_version": result.os_version,
                    "uptime": result.uptime,
                    "metrics": result.metrics
                }, ensure_ascii=False),
                "description": request.description or f"{device.name} 配置快照",
                "created_at": datetime.now().isoformat(),
                "created_by": current_user.username,
            }
        else:
            raise HTTPException(status_code=500, detail=f"设备采集失败: {result.error if result else '未知错误'}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置采集异常: {str(e)}")


@router.put("/config/{config_id}", summary="更新配置项")
async def update_config_item(
    config_id: int,
    config: ConfigItemCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新配置项"""
    return {
        "id": config_id,
        "key": config.key,
        "value": config.value,
        "category": config.category,
        "updated_at": datetime.now().isoformat(),
    }


@router.delete("/config/{config_id}", summary="删除配置项")
async def delete_config_item(
    config_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除配置项"""
    return {"status": "success", "message": "配置项已删除"}


@router.post("/config/sync/{device_id}", summary="同步设备配置")
async def sync_device_config(
    device_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """同步设备配置 - 使用DeviceManager采集设备当前状态"""
    from modules.collection.device_manager import DeviceManager

    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    try:
        manager = DeviceManager()
        result = await manager.collect_device(device.hostname or device.name)

        if result and result.status.value == 'online':
            # 返回采集到的配置信息
            config_snapshot = {
                "status": "success",
                "device_id": device_id,
                "device_name": device.name,
                "synced_at": datetime.now().isoformat(),
                "config_data": {
                    "hostname": result.hostname,
                    "os_type": result.os_type,
                    "os_version": result.os_version,
                    "uptime": result.uptime,
                    "cpu": result.metrics.get('cpu', {}),
                    "memory": result.metrics.get('memory', {}),
                    "disks": result.metrics.get('disks', []),
                    "network": result.metrics.get('network', []),
                    "processes": result.metrics.get('processes', [])[:10],  # 只取前10个
                },
                "message": f"设备 {device.name} 配置同步成功"
            }
        else:
            config_snapshot = {
                "status": "error",
                "device_id": device_id,
                "device_name": device.name,
                "synced_at": datetime.now().isoformat(),
                "error": result.error if result else "采集失败",
                "message": f"设备 {device.name} 配置同步失败"
            }

        return config_snapshot

    except Exception as e:
        return {
            "status": "error",
            "device_id": device_id,
            "device_name": device.name,
            "synced_at": datetime.now().isoformat(),
            "error": str(e),
            "message": f"设备 {device.name} 配置同步异常"
        }


# ============== 业务系统接口 ==============

@router.get("/business", summary="获取业务系统列表")
async def get_business_systems(
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取业务系统列表"""
    query = db.query(BusinessSystem)
    total = query.count()
    systems = query.offset(pagination.offset).limit(pagination.limit).all()
    
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "code": s.code,
                "description": s.description,
                "status": s.status,
                "device_count": db.query(Device).filter(Device.business_id == s.id).count(),
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in systems
        ],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.get("/business/{business_id}", summary="获取业务系统详情")
async def get_business_system(
    business_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取业务系统详情"""
    system = db.query(BusinessSystem).filter(BusinessSystem.id == business_id).first()
    
    if not system:
        raise HTTPException(status_code=404, detail="业务系统不存在")
    
    return {
        "id": system.id,
        "name": system.name,
        "code": system.code,
        "description": system.description,
        "status": system.status,
        "created_at": system.created_at.isoformat() if system.created_at else None,
    }


@router.get("/business/{business_id}/devices", summary="获取业务系统关联的设备")
async def get_business_devices(
    business_id: int,
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取业务系统关联的设备"""
    query = db.query(Device).filter(Device.business_id == business_id)
    total = query.count()
    devices = query.offset(pagination.offset).limit(pagination.limit).all()
    
    return {
        "items": [_device_to_dict(d) for d in devices],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


# ============== 资产统计接口 ==============

@router.get("/stats", summary="获取资产统计")
async def get_asset_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取资产统计信息"""
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == DBDeviceStatus.ONLINE).count()
    offline_devices = db.query(Device).filter(Device.status == 'offline').count()
    maintenance_devices = db.query(Device).filter(Device.status == 'maintenance').count()
    
    # 按类型统计
    device_type_stats = {}
    for dtype in DBDeviceType:
        count = db.query(Device).filter(Device.device_type == dtype.value).count()
        if count > 0:
            device_type_stats[dtype.value] = count
    
    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "maintenance_devices": maintenance_devices,
        "by_type": device_type_stats,
        "by_status": {
            "online": online_devices,
            "offline": offline_devices,
            "maintenance": maintenance_devices,
        }
    }


class BatchDeviceRequest(BaseModel):
    ids: List[int] = Field(..., description="设备ID列表")
    action: str = Field(..., description="操作: delete, enable, disable")


@router.post("/device/batch", summary="批量操作设备")
async def batch_device(
    request: BatchDeviceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量删除/启用/禁用设备"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="设备ID列表不能为空")

    devices = db.query(Device).filter(Device.id.in_(request.ids)).all()
    if not devices:
        raise HTTPException(status_code=404, detail="未找到指定设备")

    results = []
    for device in devices:
        if request.action == "delete":
            device.is_deleted = True
            device.deleted_at = datetime.now()
        elif request.action == "enable":
            device.is_active = True
        elif request.action == "disable":
            device.is_active = False
        results.append(device.id)

    db.commit()
    return {
        "status": "success",
        "action": request.action,
        "affected": len(results),
        "ids": results
    }
