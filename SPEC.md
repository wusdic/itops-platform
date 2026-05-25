# ITOps Platform 技术规范 (SPEC)

> 本文件是 ITOps Platform 项目的**唯一技术规范来源**。
> 所有代码必须符合本规范；所有新增功能必须先更新本规范再实现。
> 本规范采用**追加模式**演进：新问题 → 讨论决策 → 写入规范 → 按规范执行。

---

## 1. 设备数据模型规范

### 1.1 模型职责边界（不可打破）

| 模型 | 文件 | 职责 | 生命周期 |
|---|---|---|---|
| `Device` | `modules/foundation/db_models/device.py` | MySQL 持久化 ORM | 永久存储 |
| `DiscoveredHost` | `modules/collection/discovery/scanner.py` | 扫描发现的运行时数据 | 内存/扫描会话 |
| `DeviceImporter` | `modules/business/device_importer.py` | Excel/CSV 批量导入，构造 Device | 一次性导入 |
| `DeviceManager` | `modules/collection/device_manager.py` | 采集层协调，读写 Device | 运行时 |

**原则：`DiscoveredHost` 是发现层的临时对象，`Device` 是持久化对象，二者转换必须经过明确的映射函数，不得相互侵入。**

### 1.2 `Device` 模型规范

```python
# modules/foundation/db_models/device.py

class DeviceStatus(str, Enum):
    """设备状态枚举 —— 必须与 MySQL ENUM 值一一对应（全大写）"""
    ONLINE = "online"          # 正常
    OFFLINE = "offline"        # 离线
    WARNING = "warning"        # 警告
    CRITICAL = "critical"      # 严重
    MAINTENANCE = "maintenance"# 维护中
    UNKNOWN = "unknown"        # 未知

class DeviceType(str, Enum):
    """设备类型枚举"""
    SERVER_WINDOWS = 'server_windows'
    SERVER_LINUX = 'server_linux'
    # ... 其他类型见 device.py

class Device(Base):
    # status 列：必须写入 .value（字符串 "online"），由 ORM 映射到 MySQL ENUM
    status = Column(String(50), default='unknown', comment='状态')

    # device_type 列：必须写入 .value（字符串 "server_linux"）
    device_type = Column(String(50), nullable=False, index=True, comment='设备类型')
```

**规则 D-1：`Device.status` 写入时必须使用 `DeviceStatus` 枚举的 `.value`（小写字符串），不得硬编码字符串。**

**规则 D-2：`Device.device_type` 写入时必须使用 `DeviceType` 枚举的 `.value`（小写字符串），不得硬编码字符串。**

**规则 D-3：`DeviceImporter` 和 `DeviceManager` 在创建/更新 `Device` 时，必须使用 `DeviceStatus` 枚举，不得混用其他枚举或裸字符串。**

### 1.3 `DiscoveredHost` 模型规范

```python
# modules/collection/discovery/scanner.py

class OSType(str, Enum):
    """操作系统类型（发现层）"""
    WINDOWS = "windows"
    LINUX = "linux"
    UNIX = "unix"
    NETWORK = "network"
    UNKNOWN = "unknown"

@dataclass
class DiscoveredHost:
    """发现的 Host（扫描层临时对象）"""
    ip: str
    os_type: OSType = OSType.UNKNOWN   # 操作系统类型，不是设备类型
    status: str = "unknown"            # "up" | "down"，不是 DeviceStatus
```

**规则 D-4：`DiscoveredHost` 是扫描层内部模型，其 `status` 字段含义为 "up/down"（可达性），与 `DeviceStatus` 是不同概念，不得混淆。**

**规则 D-5：`DiscoveredHost` 到 `Device` 的转换必须在 `DeviceImporter` 中显式完成，映射关系由 `OSType → DeviceType` 映射表显式定义。**

### 1.4 状态枚举统一（Critical）

```python
# modules/collection/device_manager.py

# ✅ 正确：删除别名，统一使用 DeviceStatus
class DeviceStatus(str, Enum):
    """设备状态 —— 覆盖采集层和设备层"""
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    COLLECTING = "collecting"

# ❌ 错误：禁止使用别名
# DeviceStatus = CollectionStatus  # 已删除
```

