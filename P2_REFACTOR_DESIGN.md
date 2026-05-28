# ITOps Platform P2 重构设计文档

> 生成时间：2026-05-28
> 范围：前端 API 层重构 + 后端响应格式统一

---

## 一、问题优先级矩阵

| ID | 问题 | 严重度 | 影响范围 | 修复代价 | 是否重构 |
|----|------|--------|---------|---------|---------|
| F1 | 23个Vue页面使用 raw fetch()，绕过 auth interceptor | 🔴 致命 | 前端安全 | 高 | ✅ 已完成（39个文件迁移完成，0残留）|
| F2 | 67处直接调用 localStorage.getItem('token') | 🔴 高 | 前端可维护 | 中 | ✅ 已完成（request.js→store读token）|
| F3 | v-model:selected（Vue 3 反模式）| 🟡 低 | targets.vue | 低 | ✅ 已完成 |
| F4 | v-model:selected 存在于 targets.vue | 🟡 低 | 1个文件 | 低 | ✅ 已完成 |
| B1 | API 响应格式不统一（3种格式混用）| 🔴 高 | 后端全体 | 高 | ⚠️ 已定义PaginatedResponse但未强制使用 |
| B2 | DEBUG 模式 auth bypass 返回 dev 默认用户 | 🔴 安全 | 后端安全 | 中 | ✅ 已完成（SKIP_AUTH显式控制）|
| B3 | admin.py 70+端点单一文件 | 🟡 中 | admin路由 | 中 | 延后 |
| B4 | device_metrics/device_import 路由 prefix 缺失 | 🟢 低 | 2个路由 | 低 | ✅ 已完成 |
| P3-3 | 前端枚举硬编码散落，无统一常量文件 | 🟡 中 | 前端全体 | 低 | ✅ 已完成（新建enums.js）|

---

## 二、前端重构设计

### 2.1 API 层规范（强制）

**所有 API 调用必须通过 @/api 封装，禁止在 Vue 组件中直接使用 fetch() / axios。**

#### 规则 F1-RULE-001: API 模块结构

```
src/api/
  request.js          # axios 实例（唯一），包含 interceptor
  index.js            # 统一导出
  [domain].js        # 按领域划分：auth.js, monitoring.js, workorder.js, ...
```

**request.js 规范：**
```javascript
// 固定配置
baseURL: '/api/v1'
timeout: 30000
interceptor: 请求自动添加 Authorization: Bearer ${token}
// token 来源: localStorage.getItem('token') (唯一位置)
// ⚠️ 禁止在组件中再次读取 localStorage.getItem('token')
```

#### 规则 F1-RULE-002: API 函数命名规范

```
获取列表: getList(params)           → GET /{resource}
获取单个: getById(id)               → GET /{resource}/{id}
创建:     create(data)              → POST /{resource}
更新:     update(id, data)          → PUT /{resource}/{id}
删除:     delete(id)                → DELETE /{resource}/{id}
批量删除: batchDelete(ids)          → POST /{resource}/batch-delete
分页列表: getList({ page, page_size, ... })  → GET /{resource}?page=1&page_size=20
```

#### 规则 F1-RULE-003: API 返回值处理

**组件中调用 API 后，数据提取必须使用统一方式：**

```javascript
// ✅ 正确：统一数据提取模式
const res = await monitoring.device.getList(params)
const list = res?.data?.items || res?.data || res?.items || res || []

// ❌ 错误：每处写法不同
const list = response.data  // 假设 response.data 是 axios response
const list = response.items  // 假设 response 是已解包数据
```

**原因：** axios interceptor 返回 `response.data`，但某些 API 函数直接返回 `response`。统一 fallback 链解决。

#### 规则 F1-RULE-004: 迁移检查清单

迁移每个 Vue 文件时：
1. 删除顶部 `const API_BASE = '/api/v1'` 等常量
2. 删除 `import axios from 'axios'` 或 `import request from '@/api/request'`
3. 删除手动构造的 `Authorization: Bearer ${token}` header
4. 添加 `import { [domain] } from '@/api'`
5. 将 `fetch(url, { headers: {...} })` 替换为 `domain.functionName(params)`
6. 验证 token 自动注入（无手动 header 仍能访问受保护接口）

### 2.2 Token 管理规范

**规则 F2-RULE-001: Token 唯一来源**

```
token 获取位置（允许）：request.js interceptor
token 获取位置（禁止）：所有 .vue 和 .js 文件中直接调用 localStorage.getItem('token')
```

修复方案：在 useAuthStore 中封装 token getter：

```javascript
// src/stores/auth.js
export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  
  // 唯一合法的 token 读取出口
  function getToken() {
    return token.value
  }
  
  // ...
  return { token, getToken, ... }
})
```

request.js interceptor 改为从 store 获取：

```javascript
// request.js
import { useAuthStore } from '@/stores/auth'

axios.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})
```

### 2.3 待迁移文件清单（23个 raw fetch 文件）

按优先级分3批：

