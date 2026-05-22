# -*- coding: utf-8 -*-
"""
厂商账密配置管理 - 从 YAML 配置文件加载
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
VENDOR_CREDENTIALS_FILE = CONFIG_DIR / "devices" / "vendor_credentials.yaml"

# 全局缓存
_vendor_db: Optional[Dict] = None


def _load_vendor_credentials() -> Dict:
    """加载厂商账密配置"""
    global _vendor_db
    if _vendor_db is not None:
        return _vendor_db

    if not VENDOR_CREDENTIALS_FILE.exists():
        logger.warning(f"Vendor credentials file not found: {VENDOR_CREDENTIALS_FILE}")
        _vendor_db = {"vendors": [], "common_default_credentials": [], "mac_oui_database": {}}
        return _vendor_db

    try:
        with open(VENDOR_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        _vendor_db = data
        logger.info(f"Loaded vendor credentials: {len(data.get('vendors', []))} vendors")
        return data
    except Exception as e:
        logger.error(f"Failed to load vendor credentials: {e}")
        _vendor_db = {"vendors": [], "common_default_credentials": [], "mac_oui_database": {}}
        return _vendor_db


def get_all_vendors() -> List[Dict]:
    """获取所有厂商列表"""
    data = _load_vendor_credentials()
    return data.get("vendors", [])


def get_vendor_by_name(name: str) -> Optional[Dict]:
    """根据厂商名获取详情"""
    vendors = get_all_vendors()
    for v in vendors:
        if v.get("name") == name:
            return v
    return None


def get_vendor_by_pattern(banner: str) -> Optional[Dict]:
    """根据 banner 内容匹配厂商"""
    vendors = get_all_vendors()
    banner_lower = banner.lower()
    for v in vendors:
        for fp in v.get("fingerprints", []):
            if fp.get("type") in ("ssh_banner", "http_header"):
                pattern = fp.get("pattern", "")
                try:
                    if re.search(pattern, banner_lower, re.IGNORECASE):
                        return {
                            "name": v.get("name"),
                            "short_name": v.get("short_name"),
                            "category": v.get("category"),
                            "matched_by": fp.get("pattern"),
                            "confidence": fp.get("weight", 0.5),
                            "fingerprints": v.get("fingerprints", []),
                            "default_credentials": v.get("default_credentials", []),
                            "suggested_protocols": v.get("suggested_protocols", []),
                            "probe_ports": v.get("probe_ports", []),
                        }
                except re.error:
                    continue
    return None


def get_vendor_by_oid(oid_prefix: str) -> Optional[Dict]:
    """根据 SNMP OID 前缀匹配厂商"""
    vendors = get_all_vendors()
    for v in vendors:
        for fp in v.get("fingerprints", []):
            if fp.get("type") == "snmp_sysObjectID":
                prefix = fp.get("oid_prefix", "")
                if oid_prefix.startswith(prefix) or prefix.startswith(oid_prefix):
                    return {
                        "name": v.get("name"),
                        "short_name": v.get("short_name"),
                        "category": v.get("category"),
                        "matched_by": f"OID: {prefix}",
                        "confidence": fp.get("weight", 0.5),
                        "default_credentials": v.get("default_credentials", []),
                        "suggested_protocols": v.get("suggested_protocols", []),
                        "probe_ports": v.get("probe_ports", []),
                    }
    return None


def get_vendor_by_mac_oui(oui: str) -> Optional[Dict]:
    """根据 MAC OUI 查找厂商"""
    data = _load_vendor_credentials()
    mac_db = data.get("mac_oui_database", {})
    if oui.upper() in mac_db:
        entry = mac_db[oui.upper()]
        vendor_name = entry.get("vendor") if isinstance(entry, dict) else entry
        return {
            "name": vendor_name,
            "category": entry.get("category") if isinstance(entry, dict) else None,
        }
    return None


def get_common_credentials() -> List[Dict]:
    """获取通用默认账密"""
    data = _load_vendor_credentials()
    return data.get("common_default_credentials", [])


def get_all_categories() -> List[str]:
    """获取所有设备分类"""
    vendors = get_all_vendors()
    categories = set()
    for v in vendors:
        if v.get("category"):
            categories.add(v.get("category"))
    return sorted(list(categories))


def get_vendors_by_category(category: str) -> List[Dict]:
    """按分类获取厂商"""
    vendors = get_all_vendors()
    return [v for v in vendors if v.get("category") == category]


def add_vendor(vendor_data: Dict) -> Dict:
    """新增厂商"""
    data = _load_vendor_credentials()
    vendors = data.get("vendors", [])
    # 检查是否已存在
    for v in vendors:
        if v.get("name") == vendor_data.get("name"):
            raise ValueError(f"Vendor '{vendor_data['name']}' already exists")
    vendors.append(vendor_data)
    data["vendors"] = vendors
    _save_vendor_credentials(data)
    return vendor_data


def update_vendor(name: str, vendor_data: Dict) -> Optional[Dict]:
    """更新厂商信息"""
    data = _load_vendor_credentials()
    vendors = data.get("vendors", [])
    for i, v in enumerate(vendors):
        if v.get("name") == name:
            vendors[i] = vendor_data
            data["vendors"] = vendors
            _save_vendor_credentials(data)
            return vendor_data
    return None


def delete_vendor(name: str) -> bool:
    """删除厂商"""
    data = _load_vendor_credentials()
    vendors = data.get("vendors", [])
    original_count = len(vendors)
    vendors = [v for v in vendors if v.get("name") != name]
    if len(vendors) < original_count:
        data["vendors"] = vendors
        _save_vendor_credentials(data)
        return True
    return False


def _save_vendor_credentials(data: Dict) -> None:
    """保存配置到文件（仅本地，不影响容器内运行）"""
    global _vendor_db
    try:
        # 确保目录存在
        VENDOR_CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(VENDOR_CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        _vendor_db = data
        logger.info(f"Saved vendor credentials to {VENDOR_CREDENTIALS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save vendor credentials: {e}")
        raise
