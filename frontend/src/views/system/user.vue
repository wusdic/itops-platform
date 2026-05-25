<template>
  <div class="page-container">
    <el-card :bordered="false">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
        </div>
      </template>

      <el-space style="margin-bottom: 12px" align="center">
        <el-input v-model="searchKeyword" placeholder="搜索用户名/姓名" clearable style="width: 200px" @input="handleSearchInput">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="用户状态" clearable style="width: 120px" @change="debouncedSearch" />
      </el-space>

      <el-table
        :data="userList"
        :loading="loading"
        :row-key="row => row.id"
        style="width: 100%"
      >
        <el-table-column v-for="col in columns" :key="col.key" v-bind="col" />
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑用户 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-position="left" label-width="100">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item v-if="!form.id" label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" :options="roleOptions" placeholder="请选择角色" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { CONFIG } from '@/config/constants'

const loading = ref(false)
const submitting = ref(false)
const userList = ref([])
const searchKeyword = ref('')
const filterStatus = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('添加用户')

let searchTimer = null
function handleSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, CONFIG.SEARCH_DEBOUNCE)
}

function debouncedSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, CONFIG.SEARCH_DEBOUNCE)
}

// 手机号格式校验
function validatePhone(phone) {
  if (!phone) return true
  return /^1[3-9]\d{9}$/.test(phone)
}

// 邮箱格式校验
function validateEmail(email) {
  if (!email) return true
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
}

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})
const form = reactive({ id: null, username: '', password: '', full_name: '', email: '', phone: '', role: null })

const statusOptions = [
  { label: '全部', value: null },
  { label: '启用', value: '1' },
  { label: '禁用', value: '0' }
]

const roleOptions = ref([
  { label: '管理员', value: 'admin' },
  { label: '运维人员', value: 'operator' },
  { label: '访客', value: 'guest' }
])

async function loadRoles() {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/admin/roles', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) return
    const data = await res.json()
    const items = data.items || data.data?.items || []
    roleOptions.value = items.map(r => ({ label: r.name, value: r.code }))
  } catch (e) {
    // loadRoles failed, using defaults silently
  }
}

const roleMap = { admin: '管理员', operator: '运维人员', guest: '访客' }

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '用户名', key: 'username', width: 150 },
  { title: '姓名', key: 'full_name', width: 120 },
  { title: '邮箱', key: 'email', width: 180 },
  { title: '手机号', key: 'phone', width: 130 },
  { title: '角色', key: 'role', width: 120,
    render: ({ row }) => h(ElTag, { size: 'small', type: 'info' }, () => roleMap[row.role] || row.role || '-')
  },
  { title: '状态', key: 'is_active', width: 100,
    render: ({ row }) => h(ElTag, { size: 'small', type: row.is_active ? 'success' : 'info' }, () => row.is_active ? '启用' : '禁用')
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 240, fixed: 'right',
    render({ row }) {
      return h(ElSpace, { size: 12 }, () => [
        h(ElButton, { size: 'small', text: true, type: 'primary', onClick: () => handleEdit(row) }, () => '编辑'),
        h(ElButton, { size: 'small', text: true, type: 'warning', onClick: () => handleResetPwd(row) }, () => '重置密码'),
        h(ElButton, { size: 'small', text: true, type: 'danger', onClick: () => handleDelete(row) }, () => '删除')
      ])
    }
  }
]

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: pagination.page, page_size: pagination.pageSize })
    if (filterStatus.value) params.append('is_active', filterStatus.value)
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    const res = await fetch(`/api/v1/admin/users?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (!data || typeof data !== 'object') throw new Error('响应格式异常')
    userList.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载用户失败: ${e.message}`)
    userList.value = []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '添加用户'
  Object.assign(form, { id: null, username: '', password: '', full_name: '', email: '', phone: '', role: null })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑用户'
  Object.assign(form, { id: row.id, username: row.username, password: '', full_name: row.full_name || '', email: row.email || '', phone: row.phone || '', role: row.role || null })
  dialogVisible.value = true
}

async function handleResetPwd(row) {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/admin/users/${row.id}/reset-password`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success('密码已重置，请查看系统通知或联系管理员')
  } catch (e) {
    ElMessage.error(`重置失败: ${e.message}`)
  }
}

async function handleDelete(row) {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/admin/users/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    ElMessage.error(`删除失败: ${e.message}`)
  }
}

async function submitForm() {
  if (!form.username) {
    ElMessage.warning('请填写用户名')
    return
  }
  if (form.email && !validateEmail(form.email)) {
    ElMessage.warning('邮箱格式不正确')
    return
  }
  if (form.phone && !validatePhone(form.phone)) {
    ElMessage.warning('手机号格式不正确')
    return
  }
  if (submitting.value) return
  submitting.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const method = form.id ? 'PUT' : 'POST'
    const url = form.id ? `/api/v1/admin/users/${form.id}` : '/api/v1/admin/users'
    const body = { username: form.username, full_name: form.full_name, email: form.email, phone: form.phone, role: form.role }
    if (form.password) body.password = form.password
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(body)
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(`操作失败: ${e.message}`)
  } finally {
    submitting.value = false
  }
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

function handlePageChange(page) {
  pagination.page = page
  loadData()
}

onMounted(() => { loadData(); loadRoles() })
</script>

<style scoped>
.page-container { padding: 16px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
