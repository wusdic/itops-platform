#!/usr/bin/env python3
"""
ITOps Platform - Preflight Check Script
部署前检查脚本，验证各项服务配置是否正确
"""

import os
import sys
import socket
import urllib.request
import urllib.error

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def load_env():
    """加载 .env 文件"""
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value.strip()
    return env_vars


def check_env_file():
    """检查 .env 文件是否存在"""
    if not os.path.exists(ENV_FILE):
        print(f"ERROR: .env file not found at {ENV_FILE}")
        return False
    print("OK: .env file exists")
    return True


def check_db_connection(env_vars):
    """检查数据库连接"""
    host = env_vars.get("ITOPS_DB_HOST", "localhost")
    port = int(env_vars.get("ITOPS_DB_PORT", "3306"))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"OK: Database connection to {host}:{port}")
            return True
        else:
            print(f"ERROR: Cannot connect to database at {host}:{port}")
            return False
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False


def check_redis_connection(env_vars):
    """检查 Redis 连接"""
    host = env_vars.get("ITOPS_REDIS_HOST", "localhost")
    port = int(env_vars.get("ITOPS_REDIS_PORT", "6379"))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"OK: Redis connection to {host}:{port}")
            return True
        else:
            print(f"ERROR: Cannot connect to Redis at {host}:{port}")
            return False
    except Exception as e:
        print(f"ERROR: Redis connection failed: {e}")
        return False


def check_jwt_secret(env_vars):
    """检查 JWT_SECRET 是否为默认值"""
    jwt_secret = env_vars.get("ITOPS_JWT_SECRET", "")
    
    # 检查是否为空或包含明显的不安全默认值
    unsafe_defaults = [
        "your-secret-key-change-in-production",
        "your-secret-key",
        "secret",
        "changeme",
        "changethis",
    ]
    
    if not jwt_secret:
        print("ERROR: JWT_SECRET is empty, please set it in .env")
        return False
    
    # 检查是否为不安全默认值
    jwt_lower = jwt_secret.lower()
    for unsafe in unsafe_defaults:
        if jwt_lower == unsafe.lower():
            print(f"ERROR: JWT_SECRET is using default value '{unsafe}', please change it in .env")
            return False
    
    print("OK: JWT_SECRET is properly configured")
    return True


def check_default_admin_password(env_vars):
    """检查默认管理员密码是否已修改"""
    # 尝试通过 API 登录验证默认密码是否已修改
    host = env_vars.get("ITOPS_HOST", "0.0.0.0")
    port = int(env_vars.get("ITOPS_PORT", "8000"))
    
    if host in ("0.0.0.0", "127.0.0.1", "localhost"):
        check_host = "127.0.0.1"
    else:
        check_host = host
    
    try:
        import json
        url = f"http://{check_host}:{port}/api/v1/auth/login"
        data = json.dumps({"username": "admin", "password": "Admin@123456"}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Preflight-Check/1.0")
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            if response.status == 200:
                # 登录成功说明默认密码未修改
                print("ERROR: Default admin password 'Admin@123456' is still in use")
                return False
            else:
                print("OK: Admin password appears to be changed")
                return True
    except urllib.error.HTTPError as e:
        # 401 错误表示密码不对，说明密码已修改
        if e.code == 401:
            print("OK: Admin password appears to be changed")
            return True
        # 其他 HTTP 错误
        print(f"WARN: Could not verify admin password (HTTP {e.code})")
        return True
    except Exception as e:
        # API 未启动或无法连接，忽略
        print(f"WARN: Could not verify admin password via API: {e}")
        return True


def check_api_service(env_vars):
    """检查 API 服务是否在线"""
    host = env_vars.get("ITOPS_HOST", "0.0.0.0")
    port = int(env_vars.get("ITOPS_PORT", "8000"))
    
    # 只检查本机服务
    if host in ("0.0.0.0", "127.0.0.1", "localhost"):
        check_host = "127.0.0.1"
    else:
        check_host = host
    
    try:
        url = f"http://{check_host}:{port}/health"
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "Preflight-Check/1.0")
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"OK: API service is online at http://{check_host}:{port}")
                return True
            else:
                print(f"WARN: API service returned status {response.status}")
                return True  # 不阻止部署
    except urllib.error.URLError as e:
        print(f"WARN: API service is not running at http://{check_host}:{port} (may be expected before deployment)")
        return True  # 部署前 API 未启动不算错误
    except Exception as e:
        print(f"WARN: API service check failed: {e}")
        return True


def main():
    """主检查流程"""
    print("=" * 60)
    print("ITOps Platform - Preflight Check")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 1. 检查 .env 文件
    print("[1/6] Checking .env file...")
    if not check_env_file():
        all_passed = False
    print()
    
    # 2. 加载环境变量
    env_vars = load_env()
    
    # 3. 检查数据库连接
    print("[2/6] Checking database connection...")
    if not check_db_connection(env_vars):
        all_passed = False
    print()
    
    # 4. 检查 Redis 连接
    print("[3/6] Checking Redis connection...")
    if not check_redis_connection(env_vars):
        all_passed = False
    print()
    
    # 5. 检查 JWT_SECRET
    print("[4/6] Checking JWT_SECRET configuration...")
    if not check_jwt_secret(env_vars):
        all_passed = False
    print()
    
    # 6. 检查默认管理员密码
    print("[5/6] Checking admin password configuration...")
    if not check_default_admin_password(env_vars):
        all_passed = False
    print()
    
    # 7. 检查 API 服务
    print("[6/6] Checking API service status...")
    if not check_api_service(env_vars):
        all_passed = False
    print()
    
    # 总结
    print("=" * 60)
    if all_passed:
        print("All checks passed")
        sys.exit(0)
    else:
        print("Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
