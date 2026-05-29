#!/usr/bin/env python3
"""
Phase 7-6: 磁盘清理策略示例数据初始化脚本

用途：为 ITOps Platform 创建"磁盘清理策略"示例，串联完整闭环：
  disk_usage > 90% → 触发策略 → AI 分析 → dry-run → 执行 → 验证

运行方式：
  cd /home/zcxx/.hermes/projects/itops_platform
  python3 docs/07-operations/seed_disk_cleanup_example.py

验证：
  curl -s http://localhost:8000/api/v1/policies | jq '.data[] | select(.name | contains("磁盘"))'
  curl -s http://localhost:8000/api/v1/automation/scripts | jq '.data[] | select(.name | contains("磁盘"))'
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uuid
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


DISK_CLEANUP_SCRIPT = {
    "name": "disk-cleanup",
    "description": "磁盘清理脚本：删除临时文件、清理日志、清理包缓存（CentOS/Ubuntu/Debian）",
    "script_type": "shell",
    "risk_level": "high",
    "tags": ["disk", "cleanup", "maintenance"],
    "content": r"""#!/bin/bash
# disk-cleanup.sh — 磁盘清理脚本（Phase 7-6 示例）
# 用途：清理临时文件、日志、缓存，演示磁盘使用率>90%时的自动化处置闭环
# 风险：high — 需在测试环境验证后再用于生产

set -euo pipefail

LOG_PREFIX="[disk-cleanup]"
TARGET_DEVICE_ID="${TARGET_DEVICE_ID:-unknown}"

echo "$LOG_PREFIX 开始磁盘清理，目标设备: $TARGET_DEVICE_ID"
echo "$LOG_PREFIX 清理前磁盘使用率："
df -h | grep -E '/$|/var' || true

# 1. 清理临时文件
echo "$LOG_PREFIX 步骤1: 清理 /tmp 目录（保留7天内的文件）..."
find /tmp -type f -atime +7 -delete 2>/dev/null || true
find /var/tmp -type f -atime +7 -delete 2>/dev/null || true

# 2. 清理包管理器缓存
echo "$LOG_PREFIX 步骤2: 清理包管理器缓存..."
if command -v yum &>/dev/null; then
    yum clean all 2>/dev/null || true
    package-cleanup --oldkernels --count=1 -y 2>/dev/null || true
elif command -v apt-get &>/dev/null; then
    apt-get clean 2>/dev/null || true
    apt-get autoremove -y 2>/dev/null || true
fi

# 3. 清理旧日志（保留最近7天）
echo "$LOG_PREFIX 步骤3: 清理 /var/log 旧日志..."
find /var/log -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
find /var/log -type f -name "*.gz" -mtime +30 -delete 2>/dev/null || true

# 4. 清理 journal 日志（保留最近7天）
if command -v journalctl &>/dev/null; then
    echo "$LOG_PREFIX 步骤4: 清理 journal 日志..."
    journalctl --vacuum-time=7d 2>/dev/null || true
fi

# 5. 清理 pip 缓存
if command -v pip3 &>/dev/null; then
    echo "$LOG_PREFIX 步骤5: 清理 pip 缓存..."
    pip3 cache purge 2>/dev/null || true
fi

echo "$LOG_PREFIX 清理完成，磁盘使用率："
df -h | grep -E '/$|/var' || true
echo "$LOG_PREFIX 脚本执行成功完成"

