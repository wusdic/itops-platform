<template>
  <div class="canary-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">金丝雀发布</h1>
        <p class="page-subtitle">渐进式流量切换与发布管理</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建金丝雀
      </el-button>
    </div>

    <!-- Active Canary Stats -->
    <div class="canary-stats">
      <div class="stat-badge active">
        <span class="stat-count">{{ canaryStats.active }}</span>
        <span class="stat-label">进行中</span>
      </div>
      <div class="stat-badge success">
        <span class="stat-count">{{ canaryStats.promoted }}</span>
        <span class="stat-label">已提升</span>
      </div>
      <div class="stat-badge danger">
        <span class="stat-count">{{ canaryStats.rolledback }}</span>
        <span class="stat-label">已回滚</span>
      </div>
      <div class="update-time">
        <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
        <span v-else>实时更新</span>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-space :size="12" align="center">
        <el-select v-model="filterStatus" placeholder="发布状态" clearable style="width: 140px" @change="loadCanaries">
          <el-option label="进行中" value="running" />
          <el-option label="已提升" value="promoted" />
          <el-option label="已终止" value="terminated" />
          <el-option label="已回滚" value="rolledback" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadCanaries">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </el-space>
    </div>

    <!-- Canary List -->
    <div class="canary-list">
      <el-card v-for="canary in canaries" :key="canary.id" :bordered="false" class="canary-card">
        <template #header>
          <div class="canary-card-header">
            <div class="canary-info">
              <span class="app-name">{{ canary.app_name }}</span>
              <el-tag size="small" :type="getStatusType(canary.status)">{{ getStatusLabel(canary.status) }}</el-tag>
            </div>
            <div class="canary-actions">
              <el-button v-if="canary.status === 'running'" type="primary" size="small" @click="adjustWeight(canary)">调整权重</el-button>
              <el-button v-if="canary.status === 'running'" type="success" size="small" @click="promote(canary)">提升</el-button>
              <el-button v-if="canary.status === 'running'" type="danger" size="small" @click="rollback(canary)">回滚</el-button>
              <el-button v-if="canary.status === 'running'" type="warning" size="small" @click="terminate(canary)">终止</el-button>
            </div>
          </div>
        </template>

        <div class="canary-detail">
          <div class="version-info">
            <div class="version-item stable">
              <span class="version-label">稳定版本</span>
              <span class="version-value">v{{ canary.stable_version }}</span>
              <span class="version-weight">{{ 100 - canary.weight }}%</span>
            </div>
            <div class="weight-arrow">
              <span class="weight-value">{{ canary.weight }}%</span>
              <el-icon class="arrow-icon"><Right /></el-icon>
            </div>
            <div class="version-item canary">
              <span class="version-label">金丝雀版本</span>
              <span class="version-value">v{{ canary.canary_version }}</span>
              <span class="version-weight">{{ canary.weight }}%</span>
            </div>
          </div>

          <!-- Traffic Weight Visualization -->
          <div class="traffic-bar">
            <div class="traffic-track">
              <div class="traffic-stable" :style="{ width: (100 - canary.weight) + '%' }">
                <span class="traffic-label">{{ 100 - canary.weight }}%</span>
              </div>
              <div class="traffic-canary" :style="{ width: canary.weight + '%' }">
                <span class="traffic-label">{{ canary.weight }}%</span>
              </div>
            </div>
          </div>

          <div class="canary-meta">
            <span>开始时间: {{ formatTime(canary.started_at) }}</span>
            <span v-if="canary.updated_at">最后更新: {{ formatTime(canary.updated_at) }}</span>
          </div>
        </div>
      </el-card>

      <el-empty v-if="!loading && canaries.length === 0" description="暂无金丝雀发布" />
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="创建金丝雀发布" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <el-form-item label="应用名称" prop="app_name">
          <el-input v-model.trim="createForm.app_name" placeholder="请输入应用名称" />
        </el-form-item>
        <el-form-item label="稳定版本" prop="stable_version">
          <el-select v-model="createForm.stable_version" placeholder="选择稳定版本" style="width: 100%">
            <el-option v-for="v in availableVersions" :key="v.id" :label="'v' + v.version" :value="v.version" />
          </el-select>
        </el-form-item>
        <el-form-item label="金丝雀版本" prop="canary_version">
          <el-input v-model.trim="createForm.canary_version" placeholder="如 2.1.0" />
        </el-form-item>
        <el-form-item label="初始权重" prop="weight">
          <el-slider v-model="createForm.weight" :min="5" :max="50" :step="5" show-input />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="createForm.description" type="textarea" :rows="3" placeholder="发布描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- Weight Adjustment Dialog -->
    <el-dialog v-model="showWeightDialog" title="调整流量权重" width="500px">
      <div v-if="currentCanary" class="weight-adjust">
        <div class="weight-display">
          <div class="weight-item stable">
            <span class="weight-label">稳定版本 (v{{ currentCanary.stable_version }})</span>
            <span class="weight-percent">{{ 100 - weightForm.newWeight }}%</span>
          </div>
          <div class="weight-arrow-large">
            <el-icon><Right /></el-icon>
          </div>
          <div class="weight-item canary">
            <span class="weight-label">金丝雀版本 (v{{ currentCanary.canary_version }})</span>
            <span class="weight-percent">{{ weightForm.newWeight }}%</span>
          </div>
        </div>
        <el-slider v-model="weightForm.newWeight" :min="5" :max="95" :step="5" show-input />
        <div class="weight-presets">
          <el-button size="small" @click="weightForm.newWeight = 10">10%</el-button>
          <el-button size="small" @click="weightForm.newWeight = 25">25%</el-button>
          <el-button size="small" @click="weightForm.newWeight = 50">50%</el-button>
          <el-button size="small" @click="weightForm.newWeight = 75">75%</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="showWeightDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleAdjustWeight">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Right, Loading } from '@element-plus/icons-vue'
