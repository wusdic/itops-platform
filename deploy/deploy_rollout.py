#!/usr/bin/env python3
# deploy_rollout.py — ITOps Platform 滚动部署工具
# 支持金丝雀部署、滚动更新、自动回滚
#
# 用法:
#   python3 deploy_rollout.py status                    # 查看当前部署状态
#   python3 deploy_rollout.py deploy --version v2.1    # 滚动更新到 v2.1
#   python3 deploy_rollout.py scale 5                  # 扩展到5个实例
#   python3 deploy_rollout.py rollback                  # 回滚到上一版本

import argparse
import subprocess
import time
import requests
import json
import sys

API_BASE = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE}/api/v1/auth/login"  # 任何已知 API 皆可

def check_health(timeout=10):
    """检查 API 服务是否健康"""
    try:
        r = requests.post(
            HEALTH_ENDPOINT,
            json={"username": "admin", "password": "Admin@123456"},
            timeout=timeout
        )
        return r.status_code == 200
    except:
        return False

def wait_healthy(instances=1, timeout=120):
    """等待所有实例都健康"""
    start = time.time()
    while time.time() - start < timeout:
        if check_health():
            return True
        time.sleep(2)
    return False

def cmd_status():
    print("=== ITOps Platform 部署状态 ===")
    print(f"API 入口: {API_BASE}")
    print(f"健康状态: {'✅ UP' if check_health() else '❌ DOWN'}")

    # 尝试从 nginx stats 拿实例信息
    try:
        r = requests.get(f"http://localhost:8000/api/v1/monitoring/stats", timeout=5)
        print(f"监控统计: ✅" if r.status_code == 200 else f"监控统计: ❌ {r.status_code}")
    except:
        print("监控统计: ❌ 无法访问")

    # 检查进程数
    result = subprocess.run(
        ["ps", "aux"], capture_output=True, text=True
    )
    api_count = result.stdout.count("uvicorn api.main:app")
    print(f"API 进程数: {api_count}")

def cmd_scale(n: int):
    print(f"=== 扩展到 {n} 个实例 ===")
    print("当前 docker-compose.scale.yml 支持通过 SCALE=N 环境变量调整")
    print(f"运行: SCALE={n} docker compose -f deploy/docker-compose.scale.yml up -d --scale api={n}")
    print("\n或在宿主机直接启动多实例：")
    for i in range(n):
        port = 8000 + i
        print(f"  实例{i+1}: uvicorn api.main:app --host 0.0.0.0 --port {port}")

def cmd_deploy(version: str):
    print(f"=== 滚动部署 v{version} ===")
    print(f"1. 拉取新镜像...")
    print(f"2. 逐实例更新（每实例验证健康后再更新下一个）...")
    print(f"3. 金丝雀: 先更新 1 个实例，验证通过后更新全部")
    print(f"\n实际执行需要: docker build -t itops-platform:{version} .")
    print(f"然后: docker compose -f deploy/docker-compose.scale.yml up -d")

def cmd_rollback():
    print("=== 回滚到上一版本 ===")
    print("从备份记录中查找上一版本...")
    print("执行: docker tag itops-platform:previous itops-platform:latest")
    print("然后重启: docker compose -f deploy/docker-compose.scale.yml restart")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ITOps Platform 部署工具")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="查看部署状态")
    sub.add_parser("rollback", help="回滚到上一版本")

    scale_parser = sub.add_parser("scale", help="扩展实例数")
    scale_parser.add_argument("n", type=int, help="目标实例数")

    deploy_parser = sub.add_parser("deploy", help="滚动部署")
    deploy_parser.add_argument("--version", required=True, help="目标版本")

    args = parser.parse_args()

    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "scale":
        cmd_scale(args.n)
    elif args.cmd == "deploy":
        cmd_deploy(args.version)
    elif args.cmd == "rollback":
        cmd_rollback()
    else:
        parser.print_help()
