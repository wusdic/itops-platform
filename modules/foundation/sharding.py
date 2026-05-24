# -*- coding: utf-8 -*-
"""
数据库分表路由层 — P2-24 水平扩展基础设施

分片策略：
  - 时序表（performance_metrics, alerts）按月分片 → performance_metrics_202506
  - 业务表（work_orders, devices）按租户分片 → work_orders_t202605239779
  - 默认查询路由到主表（未分片数据），跨分片查询使用合并结果

路由规则：
  - get_table_name("performance_metrics", tenant_id="t1", dt=2025-06) → "performance_metrics_202506"
  - get_table_name("work_orders", tenant_id="t202605239779") → "work_orders_t202605239779"
  - get_table_name("work_orders", tenant_id=None) → "work_orders"
"""

from __future__ import annotations

import re
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable
from functools import lru_cache


# ──────────────────────────────────────────────────────────────────────────────
# 分片规则定义
# ──────────────────────────────────────────────────────────────────────────────

class ShardStrategy:
    """分片策略基类"""

    def get_physical_table(self, logical_name: str, **kwargs) -> str:
        raise NotImplementedError

    def list_shards(self, logical_name: str, **kwargs) -> List[str]:
        raise NotImplementedError


class MonthlyShard(ShardStrategy):
    """
    按月分片策略
    适用于：performance_metrics, alerts
    格式：{logical}_YYYYMM
    """

    def get_physical_table(self, logical_name: str, dt: Optional[datetime] = None, **kwargs) -> str:
        if dt is None:
            dt = datetime.now()
        suffix = dt.strftime("%Y%m")
        return f"{logical_name}_{suffix}"

    def list_shards(self, logical_name: str, from_dt: Optional[datetime] = None,
                    to_dt: Optional[datetime] = None) -> List[str]:
        if from_dt is None:
            from_dt = datetime(2024, 1, 1)
        if to_dt is None:
            to_dt = datetime.now()
        shards = []
        cur = from_dt
        while cur <= to_dt:
            shards.append(f"{logical_name}_{cur.strftime('%Y%m')}")
            # 前进到下月
            if cur.month == 12:
                cur = cur.replace(year=cur.year + 1, month=1)
            else:
                cur = cur.replace(month=cur.month + 1)
        return shards


class TenantShard(ShardStrategy):
    """
    按租户分片策略
    适用于：work_orders, devices
    格式：{logical}_{tenant_id}
    """

    # 租户ID黑名单（不允许作为表名后缀的特殊字符）
    _FORBIDDEN = re.compile(r"[^\w]")

    def get_physical_table(self, logical_name: str, tenant_id: Optional[str] = None, **kwargs) -> str:
        if not tenant_id:
            return logical_name  # 无租户ID → 主表
        safe_id = self._FORBIDDEN.sub("", tenant_id)
        return f"{logical_name}_{safe_id}"

    def list_shards(self, logical_name: str, tenant_ids: Optional[List[str]] = None) -> List[str]:
        if not tenant_ids:
            return [logical_name]
        return [self.get_physical_table(logical_name, tid) for tid in tenant_ids]


# ──────────────────────────────────────────────────────────────────────────────
# 分片配置表
# ──────────────────────────────────────────────────────────────────────────────

# 时序分片表（按月）
MONTHLY_SHARDED: Dict[str, str] = {
    "performance_metrics": "time_series",
    "alerts": "time_series",
    "audit_logs": "time_series",
}

# 租户分片表（按租户）
TENANT_SHARDED: Dict[str, str] = {
    "work_orders": "tenant",
    "devices": "tenant",
    "automation_scripts": "tenant",
}

# 始终在主表（不分片）
UNSHARDED: set = {
    "tenants",
    "system_users",
    "departments",
    "roles",
    "api_keys",
}


def _make_strategies() -> Dict[str, ShardStrategy]:
    return {
        "time_series": MonthlyShard(),
        "tenant": TenantShard(),
    }


_STRATEGIES = _make_strategies()


# ──────────────────────────────────────────────────────────────────────────────
# 核心路由函数
# ──────────────────────────────────────────────────────────────────────────────

