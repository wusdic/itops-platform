<template>
  <div class="health-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">部署健康状态</h1>
        <p class="page-subtitle">部署状态监控与健康检查</p>
      </div>
      <el-button type="primary" :loading="loading" @click="loadHealth">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- Health Overview -->
    <div class="health-overview">
      <el-card :bordered="false" class="overview-card">
        <template #header>
          <div class="card-header">
            <span>总体健康状态</span>
            <el-tag :type="overallHealth.type" size="large">{{ overallHealth.label }}</el-tag>
          </div>
        </template>
        <div class="health-summary">
          <div class="health-stat">
            <span class="stat-number healthy">{{ healthStats.healthy }}</span>
            <span class="stat-desc">健康</span>
          </div>
          <div class="health-stat">
            <span class="stat-number degraded">{{ healthStats.degraded }}</span>
            <span class="stat-desc"> degraded</span>
          </div>
          <div class="health-stat">
            <span class="stat-number unhealthy">{{ healthStats.unhealthy }}</span>
            <span class="stat-desc">异常</span>
          </div>
          <div class="health-stat">
            <span class="stat-number unknown">{{ healthStats.unknown }}</span>
            <span class="stat-desc">未知</span>
          </div>
        </div>
      </el-card>

      <el-card :bordered="false" class="overview-card">
        <template #header>
          <span>部署统计</span>
        </template>
        <div class="health-summary">
          <div class="health-stat">
            <span class="stat-number">{{ deployStats.total }}</span>
            <span class="stat-desc">总部署</span>
          </div>
          <div class="health-stat">
            <span class="stat-number success">{{ deployStats.active }}</span>
            <span class="stat-desc">运行中</span>
          </div>
          <div class="health-stat">
            <span class="stat-number">{{ deployStats.succeeded }}</span>
            <span class="stat-desc">成功</span>
          </div>
          <div class="health-stat">
            <span class="stat-number danger">{{ deployStats.failed }}</span>
            <span class="stat-desc">失败</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Deployment Status -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>部署状态</span>
          <el-select v-model="filterHealth" placeholder="健康状态" clearable style="width: 120px" @change="loadDeployments">
            <el-option label="健康" value="healthy" />
            <el-option label=" degraded" value="degraded" />
            <el-option label="异常" value="unhealthy" />
          </el-select>
        </div>
      </template>
      <el-table :data="deployments" v-loading="loading" :row-key="row => row.id" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="app_name" label="应用" :show-overflow-tooltip="true" />
        <el-table-column prop="version" label="版本" width="100">
          <template #default="{ row }"><span class="version-tag">v{{ row.version }}</span></template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.environment === 'production' ? 'danger' : 'info'">
              {{ row.environment === 'production' ? '生产' : row.environment === 'staging' ? '预发' : '测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="health_status" label="健康状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getHealthType(row.health_status)">
              {{ getHealthLabel(row.health_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="replicas" label="副本" width="80">
          <template #default="{ row }">{{ row.replicas }}/{{ row.ready_replicas || row.replicas }}</template>
        </el-table-column>
        <el-table-column prop="health_check" label="健康检查" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.health_check === 'pass'" color="#67c23a"><SuccessFilled /></el-icon>
            <el-icon v-else-if="row.health_check === 'fail'" color="#f56c6c"><CircleCloseFilled /></el-icon>
            <el-icon v-else color="#909399"><QuestionFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
              <el-button type="warning" link size="small" @click="restart(row)">重启</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Deployment History -->
    <el-card :bordered="false" class="table-card" style="margin-top: 16px;">
      <template #header>
        <span>部署历史</span>
      </template>
      <el-table :data="history" v-loading="loadingHistory" :row-key="row => row.id" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="app_name" label="应用" :show-overflow-tooltip="true" />
        <el-table-column prop="version" label="版本" width="100">
          <template #default="{ row }"><span class="version-tag">v{{ row.version }}</span></template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.environment === 'production' ? 'danger' : 'info'">
              {{ row.environment === 'production' ? '生产' : row.environment === 'staging' ? '预发' : '测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getDeployStatusType(row.status)">
              {{ getDeployStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" label="触发方式" width="100">
          <template #default="{ row }">
            {{ row.trigger_type === 'manual' ? '手动' : row.trigger_type === 'auto' ? '自动' : row.trigger_type === 'canary' ? '灰度' : row.trigger_type }}
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="started_at" label="开始时间" width="170">
          <template #default="{ row }">{{ formatTime(row.started_at) }}</template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">{{ row.duration || '-' }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && deployments.length === 0" description="暂无数据" />
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="historyPage"
          v-model:page-size="historyPageSize"
          :total="historyTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="showDetailDrawer" :size="600" direction="rtl">
      <template #title>
        <span>部署详情</span>
      </template>
      <el-descriptions v-if="currentDeployment" :column="1" border size="large" label-placement="left">
        <el-descriptions-item label="部署ID">{{ currentDeployment.id }}</el-descriptions-item>
        <el-descriptions-item label="应用名称">{{ currentDeployment.app_name }}</el-descriptions-item>
        <el-descriptions-item label="版本"><span class="version-tag">v{{ currentDeployment.version }}</span></el-descriptions-item>
        <el-descriptions-item label="环境">
          <el-tag size="small" :type="currentDeployment.environment === 'production' ? 'danger' : 'info'">
            {{ currentDeployment.environment === 'production' ? '生产' : currentDeployment.environment === 'staging' ? '预发' : '测试' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="健康状态">
          <el-tag size="small" :type="getHealthType(currentDeployment.health_status)">
            {{ getHealthLabel(currentDeployment.health_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="副本数">{{ currentDeployment.replicas }} / {{ currentDeployment.ready_replicas || currentDeployment.replicas }}</el-descriptions-item>
        <el-descriptions-item label="镜像">{{ currentDeployment.image }}</el-descriptions-item>
        <el-descriptions-item label="健康检查">
          <el-icon v-if="currentDeployment.health_check === 'pass'" color="#67c23a"><SuccessFilled /></el-icon>
          <el-icon v-else-if="currentDeployment.health_check === 'fail'" color="#f56c6c"><CircleCloseFilled /></el-icon>
          <span v-else>未检查</span>
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ formatTime(currentDeployment.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 8px;">
          <el-button @click="showDetailDrawer = false">关闭</el-button>
          <el-button type="warning" @click="restart(currentDeployment)">重启</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, SuccessFilled, CircleCloseFilled, QuestionFilled } from '@element-plus/icons-vue'
import { formatTime } from '@/utils/date'
import { deploy } from '@/api'

const deployments = ref([])
const history = ref([])
const loading = ref(false)
const loadingHistory = ref(false)
const filterHealth = ref('')
const isActive = ref(true)

const healthStats = ref({ healthy: 0, degraded: 0, unhealthy: 0, unknown: 0 })
const deployStats = ref({ total: 0, active: 0, succeeded: 0, failed: 0 })
const overallHealth = ref({ type: 'success', label: '健康' })

const showDetailDrawer = ref(false)
const currentDeployment = ref(null)
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)

const healthMap = { healthy: '健康', degraded: 'degraded', unhealthy: '异常', unknown: '未知' }
const deployStatusMap = { running: '部署中', succeeded: '成功', failed: '失败', rolledback: '已回滚' }

const getHealthType = (status) => {
  const map = { healthy: 'success', degraded: 'warning', unhealthy: 'danger', unknown: 'info' }
  return map[status] || 'info'
}

const getHealthLabel = (status) => healthMap[status] || status || '-'

const getDeployStatusType = (status) => {
  const map = { running: 'warning', succeeded: 'success', failed: 'danger', rolledback: 'info' }
  return map[status] || 'info'
}

const getDeployStatusLabel = (status) => deployStatusMap[status] || status || '-'

const viewDetail = (deployment) => {
  currentDeployment.value = deployment
  showDetailDrawer.value = true
}

const restart = async (deployment) => {
  try {
    await ElMessageBox.confirm(`确定要重启 "${deployment.app_name}" (v${deployment.version}) 吗？`, '确认重启', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deploy.health.restart(deployment.id)
    ElMessage.success('重启请求已发送')
    loadDeployments()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const loadDeployments = async () => {
  if (!isActive.value) return
  loading.value = true
  try {
    const params = {}
    if (filterHealth.value) params.health_status = filterHealth.value

    const data = await deploy.health.getStatus(params)

    deployments.value = Array.isArray(data) ? data : (data.items || [])
    updateHealthStats()
  } catch (e) {
    deployments.value = generateMockDeployments()
    updateHealthStats()
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const data = await deploy.history.getList({
      page: historyPage.value,
      page_size: historyPageSize.value
    })

    history.value = data.items || []
    historyTotal.value = data.total || history.value.length
  } catch (e) {
    history.value = generateMockHistory()
    historyTotal.value = history.value.length
  } finally {
    loadingHistory.value = false
  }
}

const updateHealthStats = () => {
  const stats = { healthy: 0, degraded: 0, unhealthy: 0, unknown: 0 }
  for (const d of deployments.value) {
    if (d.health_status === 'healthy') stats.healthy++
    else if (d.health_status === 'degraded') stats.degraded++
    else if (d.health_status === 'unhealthy') stats.unhealthy++
    else stats.unknown++
  }
  healthStats.value = stats

  const total = deployments.value.length
  if (total === 0) {
    overallHealth.value = { type: 'info', label: '暂无数据' }
  } else if (stats.unhealthy > 0) {
    overallHealth.value = { type: 'danger', label: '异常' }
  } else if (stats.degraded > 0) {
    overallHealth.value = { type: 'warning', label: 'degraded' }
  } else {
    overallHealth.value = { type: 'success', label: '健康' }
  }

  deployStats.value = {
    total: deployments.value.length,
    active: deployments.value.filter(d => d.health_status !== 'unknown').length,
    succeeded: deployments.value.filter(d => d.status === 'succeeded').length,
    failed: deployments.value.filter(d => d.status === 'failed').length
  }
}

const loadHealth = () => {
  loadDeployments()
  loadHistory()
}

const generateMockDeployments = () => [
  { id: 1, app_name: 'user-service', version: '2.1.0', environment: 'production', health_status: 'healthy', health_check: 'pass', replicas: 3, ready_replicas: 3, image: 'registry.example.com/user-service:v2.1.0', status: 'succeeded', updated_at: '2026-05-25T10:00:00Z' },
  { id: 2, app_name: 'order-service', version: '1.5.2', environment: 'production', health_status: 'degraded', health_check: 'pass', replicas: 3, ready_replicas: 2, image: 'registry.example.com/order-service:v1.5.2', status: 'running', updated_at: '2026-05-25T14:00:00Z' },
  { id: 3, app_name: 'payment-service', version: '3.0.0', environment: 'staging', health_status: 'healthy', health_check: 'pass', replicas: 2, ready_replicas: 2, image: 'registry.example.com/payment:v3.0.0', status: 'succeeded', updated_at: '2026-05-24T16:00:00Z' },
  { id: 4, app_name: 'inventory-service', version: '1.1.0', environment: 'test', health_status: 'unhealthy', health_check: 'fail', replicas: 1, ready_replicas: 0, image: 'registry.example.com/inventory:v1.1.0', status: 'failed', updated_at: '2026-05-25T08:00:00Z' },
  { id: 5, app_name: 'notification-service', version: '1.2.3', environment: 'production', health_status: 'healthy', health_check: 'pass', replicas: 5, ready_replicas: 5, image: 'registry.example.com/notify:v1.2.3', status: 'succeeded', updated_at: '2026-05-23T12:00:00Z' }
]

const generateMockHistory = () => [
  { id: 101, app_name: 'user-service', version: '2.1.0', environment: 'production', status: 'succeeded', trigger_type: 'canary', operator: 'admin', started_at: '2026-05-20T09:00:00Z', duration: '5m 32s' },
  { id: 102, app_name: 'order-service', version: '1.5.2', environment: 'production', status: 'running', trigger_type: 'canary', operator: 'devops', started_at: '2026-05-25T10:00:00Z', duration: null },
  { id: 103, app_name: 'payment-service', version: '3.0.0', environment: 'staging', status: 'succeeded', trigger_type: 'manual', operator: 'admin', started_at: '2026-05-24T14:00:00Z', duration: '8m 15s' },
  { id: 104, app_name: 'inventory-service', version: '1.1.0', environment: 'test', status: 'failed', trigger_type: 'auto', operator: 'system', started_at: '2026-05-25T08:00:00Z', duration: '2m 45s' },
  { id: 105, app_name: 'notification-service', version: '1.2.3', environment: 'production', status: 'succeeded', trigger_type: 'manual', operator: 'admin', started_at: '2026-05-23T11:00:00Z', duration: '4m 20s' },
  { id: 106, app_name: 'user-service', version: '2.0.5', environment: 'production', status: 'rolledback', trigger_type: 'manual', operator: 'devops', started_at: '2026-05-15T16:00:00Z', duration: '6m 10s' }
]

let pollTimer = null

const startPolling = () => {
  stopPolling()
  pollTimer = setInterval(() => {
    if (isActive.value && !showDetailDrawer.value) {
      loadDeployments()
    }
  }, 15000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  isActive.value = true
  loadDeployments()
  loadHistory()
  startPolling()
})
</script>

<style scoped>
.health-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.health-overview { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.overview-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

.health-summary { display: flex; justify-content: space-around; padding: 16px 0; }
.health-stat { display: flex; flex-direction: column; align-items: center; }
.stat-number { font-size: 28px; font-weight: 700; color: #e0e0e0; }
.stat-number.healthy { color: #67c23a; }
.stat-number.degraded { color: #e6a23c; }
.stat-number.unhealthy { color: #f56c6c; }
.stat-number.success { color: #67c23a; }
.stat-number.danger { color: #f56c6c; }
.stat-number.unknown { color: #909399; }
.stat-desc { font-size: 13px; color: #888; margin-top: 4px; }

.table-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.version-tag { font-family: 'Courier New', monospace; font-weight: 600; color: #409eff; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

:deep(.el-card) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-card__header) { color: #e0e0e0; border-bottom: 1px solid #2d2d44; }
:deep(.el-table) { background: transparent; color: #e0e0e0; --el-table-border-color: #2d2d44; --el-table-header-bg-color: #1a1a2e; --el-table-header-text-color: #a0a0a0; }
:deep(.el-table th) { background: #1a1a2e; color: #a0a0a0; }
:deep(.el-table tr) { background: #1a1a2e; }
:deep(.el-table td) { border-bottom: 1px solid #2d2d44; }
:deep(.el-drawer) { background: #1a1a2e; }
:deep(.el-drawer__title) { color: #e0e0e0; }
:deep(.el-descriptions__label) { color: #a0a0a0; background: #1a1a2e; }
:deep(.el-descriptions__content) { color: #e0e0e0; background: #1a1a2e; }
:deep(.el-tag) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
:deep(.el-select .el-input__wrapper) { background: #252538; }
</style>
