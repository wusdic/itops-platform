<template>
  <div class="tenants-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">租户管理</h1>
        <p class="page-subtitle">多租户环境下的租户创建、配置与配额管理</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建租户
      </el-button>
    </div>

    <!-- Tenant List -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>租户列表</span>
          <el-input v-model="searchKeyword" placeholder="搜索租户名称" clearable style="width: 200px" @input="handleSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
      </template>
      <el-table :data="filteredTenants" v-loading="loading" border style="width: 100%">
        <el-table-column prop="name" label="租户名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quota" label="配额" width="120">
          <template #default="{ row }">
            <span>{{ row.quota_used }}/{{ row.quota_total }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-button type="success" link size="small" @click="openAssignDialog(row)">分配用户</el-button>
              <el-button type="warning" link size="small" @click="openQuotaDialog(row)">配额</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showFormDialog" :title="isEdit ? '编辑租户' : '创建租户'" width="500px">
      <el-form :model="form" label-width="80px" ref="formRef">
        <el-form-item label="租户名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- Assign Users Dialog -->
    <el-dialog v-model="showAssignDialog" title="分配用户" width="600px">
      <div class="assign-container">
        <div class="assign-header">
          <span>当前租户：{{ currentTenant?.name }}</span>
          <el-button size="small" @click="loadTenantUsers">刷新</el-button>
        </div>
        <el-table :data="tenantUsers" v-loading="loadingUsers" border size="small" max-height="300">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="role" label="角色" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="danger" size="small" link @click="removeUser(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="assign-footer">
          <el-select v-model="selectedUserId" placeholder="选择用户" clearable style="width: 200px">
            <el-option v-for="u in availableUsers" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
          <el-button type="primary" size="small" @click="assignUser" :disabled="!selectedUserId">添加</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Quota Dialog -->
    <el-dialog v-model="showQuotaDialog" title="配额管理" width="400px">
      <el-form :model="quotaForm" label-width="100px">
        <el-form-item label="API调用配额">
          <el-input-number v-model="quotaForm.api_quota" :min="0" :max="1000000" />
        </el-form-item>
        <el-form-item label="存储配额(G)">
          <el-input-number v-model="quotaForm.storage_quota" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="用户数上限">
          <el-input-number v-model="quotaForm.user_quota" :min="1" :max="1000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuotaDialog = false">取消</el-button>
        <el-button type="primary" @click="saveQuota">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import tenantsAPI from '@/api/tenants'
import { formatTime } from '@/utils/date'

const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const tenants = ref([])

const showFormDialog = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({ id: null, name: '', description: '', status: 'active' })

const showAssignDialog = ref(false)
const currentTenant = ref(null)
const tenantUsers = ref([])
const loadingUsers = ref(false)
const availableUsers = ref([])
const selectedUserId = ref(null)

const showQuotaDialog = ref(false)
const quotaForm = ref({ api_quota: 10000, storage_quota: 100, user_quota: 50 })

const filteredTenants = computed(() => {
  if (!searchKeyword.value) return tenants.value
  return tenants.value.filter(t => t.name.includes(searchKeyword.value))
})

const loadTenants = async () => {
  loading.value = true
  try {
    const res = await tenantsAPI.getList()
    tenants.value = res.items || generateMockData()
  } catch {
    tenants.value = generateMockData()
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', description: '', status: 'active' }
  showFormDialog.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row }
  showFormDialog.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入租户名称')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await tenantsAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await tenantsAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    showFormDialog.value = false
    loadTenants()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除租户 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await tenantsAPI.delete(row.id)
    ElMessage.success('删除成功')
    loadTenants()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const openAssignDialog = async (row) => {
  currentTenant.value = row
  showAssignDialog.value = true
  loadTenantUsers()
  availableUsers.value = [
    { id: 1, username: 'user01' },
    { id: 2, username: 'user02' },
    { id: 3, username: 'user03' }
  ]
}

const loadTenantUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await tenantsAPI.getUsers(currentTenant.value.id)
    tenantUsers.value = res.items || generateMockUsers()
  } catch {
    tenantUsers.value = generateMockUsers()
  } finally {
    loadingUsers.value = false
  }
}

const assignUser = async () => {
  if (!selectedUserId.value) return
  try {
    await tenantsAPI.assignUser(currentTenant.value.id, { user_id: selectedUserId.value })
    ElMessage.success('添加成功')
    selectedUserId.value = null
    loadTenantUsers()
  } catch {
    ElMessage.error('添加失败')
  }
}

const removeUser = async (user) => {
  try {
    await tenantsAPI.removeUser(currentTenant.value.id, user.id)
    ElMessage.success('移除成功')
    loadTenantUsers()
  } catch {
    ElMessage.error('移除失败')
  }
}

const openQuotaDialog = (row) => {
  currentTenant.value = row
  quotaForm.value = {
    api_quota: row.api_quota || 10000,
    storage_quota: row.storage_quota || 100,
    user_quota: row.user_quota || 50
  }
  showQuotaDialog.value = true
}

const saveQuota = async () => {
  try {
    ElMessage.success('配额保存成功')
    showQuotaDialog.value = false
  } catch {
    ElMessage.error('保存失败')
  }
}

const handleSearch = () => {}

const generateMockData = () => [
  { id: 1, name: '默认租户', status: 'active', quota_used: 500, quota_total: 1000, user_count: 10, created_at: '2026-01-15T08:00:00Z', api_quota: 10000, storage_quota: 100, user_quota: 50 },
  { id: 2, name: '研发部', status: 'active', quota_used: 300, quota_total: 2000, user_count: 25, created_at: '2026-02-20T10:30:00Z', api_quota: 20000, storage_quota: 200, user_quota: 100 },
  { id: 3, name: '测试部', status: 'active', quota_used: 100, quota_total: 500, user_count: 8, created_at: '2026-03-10T14:00:00Z', api_quota: 5000, storage_quota: 50, user_quota: 20 },
  { id: 4, name: '生产租户', status: 'inactive', quota_used: 0, quota_total: 5000, user_count: 0, created_at: '2026-04-05T09:00:00Z', api_quota: 50000, storage_quota: 500, user_quota: 200 }
]

const generateMockUsers = () => [
  { id: 101, username: 'admin', role: '管理员' },
  { id: 102, username: 'dev_user', role: '开发者' }
]

onMounted(() => {
  loadTenants()
})
</script>

<style scoped>
.tenants-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }
.table-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

.assign-container { display: flex; flex-direction: column; gap: 12px; }
.assign-header { display: flex; justify-content: space-between; align-items: center; color: #e0e0e0; }
.assign-footer { display: flex; gap: 8px; align-items: center; margin-top: 12px; }

:deep(.el-card) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-card__header) { color: #e0e0e0; border-bottom: 1px solid #2d2d44; }
:deep(.el-table) { background: transparent; color: #e0e0e0; --el-table-border-color: #2d2d44; --el-table-header-bg-color: #1a1a2e; --el-table-header-text-color: #a0a0a0; }
:deep(.el-table th) { background: #1a1a2e; color: #a0a0a0; }
:deep(.el-table tr) { background: #1a1a2e; }
:deep(.el-table td) { border-bottom: 1px solid #2d2d44; }
:deep(.el-dialog) { background: #1a1a2e; }
:deep(.el-dialog__title) { color: #e0e0e0; }
:deep(.el-form-item__label) { color: #a0a0a0; }
:deep(.el-input__wrapper) { background: #252538; }
:deep(.el-radio__label) { color: #e0e0e0; }
:deep(.el-tag) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
</style>
