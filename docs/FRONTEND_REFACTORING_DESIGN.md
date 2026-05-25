# ITOps Platform 前端全量重构设计文档

> 版本：v1.1.0
> 日期：2026-05-25
> 目标：全量迁移 naive-ui → Element Plus，建立 UI 封装层，实现一步到位的前端现代化

---

## 0. 前端问题清单与开发方案（2026-05-25）

> ⚠️ **前置说明**：以下问题经逐条验证确认，**全部属于前端问题**，后端 API 均已就绪（200 OK）。开发顺序按优先级排列。

### 0.1 问题汇总

| # | 问题文件 | 问题描述 | 优先级 | 对应后端 |
|---|---------|---------|--------|---------|
| F1 | `discovery/scan.vue` | 调用 `GET /api/v1/discovery/scan`，但后端只有 POST，需改为对接 `/discovery/ip/scan` 或 `/discovery/snmp/scan` | P1 | `/api/v1/discovery/ip/scan` (POST) ✅ |
| F2 | `workorder/create.vue` | 136行，仅有基础表单骨架，缺少分类选择、优先级、SLA 等核心字段；`POST /api/v1/workorders/` 需适配 | P1 | `/api/v1/workorders/` ✅ |
| F3 | `dashboard/index.vue` | 766行硬编码静态布局，需改为调用 `GET /api/v1/monitoring/dashboard/layout` 动态加载 | P1 | `/api/v1/monitoring/dashboard/layout` (GET/PUT) ✅ |
| F4 | `monitoring/devices.vue` | 16行占位页，无设备列表；需对接 `/api/v1/assets/device` 或 `/api/v1/devices` | P1 | `/api/v1/assets/device` ✅ |
| F5 | `monitoring/alerts.vue` | 需验证是否对接 `GET /api/v1/monitoring/alerts` | P1 | `/api/v1/monitoring/alerts` ✅ |
| F6 | `automation/script.vue` | 需验证 CRUD 是否完全对接后端 scripts API（GET/POST/PUT/DELETE/versions/execute） | P1 | scripts CRUD + execute ✅ |
| F7 | `automation/task.vue` | 需验证任务创建/运行是否对接 `POST /api/v1/automation/tasks` 和 `POST .../tasks/{id}/run` | P1 | tasks + run ✅ |
| F8 | `workorder/list.vue` | 需验证列表分页和筛选是否正确对接 `/api/v1/workorders/`（注意尾部斜杠敏感） | P1 | `/api/v1/workorders/` ✅ |
| F9 | `workorder/my.vue` | 需验证是否对接 `/api/v1/workorders/` 带 `creator_id` 参数筛选 | P1 | `/api/v1/workorders/` ✅ |
| F10 | `system/user.vue` | 188行直接用 fetch，API 路径需全面审查是否对齐 `/api/v1/admin/users` | P1 | `/api/v1/admin/users` ✅ |
| F11 | `system/role.vue` | 需验证角色 CRUD 是否对接 `/api/v1/admin/roles` | P1 | `/api/v1/admin/roles` ✅ |
| F12 | `system/menu.vue` | 需验证菜单管理是否对接 `/api/v1/admin/menu` 和 `/api/v1/system/menus` | P1 | `/api/v1/admin/menu` + `/api/v1/system/menus` ✅ |
| F13 | `notification/message.vue` | 220行，需验证消息列表/已读/删除是否对接 `/api/v1/notifications/messages` | P1 | `/api/v1/notifications/messages` ✅ |
| F14 | `notification/history.vue` | 214行，需验证通知历史是否对接 `/api/v1/notifications/history` | P1 | `/api/v1/notifications/history` ✅ |
| F15 | `notification/config.vue` | 175行，需验证渠道配置是否对接 `/api/v1/notifications/channels` | P1 | `/api/v1/notifications/channels` ✅ |
| F16 | `backup/list.vue` | 307行，需验证备份列表是否对接 `/api/v1/admin/backups` | P1 | `/api/v1/admin/backups` ✅ |
| F17 | `backup/restore.vue` | 218行，需验证恢复操作是否对接 `/api/v1/admin/backups/{id}/restore` | P1 | `/api/v1/admin/backups/{id}/restore` ✅ |
| F18 | `report/list.vue` | 需验证报表列表是否对接 `/api/v1/reports/list` | P1 | `/api/v1/reports/list` ✅ |
| F19 | `report/create.vue` | 需验证报表创建是否对接 `/api/v1/reports/generate` | P1 | `/api/v1/reports/generate` ✅ |
| F20 | `report/template.vue` | 485行，需验证模板管理是否对接 `/api/v1/reports/template` | P1 | `/api/v1/reports/template` ✅ |
| F21 | `knowledge/list.vue` | 439行，需验证知识库列表是否对接 `/api/v1/knowledge/search` | P1 | `/api/v1/knowledge/search` ✅ |
| F22 | `knowledge/cases.vue` | 188行，需验证故障案例是否对接 `/api/v1/knowledge/fault-case` | P1 | `/api/v1/knowledge/fault-case` ✅ |
| F23 | `knowledge/category.vue` | 313行，需验证分类管理是否对接 `/api/v1/knowledge/category` | P1 | `/api/v1/knowledge/category` ✅ |
| F24 | `ai/chat.vue` | 592行，需验证对话发送是否对接 `POST /api/v1/ai/chat`，会话列表对接 `GET /api/v1/ai/conversations` | P1 | `/api/v1/ai/chat` + `/api/v1/ai/conversations` ✅ |
| F25 | `ai/copilot.vue` | 需验证运维 Copilot 场景分类+对话是否对接后端 AI API | P1 | `/api/v1/ai/` ✅ |
| F26 | `ai/analyze.vue` | 需验证日志分析是否对接 `POST /api/v1/ai/analyze/logs` | P1 | `/api/v1/ai/analyze/logs` ✅ |
| F27 | `management/VendorCredentials.vue` | 603行，需验证凭证管理是否对接 `/api/v1/credentials/vendors` | P1 | `/api/v1/credentials/vendors` ✅ |
| F28 | `system/adapters.vue` | 589行，需验证适配器管理是否对接 `/api/v1/admin/adapters` | P1 | `/api/v1/admin/adapters` ✅ |
| F29 | `automation/execution.vue` | **文件不存在**，`automation/` 目录下无 execution.vue；需新建或确认路径 | P1 | `/api/v1/automation/executions` ✅ |
| F30 | `monitoring/performance.vue` | 387行，需验证性能数据查询是否对接 `POST /api/v1/monitoring/metrics/query` | P2 | `/api/v1/monitoring/metrics/query` ✅ |
| F31 | `layout/index.vue` | 通知 badge 数字需动态化；`fetchNotificationCount` 已存在但需确认路由 | P2 | `/api/v1/notifications/messages/unread-count` ✅ |
| F32 | `login/index.vue` | 需验证登录后跳转逻辑是否与路由体系对齐 | P2 | `/api/v1/auth/login` ✅ |

