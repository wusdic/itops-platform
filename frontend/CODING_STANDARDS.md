# ITOps Platform 前端编码规范 v1.0

> 适用技术栈：Vue 3 + Element Plus + Vite + Axios
> 规范目标：统一 50+ 个页面的编码风格、提升可维护性、消除隐蔽 bug

---

## 一、组件库使用规范

### 1.1 组件库声明
**必须使用 Element Plus**，禁止混用其他组件库。

### 1.2 Element Plus 组件规范

| 规范 | 说明 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| el-form 的 label-width | 所有表单项必须设置 label-width | `label-width="120"` | 不设置导致错位 |
| el-input 的 v-model 类型 | 必须用 .trim 修饰符过滤首尾空格 | `v-model.trim="form.name"` | `v-model="form.name"` |
| el-input 的 clearable | 所有搜索/筛选 input 必须加 clearable | `clearable placeholder="搜索"` | 搜索框不可清空 |
| el-select 的 filterable | 选项超过 5 个必须支持搜索 | `filterable placeholder="请选择"` | 大列表无法搜索 |
| el-button 的 size | 统一用 `small`（表格内）和 `default`（页面主操作） | `size="small"` | `size="mini"` |
| el-tag 的 type | 按状态映射颜色，禁止硬编码颜色值 | `type="danger"`（严重） | `type="red"` |
| el-table 的 stripe | 列表默认开启斑马纹 | `stripe` | 无斑马纹阅读困难 |
| el-dialog 的 title | 必须设置 title，禁止空白标题 | `title="编辑设备"` | 无标题对话框 |
| el-dialog 的 width | 宽度不超过屏幕 80% | `width="600px"` | `width="100%"` |
| el-message 的 duration | 成功提示 2s，错误提示 4s | `ElMessage.success({ duration: 2000 })` | 从不关闭 |

### 1.3 响应式布局
- 使用 Element Plus 的栅格系统：`el-row` + `el-col`
- 统一断点：`xs`(<768px) / `sm`(≥768) / `md`(≥992) / `lg`(≥1200) / `xl`(≥1920)
- 禁止用固定像素宽度布局整页，只允许固定 header/sidebar 宽度

---

## 二、API 层规范

### 2.1 API 文件结构
```
api/
  request.js       # Axios 实例，全局拦截器（必须）
  index.js         # 统一导出所有 API 模块
  *.js             # 按业务模块拆分（devices.js, workorder.js...）
```

### 2.2 API 路径规范
- **必须**使用相对路径，由 `request.js` 的 baseURL 统一加 `/api/v1` 前缀
- **禁止**在 API 文件中硬编码完整 URL
- API 函数命名：`动词 + 资源名`（getDevices, createWorkorder, updateUser）

```javascript
// ✅ 正确
export const devices = {
  getList: (params) => request.get('/devices', { params }),
  getById: (id) => request.get(`/devices/${id}`),
}

// ❌ 错误
url: '/api/v1/devices'                     // 硬编码了 /api/v1
request.get('http://localhost:8000/devices') // 硬编码了 host
```

### 2.3 请求/响应处理
- 所有 API 必须通过 `request.js` 发起，由拦截器统一处理 token 注入和错误转换
- 响应数据统一从 `res.data` 取（拦截器已做解包）
- 错误必须用 `ElMessage.error()` 反馈给用户，禁止 silent catch

```javascript
// ✅ 正确（Composition API）
async function fetchDevices() {
  try {
    const res = await devices.getList({ page: 1, page_size: 20 })
    // 拦截器已解包：res 就是 {items: [...], total: N}
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载设备列表失败: ' + (e.message || '网络错误'))
  }
}

// ❌ 错误（silent catch）
async function fetchDevices() {
  try {
    const res = await devices.getList(...)
  } catch (e) {
    console.warn(e)  // 用户完全不知道失败了
  }
}
```

---

## 三、Vue 文件结构规范

### 3.1 单文件组件结构（从上到下）
```vue
<template>
  <!-- 1. 页面级容器（div.page-container） -->
  <!-- 2. 工具栏/筛选区 -->
  <!-- 3. 数据展示区（表格/卡片/图表） -->
  <!-- 4. 分页器 -->
  <!-- 5. 弹窗/抽屉（放底部） -->
</template>

<script setup>
// 1. import 区（按序：vue → 库 → 项目 → api）
// 2. 常量定义（const, 枚举映射）
// 3. 响应式状态（ref, reactive, computed）
// 4. 方法（async 函数放前面，工具函数放后面）
// 5. 生命周期 onMounted 等
</script>

<style scoped>
/* scoped 样式，禁止全局样式污染 */
.page-container {
  padding: 16px;
}
</style>
```

