# 日志系统设计方案

## 一、现状问题

| 日志类型 | 频率 | 单条信息量 | 主要问题 |
|----------|------|-----------|----------|
| 操作日志 | 每API请求 | 1条 | 中等，但无过滤 |
| 系统日志 | 非常高 | 巨大 | `DEBUG`/`INFO` 铺天盖地，文件几百MB |
| 采集日志 | 每设备每采集周期 | 很大 | 按设备聚合前，28台设备每分钟即可产生数百条 |
| 告警审计 | 告警状态变更时 | 1条 | 量少，但混在普通日志里找不到 |

**核心矛盾**：用户需要看到有意义的操作记录，但系统日志和采集日志的海量数据完全淹没了有用信息。

---

## 二、设计目标

1. **配置化**：用户决定哪些日志类型要记录，持久化到数据库
2. **分级显示**：默认只看高价值的操作日志，系统/采集日志默认折叠
3. **归集展示**：同一类型多条日志归集成一个条目，带计数和摘要
4. **二级展开**：归集条目点开后显示子列表，子列表可展开查看详情
5. **自动清理**：日志按策略自动过期删除，不过占用数据库

---

## 三、日志分类与默认配置

### 3.1 分类定义

```
操作日志 (operation)
  - login/logout        → 登录登出 ★ 默认开启
  - device CRUD         → 设备增删改查 ★ 默认开启
  - alert 状态变更       → 告警产生/确认/解决 ★ 默认开启
  - workorder CRUD      → 工单增删改   ★ 默认开启
  - adapter/credential  → 适配器/凭证  ● 默认关闭（专业用户）

系统日志 (system)
  - ERROR/CRITICAL     → 系统错误 ★ 默认开启（仅ERROR+，按需开启INFO）
  - WARNING            → 警告信息 ★ 默认开启 WARNING+
  - INFO               → 一般信息 ● 默认关闭（运维调试用）
  - DEBUG              → 调试信息 ● 默认关闭（开发调试用）

采集日志 (collection)
  - success            → 采集成功 ● 默认关闭（量大，运维不需要每条都看）
  - failed             → 采集失败 ★ 默认开启
  - offline            → 设备离线 ★ 默认开启

告警审计 (audit)
  - 所有操作           → ★ 默认开启
```

★ = 默认开启（默认选中）  ● = 默认关闭

### 3.2 归集策略

| 维度 | 归集规则 | 展示内容 |
|------|----------|----------|
| 操作日志 | action + resource + 10分钟时间桶 | 计数、涉及资源、代表性IP、时间范围 |
| 系统日志 | level + source + 5分钟时间桶 | 计数、级别分布、时间范围 |
| 采集日志 | status + device + 采集批次 | 计数、成功/失败比例、涉及设备数 |
| 告警审计 | action + alert_id | 计数、涉及告警、时间范围 |

---

## 四、数据库设计

### 4.1 日志配置表 (log_config)

```sql
CREATE TABLE log_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(32) NOT NULL,    -- 'operation'|'system'|'collection'|'audit'
    sub_category VARCHAR(64),          -- 'login'|'device_crud'|'error'|'success'|...
    enabled BOOLEAN DEFAULT 1,          -- 是否记录
    level VARCHAR(16),                 -- 最低记录级别 (DEBUG/INFO/WARNING/ERROR)
    aggregation_enabled BOOLEAN DEFAULT 1,  -- 是否启用归集
    aggregation_key VARCHAR(128),      -- 归集维度字段（JSON字符串）
    retention_days INTEGER DEFAULT 7,  -- 保留天数
    description VARCHAR(256),           -- 中文说明
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, sub_category)
);
```

### 4.2 日志归集表 (log_groups)

```sql
CREATE TABLE log_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(32) NOT NULL,
    group_key VARCHAR(256) NOT NULL,  -- 归集唯一标识 (hash of dimensions)
    dimension_summary TEXT,            -- JSON: {action: 'login', count: 42, ...}
    first_seen DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,
    total_count INTEGER DEFAULT 0,
    level_distribution TEXT,           -- JSON: {ERROR: 3, WARNING: 10}
    sample_log TEXT,                  -- 一条代表性日志的原文
    is_expanded BOOLEAN DEFAULT 0,    -- 前端展开状态（不持久化）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category_key (category, group_key),
    INDEX idx_last_seen (last_seen)
);
```

### 4.3 日志明细表 (log_items)

