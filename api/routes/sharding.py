# -*- coding: utf-8 -*-
"""
P2-24 数据库分表 API

提供分片路由和生命周期管理接口：
  GET  /sharding/routes/{logical_table}     — 获取某表的物理分片列表
  POST /sharding/routes/{logical_table}/create  — 为指定租户/月创建分片
  GET  /sharding/stats                      — 各表分片统计
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from api.dependencies import get_current_user, get_db, CurrentUser
from modules.foundation.sharding import (
    get_physical_table,
    list_shards,
    MONTHLY_SHARDED,
    TENANT_SHARDED,
    UNSHARDED,
    ShardManager,
)
from sqlalchemy import text

router = APIRouter(prefix="/sharding", tags=["分片管理"])


def _get_executor(db):
    """将 SQLAlchemy session 转换为 ShardManager 需要的回调格式

    exec-sql 返回 {"code":0,"results":[...]}，其中 results 是 list of dict
    这里直接返回 results（list）供 ShardManager 使用。
    """
    def exec_sql(sql: str):
        try:
            from sqlalchemy import text
            result = db.execute(text(sql))
            if result.returns_rows:
                rows = [dict(row._mapping) for row in result]
                return rows  # 直接返回 list of dict
            db.commit()
            return result.rowcount
        except Exception:
            db.rollback()
            raise
    return exec_sql


class ShardRouteResponse(BaseModel):
    logical: str
    physical: str
    strategy: str  # "monthly" | "tenant" | "unsharded"


class CreateShardRequest(BaseModel):
    tenant_id: Optional[str] = None  # 租户分片时使用
    dt: Optional[str] = None          # 月分片时使用，格式 "YYYY-MM" 或 "YYYY-MM-DD"


class CreateShardResponse(BaseModel):
    logical: str
    physical: str
    created: bool


class ShardStatsItem(BaseModel):
    logical: str
    strategy: str
    shard_count: int
    sample_shards: List[str]


@router.get("/routes/{logical_table}", response_model=ShardRouteResponse)
def get_shard_route(
    logical_table: str,
    tenant_id: Optional[str] = Query(None, description="租户ID（租户分片时）"),
    dt: Optional[str] = Query(None, description="日期（YYYY-MM格式，月分片时）"),
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    查询某逻辑表在当前上下文下对应的物理分片表名。
    """
    if logical_table in UNSHARDED:
        return ShardRouteResponse(
            logical=logical_table,
            physical=logical_table,
            strategy="unsharded",
        )

    parsed_dt = None
    if dt:
        try:
            if "-" in dt:
                parts = dt.split("-")
                parsed_dt = datetime(int(parts[0]), int(parts[1]), 1)
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail=f"日期格式错误，请使用 YYYY-MM 格式")

    physical = get_physical_table(logical_table, tenant_id=tenant_id, dt=parsed_dt)

    if logical_table in MONTHLY_SHARDED:
        return ShardRouteResponse(logical=logical_table, physical=physical, strategy="monthly")
    if logical_table in TENANT_SHARDED:
        return ShardRouteResponse(logical=logical_table, physical=physical, strategy="tenant")

    return ShardRouteResponse(logical=logical_table, physical=physical, strategy="unsharded")


@router.post("/routes/{logical_table}/create", response_model=CreateShardResponse)
def create_shard(
    logical_table: str,
    req: CreateShardRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    手动触发创建某个逻辑表的分片表。
    """
    if logical_table in UNSHARDED:
        raise HTTPException(status_code=400, detail="该表不分片")

    if logical_table not in MONTHLY_SHARDED and logical_table not in TENANT_SHARDED:
        raise HTTPException(status_code=400, detail="未知分片策略")

    parsed_dt = None
    if req.dt:
        try:
            parts = req.dt.split("-")
            parsed_dt = datetime(int(parts[0]), int(parts[1]), 1)
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM")

    manager = ShardManager(_get_executor(db))

    try:
        physical = manager.ensure_shard_exists(logical_table, tenant_id=req.tenant_id, dt=parsed_dt)
        return CreateShardResponse(logical=logical_table, physical=physical, created=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建分片失败: {str(e)}")


@router.get("/stats", response_model=List[ShardStatsItem])
def get_shard_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    获取各分片表的统计信息（已创建的分片数量）。
    """
    manager = ShardManager(_get_executor(db))
    result: List[ShardStatsItem] = []

    all_s = dict(**MONTHLY_SHARDED, **TENANT_SHARDED)

    for logical, strategy in all_s.items():
        try:
            existing = manager.list_existing_shards(logical)
            result.append(ShardStatsItem(
                logical=logical,
                strategy=strategy,
                shard_count=len(existing),
                sample_shards=existing[:5],  # 最多返回5个示例
            ))
        except Exception:
            result.append(ShardStatsItem(
                logical=logical,
                strategy=strategy,
                shard_count=0,
                sample_shards=[],
            ))

    return result
