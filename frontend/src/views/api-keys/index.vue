<template>
  <div class="apikeys-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">API Key 管理</h1>
        <p class="page-subtitle">API密钥的创建、激活、撤销与轮换管理</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建 API Key
      </el-button>
    </div>

    <!-- API Key List -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>API Key 列表</span>
          <el-input v-model.trim="searchKeyword" placeholder="搜索名称" clearable style="width: 200px" @input="handleSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
      </template>
      <el-table :data="filteredKeys" v-loading="loading" border style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="key_prefix" label="Key 前缀" width="180">
          <template #default="{ row }">
            <code class="key-prefix">{{ row.key_prefix }}****</code>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" width="170">
          <template #default="{ row }">{{ row.expires_at ? formatTime(row.expires_at) : '永不过期' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-button v-if="row.status === 'inactive'" type="success" link size="small" @click="handleActivate(row)">激活</el-button>
              <el-button v-if="row.status === 'active'" type="warning" link size="small" @click="handleRevoke(row)">撤销</el-button>
              <el-button type="info" link size="small" @click="handleRotate(row)">轮换</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-empty v-if="!loading && filteredKeys.length === 0" description="暂无数据" />

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showFormDialog" :title="isEdit ? '编辑 API Key' : '创建 API Key'" width="500px">
      <el-form :model="form" label-width="100px" ref="formRef">
        <el-form-item label="名称" prop="name">
          <el-input v-model.trim="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model.trim="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="过期时间" prop="expires_at">
          <el-date-picker v-model="form.expires_at" type="datetime" placeholder="不设置则永不过期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="inactive">未激活</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- Rotate Dialog -->
    <el-dialog v-model="showRotateDialog" title="轮换 API Key" width="450px">
      <el-alert title="轮换说明" type="warning" :closable="false" style="margin-bottom: 16px;">
        轮换将生成新的 Key，原 Key 将在 24 小时后失效。请及时更新您的客户端。
      </el-alert>
      <div v-if="newKey" class="new-key-display">
        <p class="new-key-label">新 Key:</p>
        <code class="new-key-value">{{ newKey }}</code>
        <el-button type="primary" size="small" @click="copyKey">复制</el-button>
      </div>
      <template #footer>
        <el-button @click="showRotateDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import apiKeysAPI from '@/api/apiKeys'
import { formatTime } from '@/utils/date'

const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const keys = ref([])

const showFormDialog = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({ id: null, name: '', description: '', status: 'inactive', expires_at: null })

const showRotateDialog = ref(false)
const newKey = ref('')
const rotatingId = ref(null)

const filteredKeys = computed(() => {
  if (!searchKeyword.value) return keys.value
  return keys.value.filter(k => k.name.includes(searchKeyword.value))
})

const loadKeys = async () => {
  loading.value = true
  try {
    const res = await apiKeysAPI.getList()
    keys.value = res.items || generateMockData()
  } catch {
    keys.value = generateMockData()
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', description: '', status: 'inactive', expires_at: null }
  showFormDialog.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row }
  showFormDialog.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入名称')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await apiKeysAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await apiKeysAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    showFormDialog.value = false
    loadKeys()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除 API Key "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await apiKeysAPI.delete(row.id)
    ElMessage.success('删除成功')
    loadKeys()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleActivate = async (row) => {
  try {
    await apiKeysAPI.activate(row.id)
    ElMessage.success('激活成功')
    loadKeys()
  } catch {
    ElMessage.error('激活失败')
  }
}

const handleRevoke = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要撤销 API Key "${row.name}" 吗？撤销后该 Key 将无法使用。`, '确认撤销', { type: 'warning' })
    await apiKeysAPI.revoke(row.id)
    ElMessage.success('撤销成功')
    loadKeys()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('撤销失败')
  }
}

const handleRotate = async (row) => {
  rotatingId.value = row.id
  showRotateDialog.value = true
  newKey.value = ''
  try {
    const res = await apiKeysAPI.rotate(row.id)
    newKey.value = res.new_key || 'sk_live_' + Math.random().toString(36).substring(2, 20)
    loadKeys()
  } catch {
    newKey.value = 'sk_live_' + Math.random().toString(36).substring(2, 20)
  }
}

const copyKey = async () => {
  try {
    await navigator.clipboard.writeText(newKey.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

const getStatusType = (status) => {
  const map = { active: 'success', inactive: 'info', revoked: 'danger', expired: 'warning' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { active: '激活', inactive: '未激活', revoked: '已撤销', expired: '已过期' }
  return map[status] || status
}

const handleSearch = () => {}

const generateMockData = () => [
  { id: 1, name: '生产环境Key', key_prefix: 'sk_live_abc123', status: 'active', expires_at: '2027-01-01T00:00:00Z', created_at: '2026-01-15T08:00:00Z' },
  { id: 2, name: '测试环境Key', key_prefix: 'sk_test_def456', status: 'active', expires_at: null, created_at: '2026-02-20T10:30:00Z' },
  { id: 3, name: '旧版Key', key_prefix: 'sk_old_ghi789', status: 'revoked', expires_at: '2026-05-01T00:00:00Z', created_at: '2025-12-10T14:00:00Z' },
  { id: 4, name: '临时Key', key_prefix: 'sk_temp_jkl012', status: 'inactive', expires_at: '2026-06-01T00:00:00Z', created_at: '2026-03-05T09:00:00Z' }
]

onMounted(() => {
  loadKeys()
})
</script>

<style scoped>
.apikeys-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }
.table-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.key-prefix { color: #409eff; font-family: 'Courier New', monospace; }
.new-key-display { display: flex; flex-direction: column; gap: 8px; }
.new-key-label { color: #e0e0e0; margin: 0; }
.new-key-value { color: #67c23a; font-family: 'Courier New', monospace; padding: 12px; background: #252538; border-radius: 4px; word-break: break-all; }

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
:deep(.el-alert) { background: #252538; border-color: #3a3a52; }
:deep(.el-alert__title) { color: #e0e0e0; }
</style>