```sql
CREATE TABLE log_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER REFERENCES log_groups(id) ON DELETE CASCADE,
    category VARCHAR(32) NOT NULL,
    raw_content TEXT NOT NULL,         -- 原始日志全文
    level VARCHAR(16),
    source VARCHAR(64),
    message TEXT,
    detail TEXT,                      -- 结构化的详情字段（JSON）
    duration_ms INTEGER,               -- 耗时（操作日志）
    username VARCHAR(64),              -- 操作人
    ip_address VARCHAR(64),            -- 客户端IP
    resource_type VARCHAR(64),         -- 资源类型
    resource_id VARCHAR(64),           -- 资源ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_group (group_id),
    INDEX idx_category_created (category, created_at)
);
```

---

## 五、API 设计

### 5.1 配置管理

| Method | Endpoint | 说明 |
|--------|----------|------|
| GET | `/api/v1/admin/logs/config` | 获取所有日志配置 |
| PUT | `/api/v1/admin/logs/config` | 批量更新配置 |
| GET | `/api/v1/admin/logs/stats` | 各分类的实时统计（当日条数、归集数） |

### 5.2 日志查询

| Method | Endpoint | 说明 |
|--------|----------|------|
| GET | `/api/v1/admin/logs/groups` | 获取归集日志列表（支持分页） |
| GET | `/api/v1/admin/logs/groups/{group_id}/items` | 获取某归集下的明细列表 |
| GET | `/api/v1/admin/logs/items/{id}` | 获取单条明细（完整内容） |
| GET | `/api/v1/admin/logs/export` | 导出CSV/JSON |

### 5.3 归集查询参数

```
GET /api/v1/admin/logs/groups?category=operation&level=ERROR&keyword=登录&start_date=2026-05-01&end_date=2026-05-21&page=1&page_size=20&expand=1
```

### 5.4 自动清理

| Method | Endpoint | 说明 |
|--------|----------|------|
| DELETE | `/api/v1/admin/logs/cleanup` | 手动触发清理（按保留天数） |
| (定时任务) | 每日凌晨3点执行 | 自动清理过期数据 |

---

## 六、前端页面设计

### 6.1 页面布局

```
日志中心
├── [Tab: 操作日志] [Tab: 系统日志] [Tab: 采集日志] [Tab: 告警审计] [Tab: ⚙ 配置]
├── 顶部工具栏
│   ├── 分类筛选 (多选)
│   ├── 关键字搜索
│   ├── 日期范围
│   ├── 级别筛选
│   └── [导出] [清空] [刷新]
└── 日志列表（归集模式）
    ├── ▼ 2026-05-21 14:00 - 14:10  登录操作 [42条]  [admin, zcxx, ...]
    │   └── [展开] 查看明细
    └── 日志明细（二级）
        ├── 14:02:31 admin 登录成功  192.168.1.100  耗时: 234ms
        ├── 14:05:17 zcxx 登录成功  192.168.1.101  耗时: 189ms
        └── ...
```

### 6.2 配置面板

```
⚙ 日志配置

操作日志
  [✓] 登录/登出    (login/logout)            每次登录登出记录
  [✓] 设备管理    (device CRUD)              设备增删改查记录
  [✓] 告警操作    (alert actions)            告警状态变更记录
  [✓] 工单管理    (workorder CRUD)           工单增删改记录
  [ ] 适配器/凭证  (adapter/credential)       适配器和凭证变更记录

系统日志
  [✓] ERROR 及以上   记录系统错误和严重问题
  [✓] WARNING        记录警告信息
  [ ] INFO           记录一般信息（量大）
  [ ] DEBUG          记录调试信息（最大量）

采集日志
  [ ] 采集成功      (success)                 每次成功采集记录（量大）
  [✓] 采集失败      (failed)                  采集失败时记录
  [✓] 设备离线      (offline)                 设备离线时记录

告警审计
  [✓] 全部告警操作  (create/update/delete/acknowledge/resolve)

保留策略: [7] 天  [批量更新] [保存配置]
```

---

## 七、实现计划

### Phase 1: 数据库和配置层
1. 创建 `log_config`、`log_groups`、`log_items` 表
2. 创建 `LogConfigService` 管理配置（CRUD + 持久化）
3. 实现默认配置初始化逻辑
4. 实现日志写入拦截和归集逻辑

### Phase 2: 后端 API
1. 重构 `GET /api/v1/admin/logs` → 归集查询
2. 新增 `GET /api/v1/admin/logs/groups/{id}/items`
3. 新增 `GET/PUT /api/v1/admin/logs/config`
4. 新增 `GET /api/v1/admin/logs/stats`
5. 实现日志清理定时任务

### Phase 3: 前端页面
1. 重构 `logs.vue` — 归集列表 + 二级展开
2. 新建 `LogConfig.vue` — 配置面板
3. 集成到系统管理菜单

### Phase 4: 优化
1. 操作日志中间件改造 — 按配置决定是否记录
2. 采集日志写入改造 — 按配置决定是否归集
3. 实时统计（当日条数、归集数）
4. 导出功能