### 0.2 开发方案

#### 第一阶段：P1 核心页面（确保基本功能可用）

**F4 → F3 → F1 → F2 → F6 → F7 → F8 → F9 → F10 → F11 → F12**

```
顺序  页面                问题
1     monitoring/devices  占位页 → 对接 /assets/device 列表
2     dashboard/index     硬编码静态 → 对接 dashboard/layout API
3     discovery/scan      调用错误的 discovery/scan GET → 改为 POST /discovery/ip/scan 或 snmp
4     workorder/create    136行骨架 → 完整表单字段
5     automation/script    验证并完善 CRUD
6     automation/task      验证并完善任务管理
7     workorder/list       验证列表+分页
8     workorder/my         验证我的工单筛选
9     system/user          全面审查 fetch 路径
10    system/role          验证角色 CRUD
11    system/menu          验证菜单管理
```

**第二阶段：P1 扩展 + 通知**

**F13 → F14 → F15 → F16 → F17 → F18 → F19 → F20 → F21 → F22 → F23 → F24 → F25 → F26 → F27 → F28 → F29**

```
12    notification/*       三个页面验证
13    backup/*             两个页面验证
14    report/*             三个页面验证
15    knowledge/*           三个页面验证
16    ai/*                 三个页面验证
17    management/VendorCredentials  凭证管理
18    system/adapters      适配器管理
19    automation/execution 新建或确认
```

**第三阶段：P2 完善**

**F30 → F31 → F32**