# 模拟执行耗时
sleep 3
exit 0
""",
    "params_schema": [
        {"name": "TARGET_DEVICE_ID", "type": "string", "required": True, "description": "目标设备ID"}
    ],
}

DISK_CLEANUP_POLICY = {
    "name": "磁盘使用率过高自动清理",
    "description": "当设备磁盘使用率超过90%时，自动执行磁盘清理脚本。先dry-run验证，最后验证清理效果。",
    "trigger_source": "alert",
    "trigger_type": "disk_usage_high",
    "risk_level": "high",
    "require_approval": 1,
    "scope": {"scope_type": "device_ids"},
    "condition": {
        "metric": "disk_usage_percent",
        "operator": "gt",
        "threshold": 90,
    },
    "actions": [
        {"type": "ai_analyze", "description": "AI分析磁盘使用原因"},
        {"type": "dry_run", "description": "先 dry-run 验证脚本安全性"},
        {"type": "execute_script", "script_name": "disk-cleanup", "description": "执行磁盘清理脚本"},
        {"type": "verify", "description": "验证清理效果"},
    ],
    "verification": {
        "metric_name": "disk_usage_percent",
        "expected_operator": "lt",
        "expected_value": 80,
        "tolerance": 5,
    },
}


def seed():
    from modules.foundation.db_models.base import DatabaseManager, Base
    from modules.foundation.db_models.automation import AutomationScript, AutomationScriptVersion
    from app.domains.policy.models import Policy, PolicyVersion
    from app.domains.policy.service import PolicyService
    from app.common.database import get_db_session

    # 确保 policy_versions 表存在
    db_mgr = DatabaseManager()
    db_mgr.setup()
    engine = db_mgr.get_engine()
    PolicyVersion.__table__.create(bind=engine, checkfirst=True)

    db = db_mgr.get_session()

    try:
        # Step 1: 创建磁盘清理脚本
        logger.info("Step 1: 创建磁盘清理脚本...")
        script_id = f"scr-{uuid.uuid4().hex[:16]}"
        version_id = f"v-{uuid.uuid4().hex[:16]}"

        version = AutomationScriptVersion(
            id=version_id,
            script_id=script_id,
            version=1,
            content=DISK_CLEANUP_SCRIPT["content"],
            change_summary="Initial version — disk cleanup script (Phase 7-6 example)",
            created_by="system",
        )
        db.add(version)

        script = AutomationScript(
            id=script_id,
            name=DISK_CLEANUP_SCRIPT["name"],
            description=DISK_CLEANUP_SCRIPT["description"],
            script_type=DISK_CLEANUP_SCRIPT["script_type"],
            content=DISK_CLEANUP_SCRIPT["content"],
            risk_level=DISK_CLEANUP_SCRIPT["risk_level"],
            params_schema=json.dumps(DISK_CLEANUP_SCRIPT["params_schema"]),
            tags=json.dumps(DISK_CLEANUP_SCRIPT["tags"]),
            source="example",
            created_by="system",
        )
        db.add(script)
        db.commit()
        logger.info(f"  ✅ 脚本已创建: {script_id} ({DISK_CLEANUP_SCRIPT['name']})")

        # Step 2: 创建策略
        logger.info("Step 2: 创建磁盘清理策略...")
        policy_id = PolicyService.create_policy({
            "name": DISK_CLEANUP_POLICY["name"],
            "description": DISK_CLEANUP_POLICY["description"],
            "trigger_source": DISK_CLEANUP_POLICY["trigger_source"],
            "trigger_type": DISK_CLEANUP_POLICY["trigger_type"],
            "condition": DISK_CLEANUP_POLICY["condition"],
            "scope": DISK_CLEANUP_POLICY["scope"],
            "risk_level": DISK_CLEANUP_POLICY["risk_level"],
            "require_approval": DISK_CLEANUP_POLICY["require_approval"],
            "actions": DISK_CLEANUP_POLICY["actions"],
            "verification": DISK_CLEANUP_POLICY["verification"],
        })
        logger.info(f"  ✅ 策略已创建: {policy_id} ({DISK_CLEANUP_POLICY['name']})")

        # Step 3: 发布策略（创建版本快照）
        logger.info("Step 3: 创建策略版本快照...")
        version_snapshot_id = PolicyService.create_version(
            policy_id,
            change_summary="初始版本 — 磁盘清理策略 (Phase 7-6 示例)",
            created_by="system",
        )

        # 将策略状态更新为 published
        with get_db_session() as s:
            policy = s.query(Policy).filter(Policy.policy_id == policy_id).first()
            if policy:
                policy.status = "published"
                s.commit()
                logger.info(f"  ✅ 策略已发布: status=published")

        logger.info(f"  ✅ 版本快照已创建: {version_snapshot_id}")

        # 汇总
        logger.info("")
        logger.info("=" * 60)
        logger.info("Phase 7-6 示例数据初始化完成！")
        logger.info("=" * 60)
        logger.info(f"  脚本ID:   {script_id}")
        logger.info(f"  脚本名称: {DISK_CLEANUP_SCRIPT['name']}")
        logger.info(f"  策略ID:   {policy_id}")
        logger.info(f"  策略名称: {DISK_CLEANUP_POLICY['name']}")
        logger.info(f"  触发条件: disk_usage_percent > 90%")
        logger.info(f"  执行动作: dry_run → 磁盘清理 → 验证 (disk_usage < 80%)")
        logger.info("")
        logger.info("验证方式：")
        logger.info(f"  curl http://localhost:8000/api/v1/automation/scripts | jq '.data[] | select(.name==\"{DISK_CLEANUP_SCRIPT['name']}\")'")
        logger.info(f"  curl http://localhost:8000/api/v1/policies | jq '.data[] | select(.name | contains(\"磁盘\"))'")
        logger.info("")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