### 3.2 样式规范
- **必须**使用 `scoped`（每个 .vue 文件都要有 `<style scoped>`）
- 样式类名用 kebab-case（`el-table` / `page-container`）
- 禁止使用元素选择器（`div {}`）应使用 class 选择器
- 统一间距基准：4px 的倍数（8 / 12 / 16 / 24 / 32px）

---

## 四、状态与数据规范

### 4.1 列表页标准结构
每个列表页必须包含以下区块：

```
┌─────────────────────────────────────┐
│ 工具栏（搜索框 + 新建按钮 + 筛选）    │  ← el-row + el-col
├─────────────────────────────────────┤
│ 数据表格（el-table + el-table-column）│
├─────────────────────────────────────┤
│ 分页器（el-pagination）              │
└─────────────────────────────────────┘
```

### 4.2 分页规范
- 默认 `page=1, page_size=20`
- `page_size` 必须是 [20, 50, 100] 三选一
- 必须同步更新 total 值

```vue
<el-pagination
  v-model:current-page="queryParams.page"
  v-model:page-size="queryParams.page_size"
  :total="total"
  :page-sizes="[20, 50, 100]"
  layout="total, sizes, prev, pager, next, jumper"
  @size-change="handleSizeChange"
  @current-change="handlePageChange"
/>
```

### 4.3 空状态处理
- 列表为空时必须显示空状态提示（`el-empty`）
- 数字 0 显示 `--` 而非 `0%`（避免误解为"加载成功但值为0"）

```vue
<el-empty v-if="tableData.length === 0" description="暂无数据" />
```

---

## 五、安全与健壮性规范

### 5.1 危险操作二次确认
- 删除、恢复、批量操作必须用 `ElMessageBox.confirm()` 包裹
- 批量删除必须显示数量

```javascript
await ElMessageBox.confirm(
  `确定删除选中的 ${selection.length} 个设备吗？此操作不可恢复。`,
  '删除确认',
  { type: 'warning' }
)
```

### 5.2 防重复提交
- 提交按钮提交后设 `loading=true`，完成后重置
- 用 `disabled` 禁用按钮

```vue
<el-button type="primary" :loading="saving" :disabled="saving" @click="handleSubmit">
  {{ saving ? '保存中...' : '保存' }}
</el-button>
```

### 5.3 凭证安全

**禁止在任何代码文件中硬编码用户名/密码。**

| 场景 | 允许 | 不允许 |
|------|------|--------|
| README / 文档 | ✅ 公开默认账号密码作为初始访问说明 | - |
| .env.example | ✅ 提示需配置真实密码 | - |
| 数据库初始化 | ✅ 首次启动时写入数据库 | - |
| 前端登录表单 data | ❌ 禁止预填默认值 | `username: 'admin'` `password: 'Admin@123456'` |
| 后端默认值 | ✅ 可接受（有生产环境强检） | - |

```javascript
// ✅ 正确：表单初始化为空
const form = reactive({
  username: '',
  password: ''
})

// ❌ 错误：硬编码凭证
const form = reactive({
  username: 'admin',
  password: 'Admin@123456'
})
```

### 5.4 密码字段
- 必须用 `type="password"` + `show-password-on="click"`
- 不能明文显示

```vue
<el-input v-model="form.password" type="password" show-password-on="click" />
```

---

## 六、命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | kebab-case | `device-list.vue`, `workorder-api.js` |
| 组件名 | PascalCase | `DeviceList.vue`, `WorkorderDetail.vue` |
| 变量/函数 | camelCase | `deviceList`, `fetchDevices()` |
| 常量 | UPPER_SNAKE_CASE | `PAGE_SIZE`, `MAX_RETRIES` |
| CSS 类 | kebab-case | `.page-container`, `.tool-bar` |
| API 函数 | 动词+资源名 | `getDevices`, `createWorkorder` |

---

## 七、图标规范

- 图标统一使用 `@element-plus/icons-vue`
- 常用图标需在组件内单独 import，不允许全局注册后使用

```javascript
import { Search, Plus, Delete, Edit, Check, Close, Refresh } from '@element-plus/icons-vue'
```

---

## 八、Vue 指令与模板规范

### 8.1 v-if vs v-show
| 场景 | 推荐指令 | 原因 |
|------|----------|------|
| 频繁切换（切换卡/折叠） | `v-show` | 不销毁 DOM，性能更好 |
| 条件不满足时不渲染（权限/数据存在性） | `v-if` | 减少 DOM 节点 |
| el-dialog 显隐 | `v-model` | 不破坏 DOM 结构，禁止用 `:visible.sync` |

### 8.2 el-table-column 规范
- 必须设置 `prop`（数据字段）和 `label`（列标题），两者缺一不可
- 状态类列必须使用 `el-tag` 而非直接显示文本
- 操作列必须添加 `fixed="right"` 固定在右侧