```
20    monitoring/performance  性能图表
21    layout/index.vue         通知动态化
22    login/index.vue          登录跳转逻辑
```

### 0.3 技术规范

1. **统一使用 request.js**：`src/api/request.js` 封装 axios，所有页面禁止直接用 `fetch`
2. **API 路径规范**：对照上表使用正确的后端路径，注意：
   - 设备用 `/assets/device`（不用 `/devices`）
   - 工单列表 `/workorders/`（**尾部有斜杠**）
   - 发现扫描用 `/discovery/ip/scan` 或 `/discovery/snmp/scan`（不用 `GET /discovery/scan`）
3. **Naive UI → Element Plus**：严格按本设计文档第2-6节执行全量迁移
4. **错误处理**：所有 async/await 必须有 `.catch(ElMessage.error)`，禁止静默失败
5. **分页**：统一使用 `page` + `page_size` 参数，从 `response.data` 取 `items` + `total`

### 0.4 验证要求

每个页面完成前端开发后，必须实际调用后端 API 验证：
1. `GET /api/v1/...` 列表 → 200，有数据返回
2. `POST /api/v1/...` 创建 → 200，新增成功
3. `PUT /api/v1/...` 更新 → 200，修改生效
4. `DELETE /api/v1/...` 删除 → 200，删除成功
5. 错误参数 → 422/400，有明确错误信息

---

## 1. 背景与目标

### 1.1 当前状态
- UI 框架：Vue 3 + Naive UI 2.43.2
- 37 个 Vue 文件使用 naive-ui（占全部 view 文件的 100%）
- App.vue + request.js 深度耦合 naive-ui
- 页面风格不统一：部分页面有完整 header + stats 卡片，部分页面只有基础 `padding: 16px`
- naive-ui 组件 API 分散，页面间复用性差

### 1.2 目标
1. 全量迁移 naive-ui → Element Plus（2.14.0）
2. 建立 UI 封装层（`src/components/ui/`），统一业务组件
3. 统一全平台视觉风格（Element Plus 默认蓝色系）
4. 建立可维护的前端架构，便于将来换库

### 1.3 设计原则
- **原生格式**：使用 Element Plus 原生 API，不兼容 naive-ui 的 column/form schema 格式
- **一步到位**：全部删除重建，不在旧代码上打补丁
- **封装层隔离**：业务代码调用封装层，封装层调用 Element Plus
- **前后分离**：基础设施（App.vue/router/styles）先行，页面按优先级逐个重建

---

## 2. 技术选型

### 2.1 UI 框架
| 项目 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 核心框架 | Vue 3 | ^3.4.21 | 保持不变 |
| UI 库 | Element Plus | 2.14.0 | 2026-05-08 最新版 |
| 状态管理 | Pinia | ^2.1.7 | 保持不变 |
| 路由 | Vue Router | ^4.3.0 | 保持不变 |
| HTTP | Axios | ^1.6.7 | 保持不变 |
| 图表 | ECharts | ^5.5.0 | 保持不变 |
| 图标 | @element-plus/icons-vue | ^1.0.0 | Element Plus 官方图标库 |

### 2.2 图标方案
Element Plus 使用 `@element-plus/icons-vue`，替换 `@vicons/ionicons5`：
- 内置图标：`Search`, `Plus`, `Delete`, `Edit`, `Refresh`, `View`, `Download`, `Upload`, `Check`, `Close`, `ArrowRight`, `ArrowLeft`, `ArrowUp`, `ArrowDown`, `Warning`, `InfoFilled`, `SuccessFilled`, `ErrorFilled`, `QuestionFilled`, `Plus`, `Minus` 等
- 使用方式：`<el-icon><Search /></el-icon>`

### 2.3 不再使用的依赖
- `naive-ui` → 移除
- `@vicons/ionicons5` → 移除

---

## 3. UI 封装层设计