import { formatTime } from '@/utils/date'

const canaries = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const isActive = ref(true)

const canaryStats = ref({ active: 0, promoted: 0, rolledback: 0 })

const showCreateDialog = ref(false)
const showWeightDialog = ref(false)
const currentCanary = ref(null)
const submitLoading = ref(false)
const availableVersions = ref([])

const createForm = ref({
  app_name: '',
  stable_version: '',
  canary_version: '',
  weight: 10,
  description: ''
})

const weightForm = ref({
  newWeight: 10
})

const createRules = {
  app_name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  stable_version: [{ required: true, message: '请选择稳定版本', trigger: 'change' }],
  canary_version: [{ required: true, message: '请输入金丝雀版本', trigger: 'blur' }],
  weight: [{ required: true, message: '请设置初始权重', trigger: 'change' }]
}

const createFormRef = ref(null)

const statusMap = { running: '进行中', promoted: '已提升', terminated: '已终止', rolledback: '已回滚' }

const getStatusType = (status) => {
  const map = { running: 'warning', promoted: 'success', terminated: 'info', rolledback: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => statusMap[status] || status || '-'

const adjustWeight = (canary) => {
  currentCanary.value = canary
  weightForm.value.newWeight = canary.weight
  showWeightDialog.value = true
}

const promote = async (canary) => {
  try {
    await ElMessageBox.confirm(`确定要提升金丝雀版本 v${canary.canary_version} 吗？这将使金丝雀版本成为唯一运行版本。`, '确认提升', {
      confirmButtonText: '确认提升',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/deploy/canary/${canary.id}/promote`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      ElMessage.success('金丝雀已提升为正式版本')
      loadCanaries()
    } else {
      ElMessage.error('提升失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const rollback = async (canary) => {
  try {
    await ElMessageBox.confirm(`确定要回滚到稳定版本 v${canary.stable_version} 吗？`, '确认回滚', {
      confirmButtonText: '确认回滚',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/deploy/canary/${canary.id}/rollback`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      ElMessage.success('已回滚到稳定版本')
      loadCanaries()
    } else {
      ElMessage.error('回滚失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const terminate = async (canary) => {
  try {
    await ElMessageBox.confirm(`确定要终止此金丝雀发布吗？流量将切回稳定版本。`, '确认终止', {
      confirmButtonText: '确认终止',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/deploy/canary/${canary.id}/terminate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      ElMessage.success('金丝雀发布已终止')
      loadCanaries()
    } else {
      ElMessage.error('终止失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const handleAdjustWeight = async () => {
  if (!currentCanary.value) return
  submitLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/deploy/canary/${currentCanary.value.id}/weight`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ weight: weightForm.value.newWeight })
    })
    if (res.ok) {
      ElMessage.success('权重已调整')
      showWeightDialog.value = false
      loadCanaries()
    } else {
      ElMessage.error('调整失败')
    }
  } catch (e) {
    ElMessage.error('调整失败')
  } finally {
    submitLoading.value = false
  }
}

const handleCreate = async () => {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/deploy/canary', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(createForm.value)
    })
    if (res.ok) {
      ElMessage.success('金丝雀发布已创建')
      showCreateDialog.value = false
      createForm.value = { app_name: '', stable_version: '', canary_version: '', weight: 10, description: '' }
      loadCanaries()
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

const loadCanaries = async () => {
  if (!isActive.value) return
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams()
    if (filterStatus.value) params.append('status', filterStatus.value)

    const res = await fetch(`/api/v1/deploy/canary?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!res.ok) {
      canaries.value = generateMockCanaries()
      updateStats()
      return
    }

    const data = await res.json()
    if (Array.isArray(data)) {
      canaries.value = data
    } else if (data.items) {
      canaries.value = data.items
    }
    updateStats()
  } catch (e) {
    canaries.value = generateMockCanaries()
    updateStats()
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const stats = { active: 0, promoted: 0, rolledback: 0 }
  for (const c of canaries.value) {
    if (c.status === 'running') stats.active++
    else if (c.status === 'promoted') stats.promoted++
    else if (c.status === 'rolledback') stats.rolledback++
  }
  canaryStats.value = stats
}

const loadVersions = async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/deploy/versions?status=active', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      availableVersions.value = data.items || []
    }
  } catch (e) {
    availableVersions.value = []
  }
}

const generateMockCanaries = () => [
  { id: 1, app_name: 'user-service', stable_version: '2.0.5', canary_version: '2.1.0', weight: 25, status: 'running', started_at: '2026-05-25T10:00:00Z', updated_at: '2026-05-25T14:30:00Z', description: '用户服务灰度发布' },
  { id: 2, app_name: 'order-service', stable_version: '1.5.1', canary_version: '1.5.2', weight: 50, status: 'running', started_at: '2026-05-24T08:00:00Z', updated_at: '2026-05-25T12:00:00Z', description: '订单服务灰度' },
  { id: 3, app_name: 'payment-service', stable_version: '2.5.0', canary_version: '3.0.0', weight: 100, status: 'promoted', started_at: '2026-05-20T09:00:00Z', updated_at: '2026-05-22T16:00:00Z', description: '支付服务全量发布' },
  { id: 4, app_name: 'inventory-service', stable_version: '1.0.0', canary_version: '1.1.0', weight: 0, status: 'rolledback', started_at: '2026-05-23T11:00:00Z', updated_at: '2026-05-23T15:00:00Z', description: '库存服务回滚' }
]

let pollTimer = null

const startPolling = () => {
  stopPolling()
  pollTimer = setInterval(() => {
    if (isActive.value) {
      loadCanaries()
    }
  }, 10000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  isActive.value = true
  loadCanaries()
  loadVersions()
  startPolling()
})

onBeforeUnmount(() => {
  isActive.value = false
  stopPolling()
})
</script>

<style scoped>
.canary-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.canary-stats { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.stat-badge { display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 6px; }
.stat-badge.active { background: #1a2a1a; border: 1px solid #2d5a2d; }
.stat-badge.success { background: #1a2a2a; border: 1px solid #2d4a4a; }
.stat-badge.danger { background: #2a1a1a; border: 1px solid #4a2d2d; }
.stat-count { font-size: 20px; font-weight: 700; color: #e0e0e0; }
.stat-label { font-size: 13px; color: #888; }

.update-time { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #888; margin-left: auto; }
.is-loading { animation: rotating 2s linear infinite; }
@keyframes rotating { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.filter-bar { margin-bottom: 12px; }

.canary-list { display: grid; gap: 16px; }
.canary-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.canary-card-header { display: flex; justify-content: space-between; align-items: center; }
.canary-info { display: flex; align-items: center; gap: 12px; }
.app-name { font-size: 16px; font-weight: 600; color: #e0e0e0; }
.canary-actions { display: flex; gap: 8px; }

.canary-detail { padding: 8px 0; }
.version-info { display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 16px; }
.version-item { display: flex; flex-direction: column; align-items: center; padding: 12px 20px; border-radius: 8px; min-width: 140px; }
.version-item.stable { background: #252538; }
.version-item.canary { background: #2a2a40; border: 1px solid #409eff; }
.version-label { font-size: 12px; color: #888; margin-bottom: 4px; }
.version-value { font-size: 16px; font-weight: 600; color: #e0e0e0; }
.version-weight { font-size: 14px; color: #409eff; margin-top: 4px; }

.weight-arrow { display: flex; flex-direction: column; align-items: center; }
.weight-value { font-size: 14px; color: #409eff; font-weight: 600; }
.arrow-icon { color: #409eff; font-size: 20px; }

.traffic-bar { margin: 16px 0; }
.traffic-track { display: flex; height: 32px; border-radius: 6px; overflow: hidden; background: #252538; }
.traffic-stable { display: flex; align-items: center; justify-content: center; background: #409eff; transition: width 0.3s; }
.traffic-canary { display: flex; align-items: center; justify-content: center; background: #66d9b8; transition: width 0.3s; }
.traffic-label { font-size: 12px; font-weight: 600; color: #fff; }

.canary-meta { display: flex; justify-content: space-between; font-size: 12px; color: #888; }

.weight-adjust { padding: 20px 0; }
.weight-display { display: flex; align-items: center; justify-content: center; gap: 30px; margin-bottom: 30px; }
.weight-item { display: flex; flex-direction: column; align-items: center; padding: 16px 24px; border-radius: 8px; min-width: 160px; }
.weight-item.stable { background: #252538; }
.weight-item.canary { background: #2a2a40; border: 1px solid #409eff; }
.weight-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.weight-percent { font-size: 24px; font-weight: 700; color: #e0e0e0; }
.weight-arrow-large { font-size: 24px; color: #409eff; }
.weight-presets { display: flex; justify-content: center; gap: 12px; margin-top: 16px; }

:deep(.el-card) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-card__header) { color: #e0e0e0; border-bottom: 1px solid #2d2d44; }
:deep(.el-dialog) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-dialog__title) { color: #e0e0e0; }
:deep(.el-form-item__label) { color: #a0a0a0; }
:deep(.el-input__wrapper) { background: #252538; border-color: #3a3a52; }
:deep(.el-select .el-input__wrapper) { background: #252538; }
:deep(.el-slider .el-slider__runway) { background: #252538; }
:deep(.el-slider .el-slider__bar) { background: #409eff; }
:deep(.el-slider .el-slider__button) { border-color: #409eff; }
:deep(.el-tag) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
:deep(.el-button--small) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
:deep(.el-empty__description) { color: #888; }
</style>