def get_physical_table(
    logical_name: str,
    tenant_id: Optional[str] = None,
    dt: Optional[datetime] = None,
) -> str:
    """
    根据逻辑表名和分片键，返回物理表名。

    Args:
        logical_name: 逻辑表名（如 "performance_metrics"）
        tenant_id: 租户ID（用于租户分片）
        dt: 日期时间（用于月分片，自动取年月）

    Returns:
        物理表名（如 "performance_metrics_202506" 或 "work_orders_t202605239779"）

    Examples:
        >>> get_physical_table("performance_metrics", dt=datetime(2025,6,15))
        'performance_metrics_202506'
        >>> get_physical_table("work_orders", tenant_id="t202605239779")
        'work_orders_t202605239779'
        >>> get_physical_table("tenants")
        'tenants'
    """
    if logical_name in UNSHARDED:
        return logical_name
    if logical_name in MONTHLY_SHARDED:
        strat_name = MONTHLY_SHARDED[logical_name]
        return _STRATEGIES[strat_name].get_physical_table(logical_name, dt=dt)
    if logical_name in TENANT_SHARDED:
        strat_name = TENANT_SHARDED[logical_name]
        return _STRATEGIES[strat_name].get_physical_table(logical_name, tenant_id=tenant_id)
    return logical_name  # 未知表名 → 不分片


def list_shards(
    logical_name: str,
    tenant_ids: Optional[List[str]] = None,
    from_dt: Optional[datetime] = None,
    to_dt: Optional[datetime] = None,
) -> List[str]:
    """
    列出某逻辑表的所有物理分片（用于跨分片查询）。

    Args:
        logical_name: 逻辑表名
        tenant_ids: 租户列表（仅租户分片）
        from_dt/to_dt: 时间范围（仅月分片）

    Returns:
        物理表名列表
    """
    if logical_name in MONTHLY_SHARDED:
        strat_name = MONTHLY_SHARDED[logical_name]
        return _STRATEGIES[strat_name].list_shards(logical_name, from_dt=from_dt, to_dt=to_dt)
    if logical_name in TENANT_SHARDED:
        strat_name = TENANT_SHARDED[logical_name]
        return _STRATEGIES[strat_name].list_shards(logical_name, tenant_ids=tenant_ids)
    return [logical_name]


def create_sharded_tables_sql(logical_name: str, shard_name: str) -> str:
    """
    生成创建分片的 DDL（基于主表结构 + 新表名）。
    这是一个模板，实际创建需要通过 show create table 获取主表DDL后替换表名。
    """
    return f"-- 分片表 {shard_name} 应从主表 {logical_name} 结构复制\n-- 请手动执行：\n-- CREATE TABLE {shard_name} LIKE {logical_name};"


# ──────────────────────────────────────────────────────────────────────────────
# SQL 改写器（核心路由逻辑）
# ──────────────────────────────────────────────────────────────────────────────

def rewrite_query(
    sql: str,
    tenant_id: Optional[str] = None,
    dt: Optional[datetime] = None,
) -> str:
    """
    将包含逻辑表名的 SQL 改写为物理表名。
    只改写 FROM 和 JOIN 子句中的表名，不改写子查询中的表名。

    ⚠️ 注意：这是一个基础版本，仅处理简单场景。
    完整实现需要解析 SQL AST 或使用 ShardingSphere 等中间件。

    Args:
        sql: 原始 SQL（应包含逻辑表名）
        tenant_id: 当前租户ID
        dt: 当前时间（用于月分片）

    Returns:
        改写后的 SQL

    Examples:
        >>> rewrite_query("SELECT * FROM performance_metrics WHERE created_at > '2025-06-01'",
        ...               dt=datetime(2025,6,15))
        "SELECT * FROM performance_metrics_202506 WHERE created_at > '2025-06-01'"
    """
    result = sql
    # 改写 FROM 子句
    for logical_name in list(MONTHLY_SHARDED) + list(TENANT_SHARDED):
        if logical_name in UNSHARDED:
            continue
        # 简单词替换（仅替换独立词，防止 "performance_metrics_xxx" 被二次替换）
        pattern = rf"\b({re.escape(logical_name)})\b(?!\w)"
        if re.search(pattern, result):
            physical = get_physical_table(logical_name, tenant_id=tenant_id, dt=dt)
            result = re.sub(pattern, physical, result)
    return result