### 3.1 组件目录结构
```
src/components/
├── ui/                          # ★ Element Plus 封装层
│   ├── AppTable.vue            # 统一表格：el-table + el-pagination + loading + 空状态
│   ├── AppModal.vue            # 统一弹窗：el-dialog + 表单 + 底部按钮 + loading
│   ├── AppDrawer.vue           # 统一抽屉：el-drawer + 标题 + loading
│   ├── AppForm.vue             # 统一表单：el-form + 验证规则 + 动态字段
│   ├── AppFilterBar.vue        # 统一筛选栏：搜索框 + 下拉筛选 + 操作按钮
│   ├── AppStatCard.vue         # 统计卡片：图标 + 数值 + 标签 + 点击事件
│   ├── AppPageHeader.vue       # 页面头部：标题 + 描述 + 右侧操作按钮
│   ├── AppConfirm.vue          # 确认对话框：删除/危险操作确认
│   └── AppEmpty.vue            # 空状态：图标 + 文案 + 可选操作按钮
│
├── illustrations/              # SVG 空状态插画（保持不变）
│   ├── EmptyChart.vue
│   ├── EmptyData.vue
│   ├── EmptyServer.vue
│   ├── EmptySearch.vue
│   └── EmptyAlert.vue
│
└── EmptyState.vue             # 空状态包装组件（保持）
```

### 3.2 AppTable.vue 规格

**功能**：封装 el-table 的分页、加载、空状态逻辑

**Props**：
```typescript
interface Props {
  // 数据
  data: any[]                    // 表格数据
  columns: TableColumn[]         // 列定义（见下方）
  loading?: boolean              // 加载状态，默认 false
  pagination?: PaginationConfig  // 分页配置，默认开启
  showEmpty?: boolean            // 是否显示空状态，默认 true
  
  // 筛选
  filterParams?: Record<string, any>  // 筛选参数（自动拼接到分页 URL）
  
  // 事件
  onPageChange?: (page: number, pageSize: number) => void
  onSortChange?: (prop: string, order: string) => void
  onSelectionChange?: (selection: any[]) => void
}

interface TableColumn {
  prop: string                   // 字段名
  label: string                  // 列标题
  width?: number | string       // 列宽
  minWidth?: number | string    // 最小列宽
  align?: 'left' | 'center' | 'right'
  sortable?: boolean | 'custom'
  fixed?: 'left' | 'right'
  showOverflowTooltip?: boolean  // 超长省略，默认 true
  
  // 自定义渲染（使用 Element Plus slot 机制）
  slot?: string                  // slot 名称，页面通过具名 slot 提供
  
  // 特殊类型
  type?: 'index' | 'selection' | 'expand'
}

interface PaginationConfig {
  current?: number               // 当前页
  pageSize?: number              // 每页条数
  total?: number                 // 总条数
  pageSizes?: number[]           // 可选每页条数 [10, 20, 50, 100]
  layout?: string               // 布局 'total, sizes, prev, pager, next, jumper'
  background?: boolean           // 按钮背景色
}
```

**事件**：
```typescript
emit('page-change', page: number, pageSize: number)
emit('sort-change', { prop: string, order: string })
emit('selection-change', rows: any[])
emit('row-click', row: any)
emit('row-dblclick', row: any)
```

**Slots**：
```html
<app-table :columns="columns" :data="tableData">
  <!-- 自定义列渲染 -->
  <template #status="{ row }">
    <el-tag :type="row.status === 'active' ? 'success' : 'info'">
      {{ row.status }}
    </el-tag>
  </template>
  
  <!-- 操作列 -->
  <template #actions="{ row }">
    <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
    <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
  </template>
</app-table>
```

### 3.3 AppModal.vue 规格

**功能**：封装 el-dialog 的表单弹窗

**Props**：
```typescript
interface Props {
  modelValue: boolean            // v-model 控制显示
  title: string                  // 弹窗标题
  width?: string | number        // 宽度，默认 '600px'
  formSchema?: FormSchema[]      // 表单字段定义（可选，不提供则用默认插槽）
  model?: Record<string, any>    // 表单数据（编辑模式时传入）
  rules?: Record<string, any>   // 表单验证规则
  loading?: boolean             // 提交 loading
  submitText?: string           // 提交按钮文字，默认 '确定'
  cancelText?: string            // 取消按钮文字，默认 '取消'
  showFooter?: boolean           // 是否显示底部按钮，默认 true
}

interface FormSchema {
  prop: string
  label: string
  component: string              // 'input' | 'select' | 'textarea' | 'switch' | 'number' | 'date' | 'datetime' | 'time' | 'cascader' | 'radio' | 'checkbox'
  componentProps?: Record<string, any>  // 组件属性
  options?: { label: string, value: any }[]  // select/radio/checkbox 选项
  show?: boolean                 // 是否显示
  if?: string                    // 条件显示（计算属性表达式）
}
```

