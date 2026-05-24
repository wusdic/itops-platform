# api/routes/deploy.py — 热升级/灰度发布 API
"""
金丝雀部署 + 滚动升级 + 版本管理

API 端点:
  GET    /api/v1/deploy/versions          # 列出所有版本
  POST   /api/v1/deploy/versions          # 注册新版本
  GET    /api/v1/deploy/versions/{name}   # 查看版本详情
  DELETE /api/v1/deploy/versions/{name}   # 删除版本记录

  POST   /api/v1/deploy/canary           # 创建金丝雀部署
  GET    /api/v1/deploy/canary            # 列出所有金丝雀
  GET    /api/v1/deploy/canary/{id}       # 查看金丝雀详情
  PUT    /api/v1/deploy/canary/{id}/weight # 调整流量权重
  POST   /api/v1/deploy/canary/{id}/promote # 升级为正式版本
  POST   /api/v1/deploy/canary/{id}/rollback # 回滚金丝雀
  DELETE /api/v1/deploy/canary/{id}      # 终止金丝雀

  GET    /api/v1/deploy/history           # 部署历史
  GET    /api/v1/deploy/health            # 各实例健康状态
"""

import uuid
import time
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from api.dependencies import get_current_user, require_role, CurrentUser

router = APIRouter(prefix="/api/v1/deploy", tags=["部署管理"])


# ─── 数据模型 ────────────────────────────────────────────────────────────────

class DeployStatus(str, Enum):
    CANARY = "canary"        # 金丝雀运行中
    PROMOTED = "promoted"    # 已升级为正式版本
    ROLLED_BACK = "rolled_back"  # 已回滚
    FAILED = "failed"        # 失败
    TERMINATED = "terminated"  # 手动终止