def guess_dt_from_sql(sql: str) -> Optional[datetime]:
    """
    从 SQL WHERE 条件中猜测时间范围（如 created_at BETWEEN '2025-06-01' AND '2025-06-30'）。
    如果命中，返回该月1号的 datetime。
    """
    # 匹配 YYYY-MM 或 YYYY-MM-DD 格式
    patterns = [
        r"\b(\d{4}-\d{2})(?:-\d{2})?",       # 2025-06 或 2025-06-15
        r"\b(\d{4})(\d{2})(\d{2})?\b",        # 202506 或 20250615
    ]
    for p in patterns:
        m = re.search(p, sql)
        if m:
            if len(m.group(1)) == 4:  # YYYY-MM-DD
                year, month = int(m.group(1)), int(m.group(2))
                return datetime(year, month, 1)
            else:  # YYYYMM
                year, month = int(m.group(1)), int(m.group(2))
                return datetime(year, month, 1)
    return None


def _remove_foreign_keys(ddl: str, logical_name: str, physical: str) -> str:
    """
    移除 DDL 中的所有 FOREIGN KEY 和 CONSTRAINT 定义。
    包括：
      1. CONSTRAINT xxx FOREIGN KEY (...) REFERENCES (...) [ON DELETE ...] [ON UPDATE ...]
      2. FOREIGN KEY (...) REFERENCES (...) [ON DELETE ...] [ON UPDATE ...]
      3. 列级内联 REFERENCES table(column) 定义
    使用括号配对算法准确定位每个外键块的起止位置。
    """
    import re

    # 先替换表名
    result = ddl.replace(f"CREATE TABLE `{logical_name}`", f"CREATE TABLE `{physical}`")
    result = result.replace(f"CREATE TABLE {logical_name}", f"CREATE TABLE `{physical}`")

    # 第一步：移除 CONSTRAINT xxx FOREIGN KEY 和 FOREIGN KEY 块（使用括号配对）
    output = []
    i = 0
    n = len(result)

    while i < n:
        rest = result[i:]
        if rest.startswith("CONSTRAINT") or (rest.lstrip().startswith("FOREIGN KEY")):
            # 找块的结束位置（匹配括号）
            depth = 0
            in_parens = False
            while i < n:
                ch = result[i]
                if ch == '(':
                    depth += 1
                    in_parens = True
                elif ch == ')':
                    depth -= 1
                    if depth == 0 and in_parens:
                        i += 1  # 包含右括号
                        break
                i += 1
            # 跳过逗号或空白直到下一个字段或结束
            while i < n and result[i] in ' \t\n,':
                i += 1
            # 不添加到 output（跳过外键块）
            continue
        output.append(result[i])
        i += 1

    result = ''.join(output)

    # 第二步：移除列级内联 REFERENCES（在列定义内的 REFERENCES table(column)）
    # 处理多种格式： REFERENCES `table`(`col`)、 REFERENCES table(col)、带换行的多行格式
    result = re.sub(
        r"REFERENCES\s+`?[\w]+`?\s*\(\s*`?[\w]+`?\s*\)",
        "",
        result,
        flags=re.IGNORECASE
    )
    # 也处理只有 REFERENCES table 列名的情况（无括号，说明已被移除）
    result = re.sub(r"REFERENCES\s+`?[\w]+`?\s*", "", result, flags=re.IGNORECASE)

    # 第三步：清理多余逗号（外键块移除后可能遗留 , )
    result = re.sub(r",\s*(PRIMARY|KEY|UNIQUE|INDEX)", r"\1", result, flags=re.IGNORECASE)
    result = re.sub(r",\s*\)", r")", result)
    result = re.sub(r"\(\s*,", r"(", result)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Shard Manager — 管理分片生命周期
