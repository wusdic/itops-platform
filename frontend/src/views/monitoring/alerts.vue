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
        <n-spin v-if="loading" :size="14" stroke-width="20" />
        <span v-else-if="lastUpdateTime">最后更新: {{ lastUpdateTime }}</span>
        <span v-else>加载中...</span>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <n-space :size="12" align="center">
        <n-select v-model:value="filterLevel" :options="levelOptions" placeholder="告警级别" clearable style="width: 130px" @update:value="onFilterChange" />
        <n-select v-model:value="filterStatus" :options="statusOptions" placeholder="处理状态" clearable style="width: 130px" @update:value="onFilterChange" />
        <n-button type="primary" :loading="loading" @click="loadAlerts">
          <template #icon><n-icon><Refresh /></n-icon></template>
          刷新
        </n-button>
      </n-space>
    </div>

    <!-- Alert Table -->
    <n-card :bordered="false" class="table-card">
      <template #header>
        <span>告警列表 <span class="table-count">共 {{ total }} 条</span></span>
      </template>
      <n-data-table
        :columns="columns"
        :data="alerts"
        :loading="loading"
        :pagination="getPaginationConfig()"
        :key="paginationVersion"
        :row-key="row => row.id"
        :row-class-name="getRowClassName"
        :bordered="false"
        :remote="true"
        :single-line="false"
      />
    </n-card>

    <!-- Detail Drawer -->
    <n-drawer v-model:show="showDrawer" :width="720" placement="right">
      <n-drawer-content title="告警详情">
        <n-descriptions v-if="currentAlert" :column="1" label-placement="left" bordered size="large">
          <n-descriptions-item label="告警ID">{{ currentAlert.id }}</n-descriptions-item>
          <n-descriptions-item label="告警名称">{{ currentAlert.title }}</n-descriptions-item>
          <n-descriptions-item label="告警级别">
            <n-tag :type="getLevelType(currentAlert.level)" size="small">{{ getLevelLabel(currentAlert.level) }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="处理状态">
            <n-tag :type="getStatusType(currentAlert.status)" size="small">{{ getStatusLabel(currentAlert.status) }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="设备">{{ currentAlert.device_name }} ({{ currentAlert.device_ip }})</n-descriptions-item>
          <n-descriptions-item label="告警信息">{{ currentAlert.message }}</n-descriptions-item>
          <n-descriptions-item label="发生时间">{{ formatTime(currentAlert.occurred_at || currentAlert.created_at) }}</n-descriptions-item>
          <n-descriptions-item v-if="currentAlert.acknowledged_at" label="确认时间">{{ formatTime(currentAlert.acknowledged_at) }}</n-descriptions-item>
          <n-descriptions-item v-if="currentAlert.resolved_at" label="解决时间">{{ formatTime(currentAlert.resolved_at) }}</n-descriptions-item>
        </n-descriptions>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showDrawer = false">关闭</n-button>
            <n-button v-if="currentAlert && currentAlert.status === 'active'" type="warning" :loading="actionLoading" @click="handleAcknowledge(currentAlert)">确认</n-button>
            <n-button v-if="currentAlert && currentAlert.status !== 'resolved'" type="primary" :loading="actionLoading" @click="handleResolve(currentAlert)">标记已解决</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watchEffect } from 'vue'
import {
  NCard, NDataTable, NButton, NSpace, NSelect, NDrawer, NDrawerContent,
  NDescriptions, NDescriptionsItem, NTag, NIcon, NSpin, useMessage, useDialog
} from 'naive-ui'
import { Refresh } from '@vicons/ionicons5'
import { formatDate, formatTime } from '@/utils/date'

// ── 所有组件调用必须在 setup 顶层 ──────────────────────────────
const message = useMessage()
const dialog = useDialog()

const alerts = ref([])
const alertStats = ref({ critical: 0, warning: 0, info: 0, active: 0 })
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const itemCountRef = ref(0)
const pageCountRef = ref(1)
const paginationVersion = ref(0)
// 共享纯 JS 对象 — getPaginationConfig() 每次返回同一引用，Naive UI 内部 Object.assign 作用在同一对象上
const paginationConfig = {
  page: 1,
  pageSize: 20,
  pageCount: 1,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (p) => {
    page.value = p
    paginationConfig.page = p
    paginationVersion.value++
    loadAlerts()
  },
  onUpdatePageSize: (s) => {
    pageSize.value = s
    page.value = 1
    paginationConfig.pageSize = s
    paginationConfig.page = 1
    paginationVersion.value++
    loadAlerts()
  }
}
// watchEffect 主动同步：total/page/pageSize 变化时 Naive UI 收到最新值
watchEffect(() => {
  paginationConfig.page = page.value
  paginationConfig.pageSize = pageSize.value
  paginationConfig.total = total.value
  paginationConfig.itemCount = total.value
  paginationConfig.pageCount = Math.max(1, Math.ceil((total.value || 0) / (pageSize.value || 1)))
})

const getPaginationConfig = () => paginationConfig

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
  if (!level) return 'default'
  const map = { critical: 'error', high: 'error', medium: 'warning', low: 'info', info: 'info' }
  return map[level] || 'default'
}
const getStatusType = (status) => {
  if (!status) return 'default'
  const map = { active: 'warning', acknowledged: 'info', resolved: 'success' }
  return map[status] || 'default'
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

// ── columns 用 defineColumns 风格在 setup 内定义 ──────────────────
const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '告警名称', key: 'title', ellipsis: { tooltip: true } },
  {
    title: '级别', key: 'level', width: 90,
    render: (row) => {
      if (!row) return null
      return h(NTag, { type: getLevelType(row.level), size: 'small' }, () => getLevelLabel(row.level))
    }
  },
  {
    title: '状态', key: 'status', width: 90,
    render: (row) => {
      if (!row) return null
      return h(NTag, { type: getStatusType(row.status), size: 'small' }, () => getStatusLabel(row.status))
    }
  },
  { title: '设备', key: 'device_name', ellipsis: { tooltip: true }, width: 140 },
  {
    title: '发生时间', key: 'occurred_at', width: 170,
    render: (row) => {
      if (!row) return null
      return formatTime(row.occurred_at || row.created_at)
    }
  },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row) => {
      if (!row) return null
      const buttons = []
      // 查看按钮
      buttons.push(h(NButton, {
        size: 'small',
        type: 'primary',
        ghost: true,
        disabled: row.status === 'resolved' || actionLoading.value,
        onClick: () => openDetail(row)
      }, () => '查看'))
      // 确认按钮
      if (row.status === 'active') {
        buttons.push(h(NButton, {
          size: 'small',
          type: 'warning',
          disabled: actionLoading.value,
          onClick: () => handleAcknowledge(row)
        }, () => '确认'))
      }
      // 解决按钮
      if (row.status !== 'resolved') {
        buttons.push(h(NButton, {
          size: 'small',
          type: 'success',
          disabled: actionLoading.value,
          onClick: () => handleResolve(row)
        }, () => '解决'))
      }
      return h(NSpace, { size: 'small' }, () => buttons)
    }
  }
]

