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


def add_vendor(vendor_data: Dict, operator: str = None) -> Dict:
    """新增厂商（变更前自动创建版本快照）"""
    # 先保存当前状态为新版本
    _create_version_snapshot(
        description=f"Auto-backup before adding vendor '{vendor_data.get('name')}'",
        operator=operator,
    )
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


def update_vendor(name: str, vendor_data: Dict, operator: str = None) -> Optional[Dict]:
    """更新厂商信息（变更前自动创建版本快照）"""
    # 先保存当前状态为新版本
    _create_version_snapshot(
        description=f"Auto-backup before updating vendor '{name}'",
        operator=operator,
    )
    data = _load_vendor_credentials()
    vendors = data.get("vendors", [])
    for i, v in enumerate(vendors):
        if v.get("name") == name:
            vendors[i] = vendor_data
            data["vendors"] = vendors
            _save_vendor_credentials(data)
            return vendor_data
    return None


def delete_vendor(name: str, operator: str = None) -> bool:
    """删除厂商（变更前自动创建版本快照）"""
    # 先保存当前状态为新版本
    _create_version_snapshot(
        description=f"Auto-backup before deleting vendor '{name}'",
        operator=operator,
    )
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


# =============================================================================
# 版本管理 - P0-6 设备指纹模板版本管理
# =============================================================================

def _create_version_snapshot(description: str, operator: str = None) -> Dict:
    """
    创建当前模板的版本快照并保存到数据库
    在 add_vendor / update_vendor / delete_vendor 之前调用
    """
    import json
    from datetime import datetime
    from modules.foundation.db_models.base import init_db
    from modules.foundation.db_models.fingerprint_template_version import FingerprintTemplateVersion

    # 获取当前模板内容
    current = _load_vendor_credentials()

    db = init_db()
    with db.session_scope() as session:
        # 生成版本号: v{timestamp}
        version = f"v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        snapshot = FingerprintTemplateVersion(
            version=version,
            description=description,
            content=json.dumps(current, ensure_ascii=False),
            operator=operator,
        )
        session.add(snapshot)
        session.flush()

        return {
            "id": snapshot.id,
            "version": snapshot.version,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        }


def list_versions(limit: int = 20, offset: int = 0) -> Dict:
    """列出所有版本（倒序，最新在前）"""
    from modules.foundation.db_models.base import init_db
    from modules.foundation.db_models.fingerprint_template_version import FingerprintTemplateVersion

    db = init_db()
    with db.session_scope() as session:
        total = session.query(FingerprintTemplateVersion).count()
        versions = (
            session.query(FingerprintTemplateVersion)
            .order_by(FingerprintTemplateVersion.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        items = [
            {
                "id": v.id,
                "version": v.version,
                "description": v.description,
                "operator": v.operator,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in versions
        ]
        return {"items": items, "total": total}


def get_version(version: str) -> Optional[Dict]:
    """获取指定版本的内容"""
    import json
    from modules.foundation.db_models.base import init_db
    from modules.foundation.db_models.fingerprint_template_version import FingerprintTemplateVersion

    db = init_db()
    with db.session_scope() as session:
        v = session.query(FingerprintTemplateVersion).filter_by(version=version).first()
        if not v:
            return None
        return {
            "id": v.id,
            "version": v.version,
            "description": v.description,
            "content": json.loads(v.content),
            "operator": v.operator,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }


def rollback_version(version: str, operator: str = None) -> bool:
    """
    回滚到指定版本
    回滚前会先保存当前状态为新版本（防止回滚后无法恢复）
    """
    import json
    from modules.foundation.db_models.base import init_db
    from modules.foundation.db_models.fingerprint_template_version import FingerprintTemplateVersion

    # 先获取目标版本内容
    target = get_version(version)
    if not target:
        raise ValueError(f"Version '{version}' not found")

    # 保存当前状态为新版本（备份）
    _create_version_snapshot(
        description=f"Auto-backup before rollback to {version}",
        operator=operator,
    )

    # 恢复目标版本内容到 YAML 文件
    db = init_db()
    with db.session_scope() as session:
        v = session.query(FingerprintTemplateVersion).filter_by(version=version).first()
        content = json.loads(v.content)
        _save_vendor_credentials(content)

    # 清除缓存，强制重新加载
    global _vendor_db
    _vendor_db = None

    return True


def create_version(description: str, operator: str = None) -> Dict:
    """
    手动创建版本快照（不修改模板，仅记录当前状态）
    """
    return _create_version_snapshot(description=description, operator=operator)