class InstanceHealth(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DeploymentVersion:
    name: str                # "v2.1.0"
    image: str               # "registry.example.com/itops:v2.1.0"
    changelog: str = ""
    created_by: str = ""
    created_at: float = field(default_factory=time.time)
    instances: int = 0
    status: str = "active"    # active / deprecated


@dataclass
class CanaryDeployment:
    id: str
    version: str              # 金丝雀版本名
    weight: int = 10          # 流量权重 %（0-100）
    status: DeployStatus = DeployStatus.CANARY
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    promoted_at: Optional[float] = None
    promoted_by: Optional[str] = None
    rollback_from: Optional[str] = None  # 从哪个正式版本回滚
    notes: str = ""


@dataclass
class DeployHistoryEntry:
    id: str
    action: str              # "deploy" / "promote" / "rollback" / "scale"
    version: str
    canary_id: Optional[str] = None
    performed_by: str = ""
    performed_at: float = field(default_factory=time.time)
    details: str = ""


@dataclass
class InstanceStatus:
    instance_id: str
    version: str
    health: InstanceHealth = InstanceHealth.UNKNOWN
    last_check: float = field(default_factory=time.time)
    uptime_seconds: float = 0


# ─── 内存存储（生产环境应持久化到 DB）────────────────────────────────────────

_versions: List[DeploymentVersion] = []
_canaries: List[CanaryDeployment] = []
_history: List[DeployHistoryEntry] = []
_instances: List[InstanceStatus] = []

# 当前正式版本（单一正式版本）
_current_version = "v1.0.0"


def _record(action: str, version: str, canary_id: Optional[str] = None,
            performed_by: str = "admin", details: str = ""):
    _history.insert(0, DeployHistoryEntry(
        id=str(uuid.uuid4())[:8],
        action=action,
        version=version,
        canary_id=canary_id,
        performed_by=performed_by,
        details=details,
    ))
    # 只保留最近 100 条
    if len(_history) > 100:
        _history[:] = _history[:100]


def _check_health(instance_id: str, version: str) -> InstanceHealth:
    """模拟健康检查——实际应调用 instance 的 /health 端点"""
    import random
    # 95% 概率 healthy
    r = random.random()
    if r < 0.95:
        return InstanceHealth.HEALTHY
    elif r < 0.98:
        return InstanceHealth.UNHEALTHY
    return InstanceHealth.UNKNOWN


# ─── Version API ─────────────────────────────────────────────────────────────

class VersionCreate(BaseModel):
    name: str = Field(..., description="版本号，如 v2.1.0")
    image: str = Field(..., description="镜像地址")
    changelog: str = ""
    created_by: str = "admin"
    instances: int = 1


class VersionResponse(BaseModel):
    name: str
    image: str
    changelog: str
    created_by: str
    created_at: float
    instances: int
    status: str


@router.get("/versions", response_model=List[VersionResponse])
def list_versions():
    """列出所有注册版本"""
    return [asdict(v) for v in _versions]


@router.post("/versions", response_model=VersionResponse)
def register_version(payload: VersionCreate):
    """注册一个新版本"""
    for v in _versions:
        if v.name == payload.name:
            raise HTTPException(400, f"版本 {payload.name} 已存在")
    ver = DeploymentVersion(
        name=payload.name,
        image=payload.image,
        changelog=payload.changelog,
        created_by=payload.created_by,
        instances=payload.instances,
    )
    _versions.append(ver)
    _record("register_version", payload.name, details=f"镜像: {payload.image}")
    return asdict(ver)


@router.get("/versions/{name}", response_model=VersionResponse)
def get_version(name: str):
    for v in _versions:
        if v.name == name:
            return asdict(v)
    raise HTTPException(404, f"版本 {name} 不存在")


@router.delete("/versions/{name}")
def delete_version(name: str):
    global _current_version
    if name == _current_version:
        raise HTTPException(400, "不能删除当前正式版本")
    for i, v in enumerate(_versions):
        if v.name == name:
            del _versions[i]
            _record("delete_version", name, details=f"删除版本记录")
            return {"message": "删除成功"}
    raise HTTPException(404, f"版本 {name} 不存在")


# ─── Canary API ──────────────────────────────────────────────────────────────

class CanaryCreate(BaseModel):
    version: str = Field(..., description="金丝雀版本号")
    weight: int = Field(10, ge=0, le=100, description="初始流量权重 %")
    notes: str = ""


class CanaryResponse(BaseModel):
    id: str
    version: str
    weight: int
    status: str
    created_at: float
    updated_at: float
    promoted_at: Optional[float]
    promoted_by: Optional[str]
    rollback_from: Optional[str]
    notes: str


@router.post("/canary", response_model=CanaryResponse)
def create_canary(payload: CanaryCreate, admin: CurrentUser = Depends(require_role("admin", "super_admin"))):
    """创建金丝雀部署（需要 super_admin）"""
    # 验证版本存在
    ver_exists = any(v.name == payload.version for v in _versions)
    if not ver_exists:
        raise HTTPException(404, f"版本 {payload.version} 未注册，请先 POST /deploy/versions")

    # 同一版本只能有一个活跃金丝雀
    for c in _canaries:
        if c.version == payload.version and c.status == DeployStatus.CANARY:
            raise HTTPException(400, f"版本 {payload.version} 已有活跃金丝雀 (id={c.id})")

    canary = CanaryDeployment(
        id=str(uuid.uuid4())[:8],
        version=payload.version,
        weight=payload.weight,
        notes=payload.notes,
    )
    _canaries.append(canary)
    _record("create_canary", payload.version, canary_id=canary.id,
            performed_by=admin.username, details=f"初始权重 {payload.weight}%")
    return asdict(canary)


@router.get("/canary", response_model=List[CanaryResponse])
def list_canaries():
    """列出所有金丝雀"""
    return [asdict(c) for c in _canaries]


@router.get("/canary/{canary_id}", response_model=CanaryResponse)
def get_canary(canary_id: str):
    for c in _canaries:
        if c.id == canary_id:
            return asdict(c)
    raise HTTPException(404, f"金丝雀 {canary_id} 不存在")


@router.put("/canary/{canary_id}/weight")
def update_canary_weight(canary_id: str, weight: int = Query(..., ge=0, le=100),
                        current_user: CurrentUser = Depends(require_role("admin", "super_admin"))):
    """调整金丝雀流量权重（实时生效）"""
    for c in _canaries:
        if c.id == canary_id:
            if c.status != DeployStatus.CANARY:
                raise HTTPException(400, f"金丝雀已 {c.status.value}，无法调整权重")
            old = c.weight
            c.weight = weight
            c.updated_at = time.time()
            _record("adjust_weight", c.version, canary_id=canary_id,
                    details=f"权重 {old}% → {weight}%")
            return {"message": "权重已更新", "weight": weight, "canary_id": canary_id}
    raise HTTPException(404, f"金丝雀 {canary_id} 不存在")


@router.post("/canary/{canary_id}/promote")
def promote_canary(canary_id: str, admin: CurrentUser = Depends(require_role("admin", "super_admin"))):
    """将金丝雀升级为正式版本（需要 super_admin）"""
    global _current_version
    for c in _canaries:
        if c.id == canary_id:
            if c.status != DeployStatus.CANARY:
                raise HTTPException(400, f"金丝雀已 {c.status.value}，无法升级")
            old_version = _current_version
            c.status = DeployStatus.PROMOTED
            c.promoted_at = time.time()
            c.promoted_by = admin.username
            _current_version = c.version
            _record("promote", c.version, canary_id=canary_id,
                    performed_by=admin.username,
                    details=f"升级 {old_version} → {c.version}")
            return {
                "message": f"已升级为正式版本 {c.version}",
                "previous_version": old_version,
                "current_version": _current_version,
            }
    raise HTTPException(404, f"金丝雀 {canary_id} 不存在")


@router.post("/canary/{canary_id}/rollback")
def rollback_canary(canary_id: str, admin: CurrentUser = Depends(require_role("admin", "super_admin"))):
    """回滚金丝雀到之前版本"""
    global _current_version
    for c in _canaries:
        if c.id == canary_id:
            if c.status not in (DeployStatus.CANARY, DeployStatus.PROMOTED):
                raise HTTPException(400, f"金丝雀已 {c.status.value}，无法回滚")
            rollback_target = c.rollback_from or _current_version
            c.status = DeployStatus.ROLLED_BACK
            c.updated_at = time.time()
            _record("rollback", rollback_target, canary_id=canary_id,
                    performed_by=admin.username, details=f"回滚到 {rollback_target}")
            return {"message": f"已回滚到 {rollback_target}"}
    raise HTTPException(404, f"金丝雀 {canary_id} 不存在")


@router.delete("/canary/{canary_id}")
def terminate_canary(canary_id: str, admin: CurrentUser = Depends(require_role("admin", "super_admin"))):
    """终止金丝雀"""
    for i, c in enumerate(_canaries):
        if c.id == canary_id:
            c.status = DeployStatus.TERMINATED
            c.updated_at = time.time()
            _record("terminate_canary", c.version, canary_id=canary_id,
                    performed_by=admin.username, details="手动终止")
            return {"message": "金丝雀已终止"}
    raise HTTPException(404, f"金丝雀 {canary_id} 不存在")


# ─── 历史 & 健康检查 ─────────────────────────────────────────────────────────

class HistoryEntry(BaseModel):
    id: str
    action: str
    version: str
    canary_id: Optional[str]
    performed_by: str
    performed_at: float
    details: str


@router.get("/history", response_model=List[HistoryEntry])
def deploy_history(limit: int = Query(20, ge=1, le=100)):
    """部署历史"""
    return [asdict(h) for h in _history[:limit]]


@router.get("/health")
def deploy_health():
    """各实例健康状态（模拟）"""
    global _instances
    now = time.time()

    # 模拟实例列表（实际应从服务发现/Nginx upstream 获取）
    demo_instances = [
        InstanceStatus("inst-001", _current_version),
        InstanceStatus("inst-002", _current_version),
    ]
    # 加入金丝雀实例
    for c in _canaries:
        if c.status == DeployStatus.CANARY:
            demo_instances.append(InstanceStatus(f"canary-{c.id}", c.version))

    for inst in demo_instances:
        inst.health = _check_health(inst.instance_id, inst.version)
        inst.last_check = now

    _instances = demo_instances

    return {
        "current_version": _current_version,
        "instances": [asdict(i) for i in _instances],
        "healthy_count": sum(1 for i in _instances if i.health == InstanceHealth.HEALTHY),
        "total_count": len(_instances),
        "checked_at": now,
    }


@router.get("/status")
def deploy_status():
    """部署总览"""
    canary_list = [asdict(c) for c in _canaries if c.status == DeployStatus.CANARY]
    return {
        "current_version": _current_version,
        "registered_versions": len(_versions),
        "active_canaries": len(canary_list),
        "canaries": canary_list,
    }