### 3.4 AppDrawer.vue 规格

**功能**：封装 el-drawer 的侧边详情抽屉

**Props**：
```typescript
interface Props {
  modelValue: boolean
  title: string
  width?: string | number        // 默认 '600px'
  loading?: boolean
  showFooter?: boolean
  confirmText?: string
}
```

### 3.5 AppFilterBar.vue 规格

**功能**：封装搜索 + 筛选 + 操作按钮

**Props**：
```typescript
interface Props {
  searchPlaceholder?: string     // 搜索框占位符
  searchModel?: string          // 搜索关键词绑定
  filters?: FilterItem[]         // 筛选项
  buttons?: ButtonItem[]         // 操作按钮
  layout?: 'inline' | 'block'   // 布局方式
}

interface FilterItem {
  model: string                  // 绑定的变量名
  type: 'select' | 'date' | 'daterange' | 'datetimerange'
  placeholder: string
  options?: { label: string, value: any }[]
  props?: Record<string, any>
}

interface ButtonItem {
  text: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text'
  icon?: string                  // 图标名
  loading?: boolean
  disabled?: boolean
  event?: string                  // 点击事件名
}
```

**事件**：
```typescript
emit('search', value: string)    // 搜索
emit('filter-change', model: Record<string, any>)  // 筛选条件变化
emit('button-click', event: string)  // 按钮点击
```

### 3.6 AppStatCard.vue 规格

**功能**：封装统计卡片（dashboard 用）

**Props**：
```typescript
interface Props {
  title: string
  value: string | number
  icon?: string                  // Element Plus 图标名
  iconColor?: string             // 图标颜色
  iconBg?: string               // 图标背景色
  trend?: { value: number, type: 'up' | 'down' }  // 趋势
  clickable?: boolean
  loading?: boolean
}
```

### 3.7 AppPageHeader.vue 规格

**功能**：页面头部标题

**Props**：
```typescript
interface Props {
  title: string
  subtitle?: string
  breadcrumbs?: { label: string, to?: string }[]
  actions?: ButtonItem[]
}
```

---

## 4. 样式系统设计

### 4.1 CSS 变量（variables.css）
```css
:root {
  /* 主色 */
  --color-primary: #409eff;
  --color-primary-light: #79bbff;
  --color-primary-lighter: #c6e2ff;
  --color-primary-dark: #337ecc;
  --color-primary-darker: #268ddd;
  
  /* 成功 */
  --color-success: #67c23a;
  --color-success-light: #85ce61;
  --color-success-lighter: #e1f3d8;
  
  /* 警告 */
  --color-warning: #e6a23c;
  --color-warning-light: #ebb563;
  --color-warning-lighter: #fdf6ec;
  
  /* 危险 */
  --color-danger: #f56c6c;
  --color-danger-light: #f78989;
  --color-danger-lighter: #fef0f0;
  
  /* 信息 */
  --color-info: #909399;
  --color-info-light: #a6a9ad;
  --color-info-lighter: #f4f4f5;
  
  /* 文字 */
  --color-text-primary: #303133;
  --color-text-regular: #606266;
  --color-text-secondary: #909399;
  --color-text-placeholder: #c0c4cc;
  
  /* 边框 */
  --color-border-base: #dcdfe6;
  --color-border-light: #e4e7ed;
  --color-border-lighter: #ebeef5;
  --color-border-extra-light: #f2f6fc;
  
  /* 背景 */
  --color-bg-page: #f5f7fa;
  --color-bg-card: #ffffff;
  --color-bg-overlay: #ffffff;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  
  /* 阴影 */
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  
  /* 过渡 */
  --transition-fast: 0.15s;
  --transition-normal: 0.3s;
}
```