# ──────────────────────────────────────────────────────────────────────────────

class ShardManager:
    """
    分片管理器：负责检测、创建、清理分片。
    与 ShardingRouter 配合使用。
    """

    def __init__(self, db_executor: Callable[[str], Any]):
        """
        Args:
            db_executor: 执行 SQL 的回调函数，接受 SQL 字符串，返回结果。
                        例如：lambda sql: _db_manager.execute(sql)
        """
        self._exec = db_executor

    def ensure_shard_exists(self, logical_name: str, tenant_id: Optional[str] = None,
                            dt: Optional[datetime] = None) -> str:
        """
        确保分片表存在，如不存在则创建。
        返回物理表名。
        """
        physical = get_physical_table(logical_name, tenant_id=tenant_id, dt=dt)

        # 检查表是否已存在（rows 是 list of dict，SHOW TABLES 返回 {"Tables_in_itops_platform": "table_name"}）
        check_rows = self._exec(f"SHOW TABLES LIKE '{physical}'")
        if check_rows and len(check_rows) > 0:
            return physical  # 表已存在

        # 获取主表 DDL（返回 list of dict [{"Table":..., "Create Table":...}]）
        raw_rows = self._exec(f"SHOW CREATE TABLE {logical_name}")
        if not raw_rows:
            raise RuntimeError(f"无法获取主表 {logical_name} 的建表语句")
        first_row = raw_rows[0]  # list of dict
        ddl = first_row.get("Create Table", "")
        if not ddl:
            raise RuntimeError(f"无法解析主表 {logical_name} 的 DDL")

        # 清理 DDL（移除 FOREIGN KEY 约束）后创建分片表
        new_ddl = _remove_foreign_keys(ddl, logical_name, physical)

        # 如果是租户分片，添加租户索引
        if logical_name in TENANT_SHARDED and tenant_id:
            if "INDEX" not in new_ddl.upper() and "KEY" not in new_ddl.upper():
                new_ddl += f", INDEX idx_tenant (tenant_id)"

        # 如果是月分片，添加月份索引
        if logical_name in MONTHLY_SHARDED and dt:
            if "INDEX" not in new_ddl.upper() and "KEY" not in new_ddl.upper():
                new_ddl += f", INDEX idx_created_at (created_at)"

        self._exec(new_ddl)
        return physical

    def list_existing_shards(self, logical_name: str) -> List[str]:
        """列出数据库中已存在的某逻辑表的所有分片"""
        pattern = f"{logical_name}_%"
        rows = self._exec(f"SHOW TABLES LIKE '{pattern}'")
        if not rows:
            return []
        # 返回是 list of dict，key 格式为 "Tables_in_itops_platform (pattern)"
        result = []
        for r in rows:
            if isinstance(r, dict):
                # 取字典中第一个 value（表名）
                result.append(next(iter(r.values())))
            elif isinstance(r, (list, tuple)):
                result.append(str(r[0]))
            else:
                result.append(str(r))
        return result

    def auto_create_current_shards(self, logical_name: str) -> List[str]:
        """
        自动为当前月份创建时序分片（如不存在）。
        对租户分片表，需提前知道所有租户ID再创建。
        """
        created = []
        if logical_name in MONTHLY_SHARDED:
            now = datetime.now()
            physical = self.ensure_shard_exists(logical_name, dt=now)
            created.append(physical)
            # 同时创建上一个月（防止数据回填）
            import calendar
            first = now.replace(day=1)
            prev = first - __import__("datetime").timedelta(days=1)
            prev_physical = self.ensure_shard_exists(logical_name, dt=prev)
            if prev_physical not in created:
                created.append(prev_physical)
        elif logical_name in TENANT_SHARDED:
            # 从 tenants 表读取所有租户ID
            tenant_rows = self._exec("SELECT id FROM tenants")
            for row in tenant_rows:
                tid = row[0] if isinstance(row, (list, tuple)) else row.get("id")
                physical = self.ensure_shard_exists(logical_name, tenant_id=tid)
                created.append(physical)
        return created
