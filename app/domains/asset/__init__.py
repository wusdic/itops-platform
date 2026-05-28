"""
资产领域 (Asset Domain)

文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1
迁移脚本: scripts/migration/013_asset_center.sql
"""

# 导入所有模型，使其注册到 Base.metadata
from app.domains.asset.models import (
    Asset,
    AssetIP,
    AssetTag,
    AssetTagBinding,
    AssetGroup,
    AssetRelation,
    AssetCredentialBinding,
    AssetCollectionProfile,
    AssetLifecycleEvent,
)

# 导入 service 和 router（用于依赖注入）
from app.domains.asset.service import AssetService, AssetGroupService, AssetTagService, BusinessSystemService
from app.domains.asset.router import router as asset_router

__all__ = [
    "Asset",
    "AssetIP",
    "AssetTag",
    "AssetTagBinding",
    "AssetGroup",
    "AssetRelation",
    "AssetCredentialBinding",
    "AssetCollectionProfile",
    "AssetLifecycleEvent",
    "AssetService",
    "AssetGroupService",
    "AssetTagService",
    "BusinessSystemService",
    "asset_router",
]