**第一批（关键 - 有敏感操作）:**
- `workorder/list.vue` — 创建/编辑/删除工单
- `workorder/detail.vue` — 工单详情
- `discovery/scan.vue` — 设备发现（已部分迁移）
- `automation/script.vue` — 脚本管理
- `automation/task.vue` — 任务管理
- `automation/execute.vue` — 执行自动化

**第二批（重要 - 数据展示）:**
- `system/dict.vue` — 字典管理
- `system/menu.vue` — 菜单管理
- `system/adapters.vue` — 适配器管理
- `notification/history.vue` — 消息历史
- `discovery/targets.vue` — 目标管理
- `backup/list.vue` — 备份列表
- `backup/restore.vue` — 备份恢复

**第三批（一般 - 页面框架）:**
- `ai/chat.vue` — AI聊天
- `ai/copilot.vue` — AI副驾驶
- `ai/analyze.vue` — AI分析
- `login/index.vue` — 登录页
- `dashboard/index.vue` — 仪表盘
- `discovery/index.vue` — 发现首页
- `automation/evaluate.vue` — 评估页
- `layout/index.vue` — 布局组件

### 2.4 v-model:selected 修复

```vue
<!-- ❌ 错误：Vue 3 中 el-table 没有 v-model:selected prop -->
<el-table v-model:selected="selectedRows">

<!-- ✅ 正确：el-table selection 通过 v-model:model-value 或直接绑定 -->
<el-table :data="tableData" @selection-change="handleSelectionChange">
  <el-table-column type="selection" />
</el-table>
```

修复文件：`discovery/targets.vue`（如果存在）

---

## 三、后端重构设计

### 3.1 API 响应格式统一

**B1-RULE-001: 统一响应包装器**

所有 API 响应必须使用以下三种格式之一：

```python
# 成功 - 分页列表
{
  "items": [...],
  "total": N,
  "page": 1,
  "page_size": 20
}

# 成功 - 单个对象
{
  "data": {...}
}

# 成功 - 简单状态
{
  "code": 0,
  "message": "success"
}
```

**实现方案：** 在 `api/dependencies.py` 中创建响应包装函数：

```python
# api/dependencies.py
def success_response(data=None, message="success", code=0):
    return {"code": code, "message": message, "data": data}

def paginated_response(items: list, total: int, page: int = 1, page_size: int = 20):
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

def single_response(data: dict):
    return {"data": data}
```

### 3.2 DEBUG Auth Bypass 修复

**B2-RULE-001: DEBUG 模式下强制使用真实认证**

```python
# api/dependencies.py
async def get_current_user(...) -> User:
    # DEBUG 模式下不再返回 dev 默认用户
    # 仅允许在 .env 中设置跳过认证的调试模式
    pass
```

具体修复：
- `get_current_user` 函数：移除 `if settings.DEBUG: return dev_user` 逻辑
- `verify_api_key` 函数：同上
- 仅允许 `.env` 环境变量 `SKIP_AUTH=true` 绕过（需显式设置）

### 3.3 路由 Prefix 规范化

检查 `api/main.py` 中所有路由注册，确保前缀一致：

```python
# 统一模式
app.include_router(xxx_router, prefix="/api/v1", tags=["功能模块"])
```

已确认 prefix 的路由：
- auth_router → /api/v1
- user_router → /api/v1
- system_router → /api/v1
- monitoring_router → /api/v1
- notification_router → /api/v1
- workorder_router → /api/v1
- ai_router → /api/v1
- automation_router → /api/v1
- device_router → /api/v1
- scheduler_router → /api/v1
- knowledge_router → /api/v1
- report_router → /api/v1
- collection_router → /api/v1
- scan_router → /api/v1
- stats_router → /api/v1
- device_metrics_router → /api/v1 ✅
- device_import_router → /api/v1 ✅
- adapters_router → /api/v1/admin ✅
- asset_router → /api/v1
- tenant_router → /api/v1
- dashboard_router → /api/v1

---

## 四、重构执行计划

### 阶段 1: 后端修复（不改架构，只修 Bug）
1. [ ] B2: DEBUG auth bypass 修复（高优先级）
2. [ ] B1: 创建统一响应包装器，应用于新增/修改的端点

### 阶段 2: 前端 API 迁移（按批次）
1. [ ] F2: 创建 auth store getter，修改 request.js 从 store 读 token
2. [ ] F1: 第一批 6 个文件迁移到 @/api
3. [ ] F1: 第二批 7 个文件迁移
4. [ ] F1: 第三批 8 个文件迁移
5. [ ] F3: 修复 targets.vue v-model:selected

### 阶段 3: 验证
1. [ ] 所有 53 个 Vue 页面 0 JS 错误
2. [ ] curl 测试关键接口
3. [ ] git commit + push

---

## 五、重构约束

1. **不停机原则**：重构过程中服务保持运行，验证通过后再提交
2. **每批验证**：每迁移完一批文件，立即在浏览器验证
3. **不回滚功能**：只修 API 调用方式，不改页面 UI/UX
4. **最小改动**：能通过改一行解决的，不改整个文件
5. **提交粒度**：每批文件迁移完成后单独 commit，便于回溯
