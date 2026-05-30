# ITOps Platform 前端用户体验工作流

> 文档状态：current
> 版本：v1.0
> 基于：Phase 10 前端实现（`frontend/src/features/`）
> 最后更新：2026-05-30

---

## 1. 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 框架 | Vue 3 + Composition API | `<script setup>` 语法 |
| 构建 | Vite 4 | 开发服务器 + 生产构建 |
| 组件库 | Element Plus + Naive UI | Element Plus 为主，Phase 10 新页面用 Element Plus |
| 状态管理 | Pinia | 全局状态 |
| HTTP | Axios + `src/api/request.js` | 统一封装，baseURL: `/api/v1` |
| 路由 | Vue Router | 前端路由 |
| 图表 | ECharts | 指标图表 |

---

## 2. 目录结构

```
frontend/src/
├── features/              # Phase 10 新建，按运维流程组织
│   ├── command-center/       运维指挥台
│   ├── incident-response/    故障处置台
│   ├── automation-orchestration/  自动化编排台
│   ├── monitoring-event/     监控与事件台
│   └── asset-config/        资产与配置台
├── views/                # 旧页面（日常运维）
│   ├── layout/
│   ├── dashboard/
│   ├── monitoring/
│   ├── workorder/
│   ├── knowledge/
│   ├── automation/
│   └── system/
├── api/                 # API 调用封装
│   ├── request.js          Axios 实例
│   ├── notification.js     通知 API
│   ├── monitoring.js        监控 API
│   └── ...
├── stores/              # Pinia store
└── router/
    └── index.js           路由配置
```

---

## 3. 核心用户工作流

### 3.1 故障发现 → 处置 → 关闭（核心闭环）

```
[运维指挥台 /command-center]
    │  查看严重告警列表 + AI 建议
    ↓
[故障处置台 /incident-response]
    │  选择告警 → 时间线展开
    │  证据分析 Tab（关联事件 / 关联日志 / 关联资产）
    │  AI 分析按钮 → 根因 + 推荐动作
    ↓
[自动化编排台 /automation-orchestration]
    │  选择剧本 → dry-run → 审批（如需）→ 执行
    │  SSE 实时日志 → 执行结果验证
    ↓
[故障处置台] 关闭告警 + 沉淀知识
```

### 3.2 告警生命周期

```
告警生成（采集器/规则）
    ↓
[监控与事件台 /monitoring-event] 告警列表
    ↓
确认（acknowledge） → 处理中（processing） → 解决/关闭（resolve/close）
    │
    ├─ 触发自动化 → 执行 → 验证
    ├─ AI 分析 → 根因 + 修复建议
    └─ 转工单（transfer）→ 工单管理
```

### 3.3 资产生命周期

```
[资产与配置台 /asset-config]
    │  新建资产 / 资产列表
    │  绑定凭证 / 绑定采集模板 / 绑定策略
    ↓
[监控与事件台] 采集指标 → 状态变化触发事件
    ↓
[运维指挥台] 实时状态监控
```

---

## 4. 页面清单

### 4.1 Phase 10 新页面（`features/`）

| 页面 | 路径 | 核心功能 |
|---|---|---|
| 运维指挥台 | `/command-center` | 严重告警排行、AI建议摘要、自动化任务状态、设备采集成功率 |
| 故障处置台 | `/incident-response` | 时间线、证据分析（事件/日志/资产Tab）、AI分析按钮、实时日志SSE |
| 自动化编排台 | `/automation-orchestration` | 剧本库、任务管理、执行历史、审批中心 |
| 监控与事件台 | `/monitoring-event` | 指标监控、日志检索、事件流、告警中心、告警规则 |
| 资产与配置台 | `/asset-config` | 资产列表、凭证管理、配置管理 |

### 4.2 旧页面（`views/`）

| 目录 | 页面 | 说明 |
|---|---|---|
| dashboard | `index.vue` | 仪表盘 |
| monitoring | `devices.vue` | 设备监控 |
| monitoring | `alerts.vue` | 告警管理 |
| monitoring | `logs.vue` | 日志管理 |
| workorder | `list.vue` | 工单列表 |
| workorder | `my.vue` | 我的工单 |
| knowledge | `list.vue` | 知识库 |
| automation | `list.vue` | 自动化脚本 |
| system | `users.vue` | 用户管理 |
| system | `roles.vue` | 角色管理 |
| system | `config.vue` | 系统配置 |

---

## 5. API 对接规范

### 5.1 Axios 实例

```javascript
// src/api/request.js
const service = axios.create({
  baseURL: '/api/v1',  // Vite 代理到后端
  timeout: 30000,
})
```

### 5.2 认证 Token 处理

```javascript
// 请求拦截器：注入 Token
service.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：统一错误处理
service.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 5.3 API 函数命名规范

```javascript
// GOOD
export const getAlerts = (params) => request({ url: '/alerts', method: 'get', params })
export const createAlert = (data) => request({ url: '/alerts', method: 'post', data })

// BAD
export function fetchAlertList() { ... }
```

---

## 6. 组件使用规范

### 6.1 表格（Element Plus）

```vue
<el-table :data="tableData" v-loading="loading">
  <el-table-column prop="name" label="名称" />
  <el-table-column label="操作">
    <template #default="{ row }">
      <el-button type="primary" @click="handleEdit(row)">编辑</el-button>
    </template>
  </el-table-column>
</el-table>
```

### 6.2 分页

```vue
<el-pagination
  v-model:current-page="page"
  v-model:page-size="pageSize"
  :total="total"
  layout="total, prev, pager, next"
  @current-change="fetchData"
/>
```

---

## 7. SSE / WebSocket 使用

```javascript
// 自动化执行实时日志
const eventSource = new EventSource(`/api/v1/automation/executions/${id}/stream`)

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'log') appendLog(data.content)
  if (data.type === 'done') {
    eventSource.close()
    fetchResult()
  }
}

eventSource.onerror = () => {
  eventSource.close()
}
```

---

## 8. 路由守卫

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})
```

---

## 9. 开发规范

- **组件库**：优先使用 Element Plus（Phase 10 新页面统一使用）
- **样式**：使用 Element Plus 主题变量，支持深色模式
- **图表**：使用 ECharts，放在 `<div ref="chartRef">` 容器中
- **状态管理**：页面级状态用 `ref/reactive`，全局状态用 Pinia store
- **API 错误处理**：禁止 `.catch(() => {})` 静默吞错，至少要 `console.error` 或显示 toast