### 4.2 全局样式（common.css）
```css
/* 页面容器 */
.page-container {
  padding: var(--spacing-md);
  background: var(--color-bg-page);
  min-height: 100vh;
}

.page-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-lg);
}

/* 区块间隔 */
.section-gap {
  margin-bottom: var(--spacing-lg);
}

/* Flex 工具 */
.flex { display: flex; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.flex-col { display: flex; flex-direction: column; }
.gap-sm { gap: var(--spacing-sm); }
.gap-md { gap: var(--spacing-md); }
.gap-lg { gap: var(--spacing-lg); }

/* 文字 */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.text-sm { font-size: 13px; }
.text-xs { font-size: 12px; }
.font-bold { font-weight: 600; }

/* 状态颜色 */
.status-success { color: var(--color-success); }
.status-warning { color: var(--color-warning); }
.status-danger { color: var(--color-danger); }
.status-info { color: var(--color-info); }
```

---

## 5. 组件映射表（naive-ui → Element Plus）

### 5.1 基础组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-button` | `el-button` | API 基本一致 |
| `n-input` | `el-input` | API 基本一致 |
| `n-select` | `el-select` | API 基本一致 |
| `n-switch` | `el-switch` | API 基本一致 |
| `n-checkbox` | `el-checkbox` | API 一致 |
| `n-radio` | `el-radio` | API 一致 |
| `n-tag` | `el-tag` | API 一致 |
| `n-progress` | `el-progress` | API 一致 |
| `n-badge` | `el-badge` | API 一致 |
| `n-avatar` | `el-avatar` | API 一致 |
| `n-tooltip` | `el-tooltip` | API 一致 |
| `n-popconfirm` | `el-popconfirm` | API 一致 |

### 5.2 容器组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-card` | `el-card` | 有差异，AppCard 封装 |
| `n-modal` (v-model:show) | `el-dialog` (v-model:modelValue) | 需封装为 AppModal |
| `n-drawer` | `el-drawer` | 需封装为 AppDrawer |
| `n-collapse` | `el-collapse` | API 一致 |
| `n-tabs` / `n-tab-pane` | `el-tabs` / `el-tab-pane` | API 一致 |
| `n-steps` / `n-step` | `el-steps` / `el-step` | API 一致 |

### 5.3 表格与列表

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-data-table` | `el-table` + `el-pagination` | 需封装为 AppTable |
| `n-list` | `el-table` | 用表格代替列表 |
| `n-list-item` | `el-table-row` | 合并到 AppTable |

### 5.4 表单组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-form` | `el-form` | API 基本一致 |
| `n-form-item` | `el-form-item` | API 一致 |
| `n-input-number` | `el-input-number` | API 一致 |
| `n-cascader` | `el-cascader` | API 一致 |
| `n-date-picker` | `el-date-picker` | API 一致 |
| `n-time-picker` | `el-time-picker` | API 一致 |
| `n-color-picker` | `el-color-picker` | API 一致 |
| `n-slider` | `el-slider` | API 一致 |
| `n-transfer` | `el-transfer` | API 一致 |

### 5.5 布局组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-grid` / `n-gi` | `el-row` / `el-col` | Bootstrap 风格 |
| `n-space` | `el-space` | API 一致（v2.14+） |
| `n-layout` / `n-layout-sider` | `el-container` + CSS | 需重写 layout |

### 5.6 反馈组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-message` (useMessage) | `ElMessage` (静态) | request.js 改一行 |
| `n-notification` | `ElNotification` | 静态方法 |
| `n-dialog` (useDialog) | `ElMessageBox` | 静态方法 |
| `n-loading-bar` | `ElLoading` | 服务方式 |
| `n-spin` | `el-skeleton` 或 `v-loading` | 用 el-skeleton |
| `n-result` | 自行封装 | 简单组件 |

### 5.7 导航组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-menu` | `el-menu` | API 差异较大，layout 重写 |
| `n-breadcrumb` | `el-breadcrumb` | API 一致 |
| `n-steps` | `el-steps` | API 一致 |
| `n-pagination` | `el-pagination` | API 一致 |

### 5.8 数据展示组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-descriptions` | `el-descriptions` | API 一致 |
| `n-statistic` | `AppStatCard` | 自行封装更灵活 |
| `n-timeline` | `el-timeline` | API 一致 |
| `n-typography` | HTML + CSS | 用全局样式代替 |

### 5.9 树形组件映射

| naive-ui | Element Plus | 备注 |
|----------|-------------|------|
| `n-tree` | `el-tree` | API 差异较大，需封装 |
| `n-tree-select` | `el-tree-select` | v2.14+ 内置 |

