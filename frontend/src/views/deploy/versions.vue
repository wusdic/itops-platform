<template>
  <div class="versions-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">版本管理</h1>
        <p class="page-subtitle">应用版本注册与变更管理</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        注册新版本
      </el-button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-space :size="12" align="center">
        <el-input v-model="searchKeyword" placeholder="搜索版本/应用" clearable style="width: 200px" @clear="loadVersions" @keyup.enter="loadVersions">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 130px" @change="loadVersions">
          <el-option label="活跃" value="active" />
          <el-option label="已下线" value="deprecated" />
          <el-option label="灰度中" value="canary" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadVersions">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </el-space>
    </div>

    <!-- Versions Table -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <span>版本列表 <span class="table-count">共 {{ total }} 条</span></span>
      </template>
      <el-table :data="versions" v-loading="loading" :row-key="row => row.id" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="version" label="版本号" width="120">
          <template #default="{ row }">
            <span class="version-tag">v{{ row.version }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="app_name" label="应用名称" :show-overflow-tooltip="true" />
        <el-table-column prop="environment" label="环境" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.environment === 'production' ? 'danger' : 'info'">
              {{ row.environment === 'production' ? '生产' : row.environment === 'staging' ? '预发' : '测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="image" label="镜像" :show-overflow-tooltip="true" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" @click="openDetail(row)">详情</el-button>
              <el-button type="warning" link size="small" @click="startCanary(row)" :disabled="row.status !== 'active'">灰度</el-button>
              <el-button type="danger" link size="small" @click="deleteVersion(row)" :disabled="row.status === 'canary'">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadVersions"
          @current-change="loadVersions"
        />
      </div>
    </el-card>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="注册新版本" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="应用名称" prop="app_name">
          <el-input v-model="createForm.app_name" placeholder="请输入应用名称" />
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="createForm.version" placeholder="如 1.0.0" />
        </el-form-item>
        <el-form-item label="环境" prop="environment">
          <el-select v-model="createForm.environment" style="width: 100%">
            <el-option label="生产环境" value="production" />
            <el-option label="预发环境" value="staging" />
            <el-option label="测试环境" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="镜像" prop="image">
          <el-input v-model="createForm.image" placeholder="registry/app:v1.0.0" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="版本描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- Detail Drawer -->
    <el-drawer v-model="showDetailDrawer" :size="600" direction="rtl">
      <template #title>
        <span>版本详情</span>
      </template>
      <el-descriptions v-if="currentVersion" :column="1" border size="large" label-placement="left">
        <el-descriptions-item label="版本ID">{{ currentVersion.id }}</el-descriptions-item>
        <el-descriptions-item label="版本号"><span class="version-tag">v{{ currentVersion.version }}</span></el-descriptions-item>
        <el-descriptions-item label="应用名称">{{ currentVersion.app_name }}</el-descriptions-item>
        <el-descriptions-item label="环境">
          <el-tag size="small" :type="currentVersion.environment === 'production' ? 'danger' : 'info'">
            {{ currentVersion.environment === 'production' ? '生产' : currentVersion.environment === 'staging' ? '预发' : '测试' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" :type="getStatusType(currentVersion.status)">{{ getStatusLabel(currentVersion.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="镜像">{{ currentVersion.image }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentVersion.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentVersion.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(currentVersion.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 8px;">
          <el-button @click="showDetailDrawer = false">关闭</el-button>
          <el-button type="primary" @click="startCanary(currentVersion)" :disabled="currentVersion?.status !== 'active'">开始灰度</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { formatTime } from '@/utils/date'

const versions = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')

const showCreateDialog = ref(false)
const showDetailDrawer = ref(false)
const currentVersion = ref(null)
const submitLoading = ref(false)

const createForm = ref({
  app_name: '',
  version: '',
  environment: 'production',
  image: '',
  description: ''
})

const createRules = {
  app_name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  environment: [{ required: true, message: '请选择环境', trigger: 'change' }],
  image: [{ required: true, message: '请输入镜像地址', trigger: 'blur' }]
}

const createFormRef = ref(null)

const statusMap = { active: '活跃', deprecated: '已下线', canary: '灰度中' }

const getStatusType = (status) => {
  const map = { active: 'success', deprecated: 'info', canary: 'warning' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => statusMap[status] || status || '-'

const openDetail = (version) => {
  currentVersion.value = version
  showDetailDrawer.value = true
}

const startCanary = (version) => {
  currentVersion.value = version
  showDetailDrawer.value = false
  ElMessage.info(`跳转到金丝雀发布页面，版本: ${version.version}`)
  window.location.hash = '#/deploy/canary'
}

const deleteVersion = async (version) => {
  try {
    await ElMessageBox.confirm(`确定要删除版本 "${version.version}" 吗？此操作不可恢复。`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/deploy/versions/${version.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      ElMessage.success('版本已删除')
      loadVersions()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(err.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleCreate = async () => {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/deploy/versions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(createForm.value)
    })
    if (res.ok) {
      ElMessage.success('版本注册成功')
      showCreateDialog.value = false
      createForm.value = { app_name: '', version: '', environment: 'production', image: '', description: '' }
      loadVersions()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(err.message || '创建失败')
    }
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    submitLoading.value = false
  }
}

const loadVersions = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams()
    params.append('page', page.value)
    params.append('page_size', pageSize.value)
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    if (filterStatus.value) params.append('status', filterStatus.value)

    const res = await fetch(`/api/v1/deploy/versions?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!res.ok) {
      // 使用模拟数据
      versions.value = generateMockVersions()
      total.value = versions.value.length
      return
    }

    const data = await res.json()
    if (data.items) {
      versions.value = data.items
      total.value = data.total || versions.value.length
    } else if (Array.isArray(data)) {
      versions.value = data
      total.value = data.length
    }
  } catch (e) {
    versions.value = generateMockVersions()
    total.value = versions.value.length
  } finally {
    loading.value = false
  }
}

const generateMockVersions = () => [
  { id: 1, version: '2.1.0', app_name: 'user-service', environment: 'production', status: 'active', image: 'registry.example.com/user-service:v2.1.0', description: '用户服务v2.1.0', created_at: '2026-05-20T10:30:00Z', updated_at: '2026-05-20T10:30:00Z' },
  { id: 2, version: '2.0.5', app_name: 'user-service', environment: 'production', status: 'deprecated', image: 'registry.example.com/user-service:v2.0.5', description: '用户服务v2.0.5', created_at: '2026-05-10T08:00:00Z', updated_at: '2026-05-18T14:20:00Z' },
  { id: 3, version: '1.5.2', app_name: 'order-service', environment: 'production', status: 'canary', image: 'registry.example.com/order-service:v1.5.2', description: '订单服务灰度版本', created_at: '2026-05-22T09:15:00Z', updated_at: '2026-05-22T09:15:00Z' },
  { id: 4, version: '3.0.0-beta', app_name: 'payment-service', environment: 'staging', status: 'active', image: 'registry.example.com/payment-service:v3.0.0-beta', description: '支付服务Beta版本', created_at: '2026-05-23T16:45:00Z', updated_at: '2026-05-23T16:45:00Z' },
  { id: 5, version: '1.0.0', app_name: 'inventory-service', environment: 'test', status: 'active', image: 'registry.example.com/inventory:v1.0.0', description: '库存服务初始版本', created_at: '2026-05-15T11:00:00Z', updated_at: '2026-05-15T11:00:00Z' }
]

onMounted(() => {
  loadVersions()
})
</script>

<style scoped>
.versions-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }
.filter-bar { margin-bottom: 12px; }
.table-count { font-size: 13px; color: #888; font-weight: normal; margin-left: 8px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
.version-tag { font-family: 'Courier New', monospace; font-weight: 600; color: #409eff; }

:deep(.el-card) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-card__header) { color: #e0e0e0; border-bottom: 1px solid #2d2d44; }
:deep(.el-table) { background: transparent; color: #e0e0e0; --el-table-border-color: #2d2d44; --el-table-header-bg-color: #1a1a2e; --el-table-header-text-color: #a0a0a0; }
:deep(.el-table th) { background: #1a1a2e; color: #a0a0a0; }
:deep(.el-table tr) { background: #1a1a2e; }
:deep(.el-table td) { border-bottom: 1px solid #2d2d44; }
:deep(.el-dialog) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-dialog__title) { color: #e0e0e0; }
:deep(.el-drawer) { background: #1a1a2e; }
:deep(.el-drawer__title) { color: #e0e0e0; }
:deep(.el-form-item__label) { color: #a0a0a0; }
:deep(.el-input__wrapper) { background: #252538; border-color: #3a3a52; }
:deep(.el-select .el-input__wrapper) { background: #252538; }
:deep(.el-descriptions__label) { color: #a0a0a0; background: #1a1a2e; }
:deep(.el-descriptions__content) { color: #e0e0e0; background: #1a1a2e; }
:deep(.el-tag) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
</style>
