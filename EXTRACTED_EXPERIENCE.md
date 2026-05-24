# ITOps Platform 经验萃取文档

> 从 itops_platform (Docker旧架构) 和 itops-deploy (物理机部署) 两个废弃仓库中提炼的核心经验
> 
> 整理时间：2026-05-24

---

## 一、架构决策与踩坑记录

### 1. MySQL ENUM 与 Python 枚举的映射

**问题**：数据库 `device_type` 存 UPPERCASE MySQL ENUM（`'SERVER_LINUX'`），Python 枚举是 lowercase（`DeviceType.SERVER_LINUX`），直接写入导致 `DataError: Data truncated`。

**原则**：
- 所有 DB 写入：`.value.upper()` (Python → MySQL)
- 所有 DB 读取后 API 响应：`.lower()` (MySQL → API)
- 推荐使用 `StringEnum` TypeDecorator 彻底绕过 ENUM 验证问题

**涉及列**：`devices.device_type`、`devices.status`、`sop_documents.status`、`fault_cases.fault_level` 等。

---

### 2. Watermark 分隔符选择

**问题**：原始格式 `{action}:{resource}:{resource_id}:{operator}:{ts}:{hmac}`，资源ID含冒号时（如 `export:report:WO123`）split 产生 8 段而非 6 段。

**修复**：改用 `|` 分隔符，格式变为 `{action}|{resource}|{resource_id}|{operator}|{ts}:{hmac}`。

**原则**：选择不可能出现在数据内容中的字符作为分隔符（`|`、`\x00`、`|` 优于 `:`、`-`）。

---

### 3. Neo4j 6.x 事务模型变更

**问题**：Neo4j 6.x 后所有写操作必须通过 `session.execute_write(lambda tx: tx.run(...))` + `result.consume()` 显式提交，`session.run()` 不再自动提交事务。

**涉及驱动**：neo4j Python driver 6.2.0

**原则**：
```python
# 写操作（必须）
def create_node(self, label, properties):
    def _create(tx):
        result = tx.run("CREATE (n:$label) SET n += $props RETURN id(n)", label=label, props=properties)
        result.consume()  # 提交
    self.driver.session.execute_write(_create)

# 读操作（独立 session）
with self.driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n)")
```

---

### 4. SQLAlchemy Model 初始化顺序

**问题**：新增 Model 后服务不重启，`Base.metadata.create_all` 不会注册新表，导致 `Table 'xxx' doesn't exist`。

**原则**：新增 Model → 重启 uvicorn 服务。

---

### 5. 多 uvicorn 进程端口冲突

**问题**：多次重启后端口 8000 上有多个 uvicorn 进程，导致 API 响应不一致（一个进程写入 DB，另一个进程返回空）。

**原则**：
```bash
# 重启前先杀干净
kill $(lsof -ti:8000) 2>/dev/null; sleep 2
```

---

### 6. device_type 写入映射（完整链路）

**链路**：
```
API (device_type="server") 
  → _map_device_type() → DBDeviceType.SERVER_LINUX 
  → .value.upper() → "SERVER_LINUX" 
  → MySQL ENUM
```

**代码位置**：`api/routes/asset.py` create_device() + `modules/collection/device_manager.py`

---

### 7. CollectionStatus 枚举的 .value 陷阱

**问题**：`str(CollectionStatus.OFFLINE)` 返回 `'CollectionStatus.OFFLINE'`（类名+值），而非 `'OFFLINE'`。

**原则**：`CollectionStatus` 枚举必须用 `.value` 获取字符串值，不能直接 `str()`。

---

### 8. LLM 连接配置

- ollama 默认端口 **11434**（不是 11435）
- `LLMClient()` 无参数调用返回 `llm_client = None`，调用前必须检查
- `chat()` 接收 `List[Dict]`（消息列表），不是字符串 prompt

---

## 二、物理机部署要点

### 系统依赖

| 依赖 | 版本 | 安装方式 |
|------|------|---------|
| Python | 3.10+ | anaconda 或系统自带 |
| Node.js | 18.x | apt |
| MySQL | 8.0 | apt |
| Nginx | 最新 | apt |
| Redis | 最新 | apt |

### 服务启动方式

```bash
# 后端（anaconda 环境）
/home/zcxx/anaconda3/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 前端：Nginx 反向代理 80/443 → 8000
# 静态文件：/opt/itops_platform/frontend/dist
```

### systemd 服务注册

```ini
[Unit]
Description=ITOps Platform API
After=network.target mysql.service

[Service]
Type=simple
User=zcxx
WorkingDirectory=/home/zcxx/.hermes/projects/itops_platform
ExecStart=/home/zcxx/anaconda3/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 三、调试方法论

### FastAPI 503 错误根因定位

503 "数据库不可用" 最常见原因：
1. **Pydantic 验证错误**：被 `except Exception` 吞掉，返回误导性 503
2. **SQLAlchemy Session 问题**：`session_scope` 内异常未回滚
3. **MySQL ENUM 不匹配**：写入值不在枚举定义中

**调试命令**：
```bash
# 查 API 日志
tail -f /tmp/itops_api.log

# 直接测试 Python driver
/home/zcxx/anaconda3/bin/python -c "
from modules.collection.device_manager import DeviceManager
dm = DeviceManager()
print(dm.list_devices())
"
```

### Neo4j 连接问题

```bash
# 验证 Neo4j 是否运行
curl http://localhost:7474/

# 验证 bolt 端口
/home/zcxx/anaconda3/bin/python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','Admin@123456'))
driver.verify_connectivity()
print('Neo4j OK')
"
```

---

## 四、知识库种子数据经验

10个 SOP + 7个故障案例 + 10个分类 + 27个标签覆盖常见运维场景。

**SOP 分类示例**：网络故障、服务器异常、数据库问题、安全事件、存储扩容、DNS故障、性能优化

**故障案例字段**：title、description、root_cause、solution、fault_level（critical/major/minor/warning）、fault_status

---

## 五、API 路由设计原则

1. **前缀统一**：所有路由挂载在 `/api/v1/{module}` 下
2. **Router 自带前缀**：`main.py` include 时不再额外加 prefix
3. **异常处理**：在 `dependencies.py` 的 `get_db` 中，`except (HTTPException, RequestValidationError)` 必须 re-raise
4. **user_id 类型**：admin 端点 user_id 是 str（`'u001'`），不是 int

---

## 六、已验证的架构能力（代码存在但旧版 GAP 漏标）

| 模块 | 能力 | 位置 |
|------|------|------|
| monitoring | 告警屏蔽 | `POST /alerts/{id}/suppress` (monitoring.py:1300) |
| monitoring | 告警升级定时任务 | `alerter.py:561-746` AlertTrigger._escalation_loop() |
| config | 配置热更新 | `core/config/manager.py` ConfigManager.start_watching() |
| workorder | 工单草稿保存 | `WorkOrderDraftManager` (modules/business/workorder/draft_manager.py) |
| deploy | 自动回滚 | `RollbackManager` (rollback.py:524行) |
| discovery | ARP 主动扫描 | `ARPScanner` (scanner.py) |
| ldap | LDAP SSO | `POST /ldap-login` (auth.py:496-646) |
