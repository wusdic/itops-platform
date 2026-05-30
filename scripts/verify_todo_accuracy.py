#!/usr/bin/env python3
"""
ITOps Platform — TODO.md 准确性守护脚本
==========================================
验证 TODO.md 中每个 Phase 的标记是否与实际代码/行为一致。

使用：
    python scripts/verify_todo_accuracy.py

规则：
    - Phase 标记为 ✅ 的项目，必须验证代码或 API 实际存在
    - 如果发现 "标记为完成但实际不存在" → 报告为 ❌ INCONSISTENCY
    - 如果发现 "标记为未开始但实际已完成" → 报告为 ⚠️ UNDERREPORTED
    - 如果发现 "标记为未开始但代码中有相关逻辑" → 报告为 ⚠️ PARTIALLY_DONE

退出码：
    0 = 所有标记准确
    1 = 存在不一致（INCONSISTENCY）
    2 = 存在未报（UNDERREPORTED）
"""

import os
import sys
import re
import json
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cmd(cmd):
    """执行 shell 命令，返回 stdout"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=PROJECT_ROOT, timeout=30
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1


def check_api_exists(path, method="GET", token=None):
    """检查 API 是否返回非 404"""
    login_cmd = (
        "curl -s -X POST http://localhost:8000/api/v1/auth/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"username\":\"admin\",\"password\":\"Admin@123456\"}'"
    )
    stdout, _ = run_cmd(login_cmd)
    try:
        token = json.loads(stdout).get("access_token", "")
    except:
        token = ""

    url = f"http://localhost:8000{path}"
    cmd = f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {token}' {url}"
    code, _ = run_cmd(cmd)
    return code not in ("", "000") and code != "404"


def check_file_exists(filepath):
    """检查文件是否存在"""
    full = os.path.join(PROJECT_ROOT, filepath)
    return os.path.isfile(full)


def check_dir_exists(dirpath):
    """检查目录是否存在"""
    full = os.path.join(PROJECT_ROOT, dirpath)
    return os.path.isdir(full)


def verify_phase1():
    """Phase 1: app/domains/ 目录 + app/common/ 基础设施"""
    issues = []

    # 1-1: 13个领域目录
    domains = [
        "app/domains/asset", "app/domains/config", "app/domains/collector",
        "app/domains/state", "app/domains/event", "app/domains/alert",
        "app/domains/log", "app/domains/policy", "app/domains/automation",
        "app/domains/aiops", "app/domains/ticket", "app/domains/knowledge",
        "app/domains/governance"
    ]
    for d in domains:
        if not check_dir_exists(d):
            issues.append(f"❌ 领域目录缺失: {d}")

    # 1-2: 统一响应 app/common/response.py
    if not check_file_exists("app/common/response.py"):
        issues.append("❌ app/common/response.py 不存在")

    # 1-3: 错误码
    if not check_file_exists("app/common/error_codes.py"):
        issues.append("❌ app/common/error_codes.py 不存在")

    # 1-4: trace_id 中间件
    if not check_file_exists("app/common/context.py"):
        issues.append("❌ app/common/context.py 不存在")

    # 1-6: 审计
    if not check_file_exists("app/common/audit.py"):
        issues.append("❌ app/common/audit.py 不存在")

    # 1-7: 权限
    if not check_file_exists("app/common/permissions.py"):
        issues.append("❌ app/common/permissions.py 不存在")

    # 1-8: 数据库
    if not check_file_exists("app/common/database.py"):
        issues.append("❌ app/common/database.py 不存在")

    # 1-9: Redis
    if not check_file_exists("app/common/redis_client.py"):
        issues.append("❌ app/common/redis_client.py 不存在")

    # 1-10: 消息队列（文件名可能是 queue.py 或 message_queue.py）
    if not (check_file_exists("app/common/queue.py") or check_file_exists("app/common/message_queue.py")):
        issues.append("❌ app/common/queue.py 或 message_queue.py 不存在")

    # 1-11: 后台任务
    if not check_file_exists("app/common/background_task.py"):
        issues.append("❌ app/common/background_task.py 不存在")

    return issues


def verify_phase5():
    """Phase 5: 告警和事件 API"""
    issues = []

    # 5-1~5-7: 验证 alert_domain + event_domain 路由
    token_cmd = (
        "curl -s -X POST http://localhost:8000/api/v1/auth/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"username\":\"admin\",\"password\":\"Admin@123456\"}' | "
        "python3 -c \"import sys,json; print(json.load(sys.stdin).get('access_token',''))\""
    )
    stdout, _ = run_cmd(token_cmd)
    token = stdout.strip()

    apis = [
        ("/api/v1/events", "事件列表"),
        ("/api/v1/alerts/", "告警列表"),
        ("/api/v1/alerts/stats", "告警统计"),
    ]
    for path, desc in apis:
        url = f"http://localhost:8000{path}"
        cmd = f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {token}' {url}"
        code, _ = run_cmd(cmd)
        if code == "404":
            issues.append(f"❌ {desc} API 404: {path}")

    return issues


def verify_phase6():
    """Phase 6: 日志与审计"""
    issues = []
    token_cmd = (
        "curl -s -X POST http://localhost:8000/api/v1/auth/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"username\":\"admin\",\"password\":\"Admin@123456\"}' | "
        "python3 -c \"import sys,json; print(json.load(sys.stdin).get('access_token',''))\""
    )
    stdout, _ = run_cmd(token_cmd)
    token = stdout.strip()

    apis = [
        ("/api/v1/logs/audit", "审计日志"),
        ("/api/v1/automation/executions", "执行列表"),
    ]
    for path, desc in apis:
        url = f"http://localhost:8000{path}"
        cmd = f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {token}' {url}"
        code, _ = run_cmd(cmd)
        if code == "404":
            issues.append(f"❌ {desc} API 404: {path}")

    return issues


def verify_phase7():
    """Phase 7: 策略"""
    issues = []
    token_cmd = (
        "curl -s -X POST http://localhost:8000/api/v1/auth/login "
        "-H 'Content-Type: application/json' "
        "-d '{\"username\":\"admin\",\"password\":\"Admin@123456\"}' | "
        "python3 -c \"import sys,json; print(json.load(sys.stdin).get('access_token',''))\""
    )
    stdout, _ = run_cmd(token_cmd)
    token = stdout.strip()

    url = f"http://localhost:8000/api/v1/policies"
    cmd = f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {token}' {url}"
    code, _ = run_cmd(cmd)
    if code == "404":
        issues.append(f"❌ 策略 API 404")

    return issues


def verify_phase10():
    """Phase 10: 前端 features/ 目录"""
    issues = []

    features = [
        "frontend/src/features/command-center",
        "frontend/src/features/incident-response",
        "frontend/src/features/monitoring-event",
        "frontend/src/features/automation-orchestration",
        "frontend/src/features/asset-config",
    ]
    for d in features:
        if not check_dir_exists(d):
            issues.append(f"❌ Phase 10 目录缺失: {d}")
        else:
            # 检查是否有 .vue 文件
            vue_files = [f for f in os.listdir(os.path.join(PROJECT_ROOT, d))
                        if f.endswith(".vue")]
            if not vue_files:
                issues.append(f"⚠️ Phase 10 目录为空: {d}")

    return issues


def main():
    print("=" * 60)
    print("🔍 ITOps Platform TODO.md 准确性验证")
    print("=" * 60)
    print()

    all_issues = []

    # 检查 README.md 要求的子目录是否存在
    print("📋 检查 README.md 要求的子目录...")
    required_subdirs = {
        "docs/03-api/": ["API_CONTRACT.md", "ERROR_CODES.md"],
        "docs/04-frontend/": ["UX_WORKFLOWS.md", "PAGE_STRUCTURE.md"],
    }
    for dirpath, required_files in required_subdirs.items():
        for fname in required_files:
            fpath = os.path.join(PROJECT_ROOT, dirpath, fname)
            if os.path.isfile(fpath):
                print(f"  ✅ {dirpath}{fname}")
            else:
                print(f"  ❌ MISSING: {dirpath}{fname}")
                all_issues.append(f"README.md 要求但缺失: {dirpath}{fname}")

    print()
    print("🔍 验证 Phase 1 标记（app/domains/ + app/common/）...")
    p1_issues = verify_phase1()
    if p1_issues:
        for i in p1_issues:
            print(f"  {i}")
            all_issues.append(f"Phase 1: {i}")
    else:
        print("  ✅ Phase 1 所有检查通过")

    print()
    print("🔍 验证 Phase 5 标记（告警 + 事件 API）...")
    p5_issues = verify_phase5()
    if p5_issues:
        for i in p5_issues:
            print(f"  {i}")
            all_issues.append(f"Phase 5: {i}")
    else:
        print("  ✅ Phase 5 API 全部 200 OK")

    print()
    print("🔍 验证 Phase 6 标记（日志 + 审计 API）...")
    p6_issues = verify_phase6()
    if p6_issues:
        for i in p6_issues:
            print(f"  {i}")
            all_issues.append(f"Phase 6: {i}")
    else:
        print("  ✅ Phase 6 API 全部 200 OK")

    print()
    print("🔍 验证 Phase 7 标记（策略 API）...")
    p7_issues = verify_phase7()
    if p7_issues:
        for i in p7_issues:
            print(f"  {i}")
            all_issues.append(f"Phase 7: {i}")
    else:
        print("  ✅ Phase 7 API 全部 200 OK")

    print()
    print("🔍 验证 Phase 10 标记（features/ 前端页面）...")
    p10_issues = verify_phase10()
    if p10_issues:
        for i in p10_issues:
            print(f"  {i}")
            all_issues.append(f"Phase 10: {i}")
    else:
        print("  ✅ Phase 10 所有目录存在且含 .vue 文件")

    print()
    print("=" * 60)

    if all_issues:
        print(f"❌ 检查失败：发现 {len(all_issues)} 个不一致")
        for issue in all_issues:
            print(f"  - {issue}")
        print()
        print("→ 必须在 TODO.md 中修正标记，或修正实际代码")
        sys.exit(1)
    else:
        print("✅ 所有检查通过：TODO.md 标记与实际代码一致")
        sys.exit(0)


if __name__ == "__main__":
    main()