---

## 6. 页面优先级与实施顺序

### Phase 1：基础设施（P0）
| 文件 | 复杂度 | 说明 |
|------|--------|------|
| `package.json` | 低 | naive-ui → element-plus |
| `vite.config.js` | 低 | 组件自动导入配置 |
| `src/styles/variables.css` | 中 | CSS 变量定义 |
| `src/styles/common.css` | 中 | 全局样式 |
| `src/styles/reset.css` | 低 | 样式重置 |
| `src/api/request.js` | 低 | useMessage → ElMessage |
| `src/App.vue` | 中 | n-config-provider → el-config-provider |
| `src/views/layout/index.vue` | 高 | 侧边栏 + 头部重写 |
| `src/views/login/index.vue` | 中 | 登录页重写 |

### Phase 2：封装层建立（P0）
| 文件 | 复杂度 | 说明 |
|------|--------|------|
| `src/components/ui/AppTable.vue` | 高 | 核心表格封装 |
| `src/components/ui/AppModal.vue` | 高 | 弹窗表单封装 |
| `src/components/ui/AppDrawer.vue` | 中 | 抽屉封装 |
| `src/components/ui/AppForm.vue` | 中 | 表单封装 |
| `src/components/ui/AppFilterBar.vue` | 中 | 筛选栏封装 |
| `src/components/ui/AppStatCard.vue` | 中 | 统计卡片封装 |
| `src/components/ui/AppPageHeader.vue` | 中 | 页面头部封装 |
| `src/components/ui/AppConfirm.vue` | 低 | 确认对话框封装 |
| `src/components/ui/AppEmpty.vue` | 低 | 空状态封装 |

### Phase 3-5：各模块页面

详见上方 **第 0 节** 统一的问题清单与开发方案，按 F1-F32 编号顺序执行。

---

## 7. request.js 重写

**改动点**：
```javascript
// Before
import { useMessage } from 'naive-ui'
let _message = null
const getMessage = () => {
  if (!_message) {
    try { _message = useMessage() } catch {}
  }
  return _message
}
getMessage()?.error('错误')

// After
import { ElMessage } from 'element-plus'
ElMessage.error('错误')
```

---

## 8. App.vue 重写

**改动点**：
```vue
<!-- Before -->
<n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
  <n-message-provider>
    <n-dialog-provider>
      <n-notification-provider>
        <n-loading-bar-provider>
          <router-view />
        </n-loading-bar-provider>
      </n-notification-provider>
    </n-dialog-provider>
  </n-message-provider>
</n-config-provider>

<!-- After -->
<el-config-provider :locale="zhCn" :size="defaultSize">
  <el-loading></el-loading>
  <router-view />
</el-config-provider>
```

**Element Plus 全局配置**：
- `el-config-provider`：提供全局 locale、size、message 等配置
- `size`：全局组件尺寸（large/default/small）
- `locale`：中文语言包

---

## 9. layout/index.vue 重写要点

**当前结构**（naive-ui）：
- `n-layout`（n-layout-sider + n-layout-header + n-layout-content）

**目标结构**（Element Plus）：
- `el-container` + `el-aside` + `el-header` + `el-main`
- `el-menu`：侧边栏菜单（需要重新配置 menu 数据）
- `el-scrollbar`：内容区域滚动条

**关键改动**：
1. 侧边栏菜单数据需要重新格式化
2. 折叠/展开状态需要自行维护
3. 面包屑导航需要使用 `el-breadcrumb`

---

## 10. 验收标准

### 基础设施验收
- [ ] `npm install` 无报错
- [ ] 首页加载无 console.error
- [ ] 登录/登出功能正常
- [ ] 侧边栏菜单可折叠
- [ ] 面包屑导航正确

### 封装层验收
- [ ] AppTable 在至少一个页面正常工作（分页、排序、loading、空状态）
- [ ] AppModal 在至少一个页面正常工作（新建、编辑）
- [ ] AppFilterBar 在至少一个页面正常工作

### 全页面验收
- [ ] 所有 37 个页面无 console.error
- [ ] 所有表单提交正常
- [ ] 所有表格分页正常
- [ ] 所有删除操作有确认提示
- [ ] 所有抽屉/弹窗关闭正常
- [ ] 响应式布局在 1920px 和 1366px 下正常

