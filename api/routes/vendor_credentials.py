# -*- coding: utf-8 -*-
"""
厂商账密管理 API
提供厂商账密配置的查看和运维接口
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# 尝试导入配置加载模块
try:
    from modules.collection.fingerprint.vendor_credential_config import (
        get_all_vendors,
        get_vendor_by_name,
        get_vendor_by_pattern,
        get_vendor_by_oid,
        get_vendor_by_mac_oui,
        get_common_credentials,
        get_all_categories,
        get_vendors_by_category,
        add_vendor,
        update_vendor,
        delete_vendor,
    )
    _config_available = True
except ImportError as e:
    _config_available = False

router = APIRouter(tags=["厂商账密管理"])


# =============================================================================
# Pydantic 模型
# =============================================================================

class FingerprintRule(BaseModel):
    pattern: Optional[str] = None
    type: str  # ssh_banner, http_header, snmp_sysObjectID, snmp_sysDesc
    weight: float = 0.5
    oid_prefix: Optional[str] = None


class CredentialItem(BaseModel):
    protocol: str
    username: Optional[str] = None
    password: Optional[str] = None
    password_hash: Optional[str] = None
    community: Optional[str] = None
    notes: Optional[str] = None
    priority: int = 99


class VendorIn(BaseModel):
    name: str
    short_name: str
    category: str
    homepage: Optional[str] = ""
    description: Optional[str] = ""
    fingerprints: List[FingerprintRule] = []
    default_credentials: List[CredentialItem] = []
    suggested_protocols: List[str] = []
    probe_ports: List[int] = []


class VendorOut(BaseModel):
    name: str
    short_name: str
    category: str
    homepage: str
    description: str
    fingerprints: List[FingerprintRule]
    default_credentials: List[CredentialItem]
    suggested_protocols: List[str]
    probe_ports: List[int]


class VendorListItem(BaseModel):
    name: str
    short_name: str
    category: str
    homepage: str
    description: str
    credential_count: int
    fingerprint_count: int


# =============================================================================
# 辅助函数
# =============================================================================

def _vendor_to_out(v: Dict) -> VendorOut:
    """将厂商字典转为 VendorOut 模型"""
    return VendorOut(
        name=v.get("name", ""),
        short_name=v.get("short_name", ""),
        category=v.get("category", ""),
        homepage=v.get("homepage", ""),
        description=v.get("description", ""),
        fingerprints=[FingerprintRule(**fp) for fp in v.get("fingerprints", [])],
        default_credentials=[CredentialItem(**c) for c in v.get("default_credentials", [])],
        suggested_protocols=v.get("suggested_protocols", []),
        probe_ports=v.get("probe_ports", []),
    )


def _vendor_to_list_item(v: Dict) -> VendorListItem:
    """将厂商字典转为列表项"""
    return VendorListItem(
        name=v.get("name", ""),
        short_name=v.get("short_name", ""),
        category=v.get("category", ""),
        homepage=v.get("homepage", ""),
        description=v.get("description", ""),
        credential_count=len(v.get("default_credentials", [])),
        fingerprint_count=len(v.get("fingerprints", [])),
    )


# =============================================================================
# API 路由
# =============================================================================

@router.get("/vendors", summary="获取所有厂商列表")
async def list_vendors(
    category: Optional[str] = Query(None, description="按分类筛选"),
    search: Optional[str] = Query(None, description="搜索厂商名"),
):
    """获取所有厂商列表，支持分类筛选和搜索"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    if category:
        vendors = get_vendors_by_category(category)
    else:
        vendors = get_all_vendors()

    if search:
        search_lower = search.lower()
        vendors = [v for v in vendors if search_lower in v.get("name", "").lower()]

    return {
        "total": len(vendors),
        "items": [_vendor_to_list_item(v) for v in vendors],
    }


@router.get("/vendors/categories", summary="获取所有分类")
async def list_categories():
    """获取所有设备分类列表"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")
    return {"categories": get_all_categories()}


@router.get("/vendors/common-creds", summary="获取通用默认账密")
async def list_common_credentials():
    """获取通用默认账密列表（不区分厂商）"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")
    return {"items": get_common_credentials()}


@router.get("/vendors/{vendor_name}", summary="获取厂商详情")
async def get_vendor(vendor_name: str):
    """获取某个厂商的完整信息"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    vendor = get_vendor_by_name(vendor_name)
    if not vendor:
        raise HTTPException(status_code=404, detail=f"厂商 '{vendor_name}' 不存在")
    return _vendor_to_out(vendor)


@router.post("/vendors", summary="新增厂商")
async def create_vendor(vendor: VendorIn):
    """新增一个厂商的账密配置"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    try:
        vendor_dict = vendor.model_dump()
        add_vendor(vendor_dict)
        return {"message": f"厂商 '{vendor.name}' 创建成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/vendors/{vendor_name}", summary="更新厂商")
async def modify_vendor(vendor_name: str, vendor: VendorIn):
    """更新某个厂商的账密配置"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    result = update_vendor(vendor_name, vendor.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail=f"厂商 '{vendor_name}' 不存在")
    return {"message": f"厂商 '{vendor_name}' 更新成功"}


@router.delete("/vendors/{vendor_name}", summary="删除厂商")
async def remove_vendor(vendor_name: str):
    """删除某个厂商的账密配置"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    if not delete_vendor(vendor_name):
        raise HTTPException(status_code=404, detail=f"厂商 '{vendor_name}' 不存在")
    return {"message": f"厂商 '{vendor_name}' 删除成功"}


@router.get("/probe/banner", summary="根据 banner 匹配厂商")
async def probe_by_banner(banner: str = Query(..., description="SSH/HTTP banner")):
    """根据 banner 内容自动匹配厂商和默认账密"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    result = get_vendor_by_pattern(banner)
    if not result:
        return {"matched": False, "message": "未匹配到已知厂商"}
    return {"matched": True, "vendor": result}


@router.get("/probe/oid", summary="根据 OID 匹配厂商")
async def probe_by_oid(oid: str = Query(..., description="SNMP sysObjectID")):
    """根据 SNMP OID 前缀匹配厂商"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    result = get_vendor_by_oid(oid)
    if not result:
        return {"matched": False, "message": "未匹配到已知厂商"}
    return {"matched": True, "vendor": result}


@router.get("/probe/mac", summary="根据 MAC OUI 匹配厂商")
async def probe_by_mac(oui: str = Query(..., description="MAC 地址前6位 OUI")):
    """根据 MAC OUI 匹配厂商"""
    if not _config_available:
        raise HTTPException(status_code=503, detail="配置模块不可用")

    result = get_vendor_by_mac_oui(oui)
    if not result:
        return {"matched": False, "message": "未匹配到已知 OUI"}
    return {"matched": True, "vendor": result}