**规则 D-6：禁止使用 `CollectionStatus` 作为别名，必须统一使用 `DeviceStatus`。所有层（采集层、API 层、导入层）共用同一个 `DeviceStatus` 枚举。**

**规则 D-7：`DeviceStatus` 枚举值统一为**小写字符串**（`.value`），MySQL ENUM 列在数据库层统一存储大写（由 MySQL 的 `LOWERCASE()` 或应用层统一 `.upper()` 处理），但**应用层 Python 代码始终使用小写**。**

---

## 2. MySQL Schema 规范

### 2.1 ENUM 列规范

```sql
-- devices.status 列
status ENUM('ONLINE','OFFLINE','WARNING','CRITICAL','MAINTENANCE','UNKNOWN')
  DEFAULT 'UNKNOWN'  -- 大写存储

-- devices.device_type 列（建议，避免 String 列失控增长）
device_type ENUM(
  'SERVER_WINDOWS','SERVER_LINUX','SERVER_VMWARE','SERVER_HYPERV','SERVER_KVM',
  'NETWORK_SWITCH','NETWORK_ROUTER','NETWORK_FIREWALL','NETWORK_WAF',
  'NETWORK_LB','NETWORK_VPN','NETWORK_AP','NETWORK_AC',
  'SECURITY_IDS','SECURITY_IPS','SECURITY_AMS',
  'STORAGE_ARRAY','STORAGE_NAS','STORAGE_TAPE',
  'OTHER'
)
```

**规则 S-1：MySQL ENUM 列存储**大写**值。**

**规则 S-2：Python 应用层（SQLAlchemy `Device` 模型）写入前必须确保值为**小写**字符串（对应枚举 `.value`），由 SQLAlchemy 的 EnumType 或 MySQL 的 `LOWERCASE` 策略处理大小写映射。**

**规则 S-3：所有写入 `devices.status` 的代码路径（导入、采集、定时任务）必须经过 `DeviceStatus` 枚举，禁止裸字符串写入。**

### 2.2 外键与分片表约束

> 参见 `modules/foundation/sharding.py` 的 `_remove_foreign_keys` 方法。
> 分片表（`alerts`、`work_orders`）因复杂 FK 约束无法创建外键，需要应用层约束。

**规则 S-4：新增分片表时，必须显式移除所有外键约束（通过 `_remove_foreign_keys`），并在文档中注明应用层如何保证引用完整性。**

---

## 3. API 设计规范

### 3.1 路由前缀

```
/api/v1/auth/        -- 认证
/api/v1/assets/      -- 资产管理
/api/v1/discovery/   -- 网络发现
/api/v1/monitoring/  -- 监控
/api/v1/admin/       -- 系统管理（菜单、字典、用户）
/api/v1/notification/ -- 通知
/api/v1/automation/  -- 自动化
/api/v1/ai/          -- AI 能力
```

**规则 A-1：API 路由前缀必须严格遵循上述规范。前端调用必须使用正确的后端已有路径，不得自行发明路径。**

### 3.2 响应格式

```json
// 成功
{"code": 0, "message": "success", "data": {...}}

// 失败
{"code": 非0, "message": "错误描述", "data": null}
```

**规则 A-2：所有 API 响应必须符合上述格式，`data` 字段在成功时为对象/数组，失败时为 `null`。**

### 3.3 异常处理

```python
# api/main.py 异常处理层次
1. FastAPI 内置异常（如 404, 422）  -- FastAPI 自动处理
2. 自定义异常（如 ResourceNotFound）  -- @app.exception_handler 注册
3. validation_exception_handler       -- 处理 Pydantic 验证错误
4. generic_exception_handler           -- 兜底，所有未处理异常
```

**规则 A-3：`validation_exception_handler` 内部不得再抛出异常。如果 `exc.errors()` 返回非 JSON 可序列化对象，必须先做 `str()` 转换。**

---

## 4. 前端-后端契约规范

### 4.1 字段命名

- **Python 后端**：snake_case（`ip_address`, `device_type`）
- **前端 Vue**：camelCase（`ipAddress`, `deviceType`）
- **API 传输**：snake_case（JSON 标准）