```vue
<!-- ✅ 正确 -->
<el-table-column prop="status" label="状态" width="100">
  <template #default="{ row }">
    <el-tag :type="statusTypeMap[row.status]">{{ statusTextMap[row.status] }}</el-tag>
  </template>
</el-table-column>

<!-- ❌ 错误：没有 label -->
<el-table-column prop="status" />

<!-- ❌ 错误：状态用文本而非 el-tag -->
<el-table-column prop="status" label="状态">
  <template #default="{ row }">{{ row.status }}</template>
</el-table-column>
```

### 8.3 v-loading 规范
- 所有异步加载区域必须添加 `v-loading`
- 加载文案必须说明在加载什么

```vue
<el-table v-loading="loading" element-loading-text="正在加载设备列表..." />
```

### 8.4 时间格式化
- 所有时间字段必须用 `dayjs` 格式化，禁止在前端直接显示原始 ISO 字符串
- 表格内时间格式：`YYYY-MM-DD HH:mm`
- 列表页时间格式：`YYYY-MM-DD`

### 8.5 状态枚举映射（强制使用）
```javascript
const statusTypeMap = {
  online: 'success',    // 绿色-在线
  offline: 'info',     // 灰色-离线
  warning: 'warning',   // 黄色-警告
  critical: 'danger',   // 红色-严重
  pending: 'warning',   // 黄色-待处理
  resolved: 'success', // 绿色-已解决
}

const statusTextMap = {
  online: '在线',
  offline: '离线',
  warning: '警告',
  critical: '严重',
  pending: '待处理',
  resolved: '已解决',
}
```

### 8.6 日期范围选择器
```vue
<el-date-picker
  v-model="query.dateRange"
  type="datetimerange"
  range-separator="至"
  start-placeholder="开始时间"
  end-placeholder="结束时间"
  value-format="YYYY-MM-DD HH:mm:ss"
/>
```

### 8.7 Composition API 规范
```javascript
// ✅ ref 用于基础类型和需要整体替换的值
const count = ref(0)
const form = ref(null)

// ✅ reactive 用于对象类型
const queryParams = reactive({ page: 1, page_size: 20 })

// ✅ computed 正确用法
const isEmpty = computed(() => tableData.value.length === 0)

// ❌ 错误：reactive 绑定数组（失去响应式）
const list = reactive([])  // 改用 ref
```

---

## 九、常见场景模板

### 9.1 表格搜索表单
```vue
<el-row :gutter="12" class="filter-row">
  <el-col :span="6">
    <el-input v-model.trim="query.name" clearable placeholder="按名称搜索" @keyup.enter="handleSearch" />
  </el-col>
  <el-col :span="4">
    <el-select v-model="query.status" clearable placeholder="状态">
      <el-option label="在线" value="online" />
      <el-option label="离线" value="offline" />
    </el-select>
  </el-col>
  <el-col :span="4">
    <el-button type="primary" @click="handleSearch">查询</el-button>
    <el-button @click="handleReset">重置</el-button>
  </el-col>
</el-row>
```

### 9.2 表格操作列模板
```vue
<el-table-column label="操作" width="120" fixed="right">
  <template #default="{ row }">
    <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
    <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
  </template>
</el-table-column>
```

---

## 十、Git 提交规范

```
fix: 修复设备列表分页加载失败的问题
feat: 新增工单批量审批功能
refactor: 重构 monitoring.js API 结构
docs: 更新前端编码规范
style: 统一表格样式间距
```

---

## 十一、强制检查项（Q1-Q13）

检查每个 .vue 文件时，必须确认以下问题**不存在**：

| # | 问题描述 | 规范位置 |
|---|----------|----------|
| Q1 | 没有 `<style scoped>` | 3.1 |
| Q2 | `v-model` 没有 `.trim` 修饰符的文本输入框 | 1.2 |
| Q3 | 搜索框没有 `clearable` | 1.2 |
| Q4 | 危险操作没有二次确认 | 5.1 |
| Q5 | 提交按钮没有 `:loading` 防重 | 5.2 |
| Q6 | API 调用用 `catch(e) {}`（silent） | 2.3 |
| Q7 | `el-tag` 硬编码颜色而非 type 映射 | 1.2 |
| Q8 | 列表为空时没有 `el-empty` | 4.3 |
| Q9 | `el-dialog` 没有 title | 1.2 |
| Q10 | 分页器没有完整 layout 配置 | 4.2 |
| Q11 | `el-table-column` 没有 label 属性 | 8.2 |
| Q12 | `el-dialog` 使用已废弃的 `:visible.sync` | 8.1 |
| Q13 | 时间字段没有格式化（直接显示原始字符串） | 8.4 |

---

*规范版本：v1.0 | 创建日期：2026-05-27 | 三轮审查完成*
