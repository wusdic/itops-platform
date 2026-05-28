<template>
  <div class="alerts-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">告警管理</h1>
        <p class="page-subtitle">监控系统告警信息</p>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="alert-stats">
      <div class="stat-badge critical" @click="quickFilter('critical')">
        <span class="stat-count">{{ alertStats.critical }}</span>
        <span class="stat-label">严重</span>
      </div>
      <div class="stat-badge warning" @click="quickFilter('warning')">
        <span class="stat-count">{{ alertStats.warning }}</span>
        <span class="stat-label">警告</span>
      </div>
      <div class="stat-badge info" @click="quickFilter('info')">
        <span class="stat-count">{{ alertStats.info }}</span>
        <span class="stat-label">提示</span>
      </div>
      <div class="stat-badge active" @click="quickFilter('active')">
        <span class="stat-count">{{ alertStats.active }}</span>
        <span class="stat-label">待处理</span>
      </div>
      <div class="update-time">
        <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
        <span v-else-if="lastUpdateTime">最后更新: {{ lastUpdateTime }}</span>
        <span v-else>加载中...</span>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-space :size="12" align="center">
        <el-select v-model="filterLevel" :options="levelOptions" placeholder="告警级别" clearable style="width: 130px" @change="onFilterChange" />
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="处理状态" clearable style="width: 130px" @change="onFilterChange" />
        <el-button type="primary" :loading="loading" @click="loadAlerts">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </el-space>
    </div>

    <!-- Alert Table -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <span>告警列表 <span class="table-count">共 {{ total }} 条</span></span>
      </template>
      <el-table
        :data="alerts"
        v-loading="loading"
        :row-key="row => row.id"
        :row-class-name="getRowClassName"
        :border="false"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="告警名称" :show-overflow-tooltip="true" />
        <el-table-column prop="level" label="级别" width="90">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">{{ getLevelLabel(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_name" label="设备" :show-overflow-tooltip="true" width="140" />
        <el-table-column prop="occurred_at" label="发生时间" width="170">
          <template #default="{ row }">{{ formatTime(row.occurred_at || row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" :disabled="row.status === 'resolved' || actionLoading" @click="openDetail(row)">查看</el-button>
              <el-button v-if="row.status === 'active'" type="warning" link size="small" :disabled="actionLoading" @click="handleAcknowledge(row)">确认</el-button>
              <el-button v-if="row.status !== 'resolved'" type="success" link size="small" :disabled="actionLoading" @click="handleResolve(row)">解决</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && alerts.length === 0" description="暂无数据" />
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadAlerts"
          @current-change="loadAlerts"
        />
      </div>
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="showDrawer" :size="720" direction="rtl">
      <template #title>
        <span>告警详情</span>
      </template>
      <el-descriptions v-if="currentAlert" :column="1" border size="large" label-placement="left">
        <el-descriptions-item label="告警ID">{{ currentAlert.id }}</el-descriptions-item>
        <el-descriptions-item label="告警名称">{{ currentAlert.title }}</el-descriptions-item>
        <el-descriptions-item label="告警级别">
          <el-tag :type="getLevelType(currentAlert.level)" size="small">{{ getLevelLabel(currentAlert.level) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(currentAlert.status)" size="small">{{ getStatusLabel(currentAlert.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备">{{ currentAlert.device_name }} ({{ currentAlert.device_ip }})</el-descriptions-item>
        <el-descriptions-item label="告警信息">{{ currentAlert.message }}</el-descriptions-item>
        <el-descriptions-item label="发生时间">{{ formatTime(currentAlert.occurred_at || currentAlert.created_at) }}</el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.acknowledged_at" label="确认时间">{{ formatTime(currentAlert.acknowledged_at) }}</el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.resolved_at" label="解决时间">{{ formatTime(currentAlert.resolved_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 8px;">
          <el-button @click="showDrawer = false">关闭</el-button>
          <el-button v-if="currentAlert && currentAlert.status === 'active'" type="warning" :loading="actionLoading" @click="handleAcknowledge(currentAlert)">确认</el-button>
          <el-button v-if="currentAlert && currentAlert.status !== 'resolved'" type="primary" :loading="actionLoading" @click="handleResolve(currentAlert)">标记已解决</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { formatDate, formatTime } from '@/utils/date'
import * as monitoring from '@/api/monitoring'

const alerts = ref([])
const alertStats = ref({ critical: 0, warning: 0, info: 0, active: 0 })
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showDrawer = ref(false)
const currentAlert = ref(null)
const filterLevel = ref(null)
const filterStatus = ref(null)
const actionLoading = ref(false)
const lastUpdateTime = ref('')
const isActive = ref(true)

const levelOptions = [
  { label: '严重', value: 'critical' },
  { label: '高', value: 'high' },
  { label: '警告', value: 'medium' },
  { label: '低', value: 'low' },
  { label: '提示', value: 'info' }
]

const statusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已确认', value: 'acknowledged' },
  { label: '已解决', value: 'resolved' }
]

const levelMap = { critical: '严重', high: '高', medium: '警告', low: '低', info: '提示' }
const statusMap = { active: '活跃', acknowledged: '已确认', resolved: '已解决' }

const getLevelType = (level) => {
  if (!level) return 'info'
  const map = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info', info: 'info' }
  return map[level] || 'info'
}
const getStatusType = (status) => {
  if (!status) return 'info'
  const map = { active: 'warning', acknowledged: 'info', resolved: 'success' }
  return map[status] || 'info'
}
const getLevelLabel = (level) => levelMap[level] || level || '-'
const getStatusLabel = (status) => statusMap[status] || status || '-'

const getRowClassName = ({ row }) => {
  if (!row) return ''
  if (row.status === 'active') return 'row-active'
  if (row.status === 'acknowledged') return 'row-acknowledged'
  if (row.status === 'resolved') return 'row-resolved'
  return ''
}

const openDetail = (alert) => {
  currentAlert.value = alert
  showDrawer.value = true
}

const onFilterChange = () => {
  page.value = 1
  loadAlertStats()
  loadAlerts()
}

async function loadAlertStats() {
  try {
    const params = {}
    if (filterLevel.value) params.severity = filterLevel.value
    if (filterStatus.value) params.status = filterStatus.value
    const data = await monitoring.alerts.getList(params)
    let items = []
    if (Array.isArray(data)) {
      items = data
    } else if (data.items) {
      items = data.items || []
    }
    const stats = { critical: 0, warning: 0, info: 0, active: 0 }
    for (const alert of items) {
      if (alert.level === 'critical' || alert.level === 'high') stats.critical++
      else if (alert.level === 'medium') stats.warning++
      else if (alert.level === 'info' || alert.level === 'low') stats.info++
      if (alert.status === 'active' || alert.status === 'acknowledged') stats.active++
    }
    alertStats.value = stats
  } catch (e) { /* silent */ }
}

const quickFilter = (type) => {
  if (type === 'critical') {
    filterLevel.value = (filterLevel.value === 'critical' || filterLevel.value === 'high') ? null : 'critical'
  } else if (type === 'warning') {
    filterLevel.value = filterLevel.value === 'medium' ? null : 'medium'
  } else if (type === 'info') {
    filterLevel.value = filterLevel.value === 'info' ? null : 'info'
  } else if (type === 'active') {
    filterStatus.value = filterStatus.value === 'active' ? null : 'active'
  }
  onFilterChange()
}

const handleAcknowledge = async (alert) => {
  ElMessageBox.confirm(`确定要确认告警"${alert.title}"吗？`, '确认操作', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    actionLoading.value = true
    try {
      await monitoring.alerts.update(alert.id, { acknowledged: true })
      ElMessage.success('告警已确认')
      showDrawer.value = false
      loadAlerts()
    } catch (e) {
      ElMessage.error(e.message || '确认告警失败')
    } finally {
      actionLoading.value = false
    }
  }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

const handleResolve = async (alert) => {
  ElMessageBox.confirm(`确定要解决告警"${alert.title}"吗？`, '确认操作', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    actionLoading.value = true
    try {
      await monitoring.alerts.update(alert.id, { resolved: true })
      ElMessage.success('告警已解决')
      showDrawer.value = false
      loadAlerts()
    } catch (e) {
      ElMessage.error(e.message || '解决告警失败')
    } finally {
      actionLoading.value = false
    }
  }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

const loadAlerts = async () => {
  if (!isActive.value) return
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filterLevel.value) params.severity = filterLevel.value
    if (filterStatus.value) params.status = filterStatus.value

    const data = await monitoring.alerts.getList(params)

    if (!isActive.value) return

    let items = []
    let totalCount = 0
    if (Array.isArray(data)) {
      items = data
      totalCount = data.length
    } else if (data.items) {
      items = data.items || []
      totalCount = data.total || items.length
    } else if (data.data?.items) {
      items = data.data.items
      totalCount = data.data.total || items.length
    }

    alerts.value = items
    total.value = totalCount
    if (page.value > Math.max(1, Math.ceil((totalCount || 0) / (pageSize.value || 1)))) {
      page.value = 1
    }
  } catch (e) {
    if (isActive.value) {
      ElMessage.error('加载告警列表失败')
    }
  } finally {
    if (isActive.value) {
      loading.value = false
      lastUpdateTime.value = formatDate(new Date(), 'HH:mm:ss')
    }
  }
}

let pollTimer = null

const startPolling = () => {
  stopPolling()
  pollTimer = setInterval(() => {
    if (!showDrawer.value && isActive.value) {
      loadAlerts()
    }
  }, 30000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  isActive.value = true
  loadAlertStats()
  loadAlerts()
  startPolling()
})

onBeforeUnmount(() => {
  isActive.value = false
  showDrawer.value = false
  stopPolling()
})
</script>

<style scoped>
.alerts-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #303133; margin: 0; }
.page-subtitle { font-size: 14px; color: #909399; margin: 4px 0 0 0; }

.alert-stats {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px; flex-wrap: wrap;
}

.stat-badge {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 6px;
  cursor: pointer; transition: all 0.2s;
}
.stat-badge:hover { transform: translateY(-1px); }
.stat-badge.critical { background: #fff1f0; border: 1px solid #ffccc7; }
.stat-badge.warning { background: #fff7e6; border: 1px solid #ffe58f; }
.stat-badge.info { background: #e8f4ff; border: 1px solid #adc6ff; }
.stat-badge.active { background: #f0f5ff; border: 1px solid #adc6ff; }
.stat-count { font-size: 20px; font-weight: 700; }
.stat-badge.critical .stat-count { color: #f53f3f; }
.stat-badge.warning .stat-count { color: #ff7d00; }
.stat-badge.info .stat-count { color: #165dff; }
.stat-badge.active .stat-count { color: #165dff; }
.stat-label { font-size: 13px; color: #606266; }

.update-time {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #909399; margin-left: auto; min-height: 20px;
}
.update-time .is-loading { animation: rotating 2s linear infinite; }
@keyframes rotating { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.filter-bar { margin-bottom: 12px; }
.table-count { font-size: 13px; color: #909399; font-weight: normal; margin-left: 8px; }

.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

:deep(.row-active) { background-color: #fff2f0 !important; border-left: 3px solid #f53f3f; }
:deep(.row-acknowledged) { background-color: #fffbe6 !important; border-left: 3px solid #ff7d00; }
:deep(.row-resolved) { background-color: #f5f5f5 !important; border-left: 3px solid #52c41a; color: #909399; }
</style>