**规则 F-1：前端与后端通信使用 snake_case JSON。前端内部组件通信可自行决定，但 API 请求/响应必须严格 snake_case。**

### 4.2 前端 API 路径必须与后端路由完全一致

**规则 F-2：前端 `src/api/*.js` 中的所有路径，必须与后端 `api/routes/*.py` 中的路由 prefix + path 完全一致。在添加新 API 时，必须先确认后端已有该路由。**

### 4.3 Naive UI DataTable 远程分页

> 已知 bug：Naive UI `n-data-table` 远程分页只显示第 1 页。
> 根因：`Object.assign` 破坏响应式，导致 `pagination.page` 未更新。

**规则 F-3：使用 `n-data-table` 远程分页时，必须在 `onLoad` 中用 `nextTick(() => { pagination.page = res.data.page })` 强制同步页码。参见 `skills/naive-ui-remote-pagination-workaround`。**

---

## 5. 服务生命周期规范

### 5.1 API 服务启动

```
启动命令：uvicorn api.main:app --host 0.0.0.0 --port 8000
初始化：所有初始化（DB/Redis/AI/后台任务）必须放在 api/main.py 的 @asynccontextmanager lifespan() 中
```

**规则 L-1：`api/start.py` 的 `main()` 函数从不被调用。所有初始化逻辑必须放在 `api/main.py` 的 `lifespan()` 中。Shutdown 逻辑也在 `lifespan` 的 finally 部分。**

### 5.2 重启后等待

```
服务重启后需等待 ~10s 才能响应。
请求失败很常见不一定是 bug，应等待 10s 后重试。
```

**规则 L-2：所有健康检查和功能验证，必须在服务启动后等待至少 10 秒再进行。**

---

## 6. 日志规范

### 6.1 日志归集层

> 已知问题：`api/middleware/request_id.py` 的中间件只写 `operation_logs`，从不写 `log_group` 表。
> 参见 `skills/itops-platform-log-architecture-fix`。

**规则 G-1：所有日志写入必须使用 `logger = logging.getLogger(__name__)`，禁止直接 `print()`。生产环境日志通过 `operation_logs` 表归集。**

---

## 7. 设备状态写入路径（强制）

以下是所有已知的写入 `devices.status` 的代码路径，任何新增路径必须遵守本规范：

### 路径 A：DeviceImporter 导入（一次性）

```python
# modules/business/device_importer.py
from modules.foundation.db_models.device import Device, DeviceStatus

device = Device(
    status=DeviceStatus.UNKNOWN,  # ✅ 正确：枚举 .value
)
```

### 路径 B：DeviceManager 采集（定时）

```python
# modules/collection/device_manager.py
from modules.foundation.db_models.device import DeviceStatus

# 映射关系
status_mapping = {
    DeviceStatus.ONLINE: DeviceStatus.ONLINE,
    DeviceStatus.OFFLINE: DeviceStatus.OFFLINE,
    DeviceStatus.ERROR: DeviceStatus.WARNING,
    DeviceStatus.UNKNOWN: DeviceStatus.UNKNOWN,
    DeviceStatus.COLLECTING: DeviceStatus.UNKNOWN,
}
device.status = str(db_status.value).lower()  # ✅ 正确：统一小写
```

### 路径 C：API 路由直接更新

```python
# api/routes/asset.py
from modules.foundation.db_models.device import DeviceStatus

device.status = DeviceStatus.ONLINE  # ✅ 正确
```

**规则 W-1：所有写入 `Device.status` 的路径必须使用 `DeviceStatus` 枚举的 `.value`（小写字符串）。禁止直接赋值裸字符串。**

---

## 8. 规范演进流程

当遇到本规范未覆盖的新情况时：

1. **讨论**：在对话中说明新情况
2. **决策**：确定解决方案
3. **写入**：将决策结果追加到 `SPEC.md` 对应章节
4. **执行**：按新规范实现

**本规范采用追加模式，不删除已有规则，只补充例外和细化条款。**

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|---|---|---|
| v1.0 | 2026-05-25 | 初始版本：设备数据模型规范（Device/DiscoveredHost/Importer/Manager）、MySQL Schema 规范、API 设计规范、前端契约、服务生命周期、日志规范、设备状态写入路径 |
