#!/usr/bin/env python3
"""
执行迁移脚本 013: 资产中心表创建
通过 SQLAlchemy 创建 assets 等新表（不依赖 MySQL 命令行）
"""
import sys
sys.path.insert(0, '/home/zcxx/.hermes/projects/itops_platform')

from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 读取 .env
env_path = Path('/home/zcxx/.hermes/projects/itops_platform/.env')
for line in env_path.read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        if k == 'ITOPS_DB_HOST': DB_HOST = v
        elif k == 'ITOPS_DB_PORT': DB_PORT = v
        elif k == 'ITOPS_DB_NAME': DB_NAME = v
        elif k == 'ITOPS_DB_USER': DB_USER = v
        elif k == 'ITOPS_DB_PASSWORD': DB_PWD = v

url = f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

engine = create_engine(url, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

# 读取迁移 SQL
sql_path = Path('/home/zcxx/.hermes/projects/itops_platform/scripts/migration/013_asset_center.sql')
sql_content = sql_path.read_text()

# 分割并执行每条语句（跳过注释）
statements = []
current = []
for line in sql_content.splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith('--'):
        continue
    current.append(line)
    if stripped.endswith(';'):
        stmts = '\n'.join(current)
        # 分割多条语句
        for s in stmts.split(';'):
            s = s.strip()
            if s:
                statements.append(s)
        current = []

print(f"Found {len(statements)} SQL statements to execute")

# 执行
for i, stmt in enumerate(statements):
    if not stmt.strip():
        continue
    try:
        session.execute(text(stmt))
        session.commit()
        # 只打印前几行和表创建
        first_line = stmt.split('\n')[0][:80]
        print(f"  [{i+1}/{len(statements)}] OK: {first_line}")
    except Exception as e:
        session.rollback()
        err_str = str(e)
        if 'already exists' in err_str.lower() or 'duplicate' in err_str.lower():
            print(f"  [{i+1}/{len(statements)}] SKIP (already exists): {stmt.split(chr(10))[0][:60]}")
        else:
            print(f"  [{i+1}/{len(statements)}] ERROR: {e}")
            print(f"    SQL: {stmt[:200]}")

session.close()
print("\nMigration complete!")