const openDetail = (alert) => {
  currentAlert.value = alert
  showDrawer.value = true
}

const onFilterChange = () => {
  page.value = 1
  loadAlertStats()      // 筛选变化时重新加载统计
  loadAlerts()
}

// 独立加载告警统计（从专用 stats API，不依赖当前页数据）
async function loadAlertStats() {
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams()
    if (filterLevel.value) params.append('severity', filterLevel.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    const res = await fetch(`/api/v1/monitoring/alerts?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) return
    const data = await res.json()
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
  dialog.warning({
    title: '确认操作',
    content: `确定要确认告警"${alert.title}"吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      actionLoading.value = true
      try {
        const token = localStorage.getItem('token') || ''
        const res = await fetch(`/api/v1/monitoring/alerts/${alert.id}/acknowledge`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        })
        if (res.status === 401) {
          message.warning('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          return
        }
        if (res.ok) {
          message.success('告警已确认')
          showDrawer.value = false
          loadAlerts()
        } else {
          const err = await res.json().catch(() => ({}))
          message.error(err.message || '确认告警失败')
        }
      } catch (e) {
        message.error('确认告警失败')
      } finally {
        actionLoading.value = false
      }
    }
  })
}

const handleResolve = async (alert) => {
  dialog.warning({
    title: '确认操作',
    content: `确定要解决告警"${alert.title}"吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      actionLoading.value = true
      try {
        const token = localStorage.getItem('token') || ''
        const res = await fetch(`/api/v1/monitoring/alerts/${alert.id}/resolve`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        })
        if (res.status === 401) {
          message.warning('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          return
        }
        if (res.ok) {
          message.success('告警已解决')
          showDrawer.value = false
          loadAlerts()
        } else {
          const err = await res.json().catch(() => ({}))
          message.error(err.message || '解决告警失败')
        }
      } catch (e) {
        message.error('解决告警失败')
      } finally {
        actionLoading.value = false
      }
    }
  })
}

const loadAlerts = async () => {
  if (!isActive.value) return
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams()
    params.append('page', page.value)
    params.append('page_size', pageSize.value)
    if (filterLevel.value) params.append('severity', filterLevel.value)
    if (filterStatus.value) params.append('status', filterStatus.value)

    const res = await fetch(`/api/v1/monitoring/alerts?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.status === 401) {
      message.warning('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
      return
    }

    if (!res.ok) {
      message.error(`加载失败: HTTP ${res.status}`)
      return
    }

    const data = await res.json()

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

    // Stats are loaded separately by loadAlertStats(), not from current page data
    alerts.value = items
    total.value = totalCount
    itemCountRef.value = totalCount
    pageCountRef.value = Math.max(1, Math.ceil((totalCount || 0) / (pageSize.value || 1)))
    paginationVersion.value++
    // Ensure current page doesn't exceed total
    if (page.value > pageCountRef.value) {
      page.value = 1
    }
  } catch (e) {
    if (isActive.value) {
      message.error('加载告警列表失败')
      console.error('loadAlerts error:', e)
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
.update-time .n-spin { flex-shrink: 0; }

.filter-bar { margin-bottom: 12px; }
.table-count { font-size: 13px; color: #909399; font-weight: normal; margin-left: 8px; }

:deep(.row-active) { background-color: #fff2f0 !important; border-left: 3px solid #f53f3f; }
:deep(.row-acknowledged) { background-color: #fffbe6 !important; border-left: 3px solid #ff7d00; }
:deep(.row-resolved) { background-color: #f5f5f5 !important; border-left: 3px solid #52c41a; color: #909399; }
</style>