---

## 11. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Element Plus 与 naive-ui API 差异导致封装层设计偏差 | 中 | Phase 1 先快速验证基础设施，再建立封装层 |
| 37 个页面逐一验证耗时长 | 低 | 批量替换后按优先级分批验证 |
| AppTable 封装无法覆盖所有表格场景 | 中 | 提供 slot 机制允许页面自定义 |
| 图标替换工作量大（ionicons → element icons） | 低 | 搜索替换为主，少量手动调整 |
| layout/index.vue 重写工作量大 | 中 | 最后处理，留足时间 |

---

## 12. 文件清单

### 需要新建的文件
```
frontend/src/styles/variables.css
frontend/src/styles/common.css
frontend/src/styles/reset.css
frontend/src/components/ui/AppTable.vue
frontend/src/components/ui/AppModal.vue
frontend/src/components/ui/AppDrawer.vue
frontend/src/components/ui/AppForm.vue
frontend/src/components/ui/AppFilterBar.vue
frontend/src/components/ui/AppStatCard.vue
frontend/src/components/ui/AppPageHeader.vue
frontend/src/components/ui/AppConfirm.vue
frontend/src/components/ui/AppEmpty.vue
```

### 需要重写的文件
```
frontend/src/App.vue
frontend/src/views/layout/index.vue
frontend/src/views/login/index.vue
frontend/src/views/dashboard/index.vue
frontend/src/views/monitoring/alerts.vue
frontend/src/views/monitoring/devices.vue
frontend/src/views/monitoring/performance.vue
frontend/src/views/automation/script.vue
frontend/src/views/automation/task.vue
frontend/src/views/automation/execution.vue
frontend/src/views/workorder/list.vue
frontend/src/views/workorder/my.vue
frontend/src/views/workorder/create.vue
frontend/src/views/knowledge/list.vue
frontend/src/views/knowledge/cases.vue
frontend/src/views/knowledge/category.vue
frontend/src/views/ai/chat.vue
frontend/src/views/ai/copilot.vue
frontend/src/views/ai/analyze.vue
frontend/src/views/backup/list.vue
frontend/src/views/backup/restore.vue
frontend/src/views/notification/message.vue
frontend/src/views/notification/config.vue
frontend/src/views/notification/history.vue
frontend/src/views/report/list.vue
frontend/src/views/report/create.vue
frontend/src/views/report/template.vue
frontend/src/views/system/user.vue
frontend/src/views/system/role.vue
frontend/src/views/system/menu.vue
frontend/src/views/system/dict.vue
frontend/src/views/system/config.vue
frontend/src/views/system/logs.vue
frontend/src/views/system/adapters.vue
frontend/src/views/discovery/scan.vue
frontend/src/views/management/VendorCredentials.vue
```

### 需要修改的文件
```
frontend/package.json
frontend/vite.config.js (可能需要调整自动导入配置)
frontend/src/api/request.js
```

### 需要删除的文件
```
frontend/src/_archive_/ 目录（旧的备份文件）
```

---

## 13. 实施顺序

```
[Phase 1: 基础设施]
1. package.json 替换 naive-ui → element-plus + @element-plus/icons-vue
2. npm install
3. vite.config.js 更新自动导入配置
4. src/styles/ 建立（3个文件）
5. src/api/request.js 重写
6. src/App.vue 重写
7. src/views/layout/index.vue 重写（验证基础架构）
8. src/views/login/index.vue 重写
9. 浏览器验证：首页、登录、侧边栏

[Phase 2: 封装层]
10. src/components/ui/ 8 个封装组件
11. 在简单页面上验证封装层可用

[Phase 3: P1 页面]
12. dashboard/index.vue
13. monitoring/alerts.vue
14. monitoring/devices.vue
15. system/user.vue
16. system/role.vue
17. 验证 P1 页面

[Phase 4: P2 页面]
18. automation 3个页面
19. workorder 3个页面
20. system 4个页面
21. report 3个页面
22. discovery/scan.vue
23. 验证 P2 页面

[Phase 5: P3 页面]
24. 剩余页面
25. 整体验证

[Phase 6: 收尾]
26. 清理 _archive_ 目录
27. 全平台回归测试
28. 上线
```
