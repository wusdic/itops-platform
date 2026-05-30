#!/usr/bin/env python3
"""
ITOps Platform — Agent Self-Check Guard Script
===============================================
在每次任务开始前运行此脚本，确保 Agent 已经读取了 docs/ 事实源。

使用方法：
    python scripts/agent_self_check.py

如果此脚本返回非零，Agent 必须重新读取 docs/00-overview/README.md，
否则任务结果将被视为无效。

退出码：
    0 = 检查通过（docs/ 事实源已就位）
    1 = 检查失败（缺少关键文档或配置）
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_DOCS = {
    "docs/00-overview/README.md": "文档入口（必须首先读取）",
    "docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md": "目标架构（最高级依据）",
    "docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md": "代码取舍与治理方案",
    "docs/05-implementation/TODO.md": "当前各 Phase 执行状态",
}

REQUIRED_CODE_DIRS = {
    "api/routes": "后端路由层（当前唯一）",
    "modules/business": "业务逻辑层（当前唯一）",
    "modules/collection": "采集器（当前唯一）",
}


def check_docs():
    print("📋 事实源文档检查...")
    all_pass = True
    for rel_path, desc in REQUIRED_DOCS.items():
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        status = "✅" if os.path.exists(full_path) else "❌"
        print(f"  {status} {rel_path} — {desc}")
        if not os.path.exists(full_path):
            all_pass = False
    return all_pass


def check_code_dirs():
    print("\n📁 当前代码目录检查...")
    all_pass = True
    for rel_path, desc in REQUIRED_CODE_DIRS.items():
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        status = "✅" if os.path.isdir(full_path) else "❌"
        print(f"  {status} {rel_path} — {desc}")
        if not os.path.isdir(full_path):
            all_pass = False
    return all_pass


def check_hermes_rules():
    print("\n📜 HERMES_RULES.md 检查...")
    rules_path = os.path.join(PROJECT_ROOT, "HERMES_RULES.md")
    if os.path.exists(rules_path):
        # 检查文件是否提到 docs/ 事实源
        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "docs/00-overview/README.md" in content and "Single Source of Truth" in content:
            print(f"  ✅ HERMES_RULES.md 存在且包含事实源规则")
            return True
        else:
            print(f"  ⚠️ HERMES_RULES.md 存在但内容不完整")
            return False
    else:
        print(f"  ⚠️ HERMES_RULES.md 不存在（建议创建）")
        return True  # 不强制退出


def main():
    print("=" * 60)
    print("🛡️ ITOps Platform Agent Self-Check")
    print("=" * 60)
    print()

    docs_ok = check_docs()
    code_ok = check_code_dirs()
    rules_ok = check_hermes_rules()

    print()
    print("=" * 60)

    if not docs_ok:
        print("❌ 检查失败：缺少关键事实源文档")
        print("   → 必须先在 docs/ 目录下建立完整的架构文档")
        sys.exit(1)

    if not code_ok:
        print("❌ 检查失败：缺少当前代码目录")
        print("   → 当前系统可能已被破坏")
        sys.exit(1)

    print("✅ 所有检查通过")
    print()
    print("📌 记住：在开始任何任务前，必须先执行：")
    print("   head -50 docs/00-overview/README.md")
    print()
    sys.exit(0)


if __name__ == "__main__":
    main()
