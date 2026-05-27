<template>
  <div class="page-container">
    <!-- 自定义工具栏 -->
    <div class="dashboard-toolbar">
      <el-space>
        <el-button type="primary" plain size="small" @click="showCustomize = !showCustomize">
          <el-icon><Setting /></el-icon> 自定义布局
        </el-button>
        <el-button size="small" @click="resetLayout" :disabled="saving">
          <el-icon><RefreshRight /></el-icon> 重置默认
        </el-button>
        <el-button type="success" size="small" @click="saveLayout" :disabled="saving || !layoutModified">
          <el-icon v-if="saving"><Loading /></el-icon>
          <el-icon v-else><Check /></el-icon> {{ saving ? '保存中...' : '保存布局' }}
        </el-button>
      </el-space>
      <el-tag v-if="layoutModified" type="warning" size="small">有未保存的更改</el-tag>
    </div>

    <!-- Loading State -->
    <div v-loading="loading" class="loading-container" :element-loading-text="'加载数据中...'">

      <!-- 统计卡片（始终显示） -->
      <el-row :gutter="16" class="stats-grid">
        <el-col :xs="24" :sm="12" :md="6" v-for="(item, idx) in statWidgets" :key="item.item_id">
          <!-- 自定义模式：可拖拽/隐藏/折叠 -->
          <div v-if="showCustomize" class="widget-control">
            <el-button-group size="small">
              <el-button @click="toggleVisibility(item)" :type="item.visibility === false ? 'info' : 'default'" :icon="item.visibility === false ? 'Hide' : 'View'"></el-button>
              <el-button @click="toggleCollapse(item)" :type="item.collapsed ? 'warning' : 'default'" :icon="item.collapsed ? 'DArrowRight' : 'DArrowLeft'"></el-button>
            </el-button-group>
          </div>
          <div v-show="item.visibility !== false && !item.collapsed" class="stat-card" :style="{ borderLeftColor: statCardColors[idx] }" @click="handleStatClick(item.widget?.metric_names?.[0])">
            <div class="stat-icon-wrap" :style="{ background: statCardBgColors[idx] }">
              <el-icon :size="24" :color="statCardColors[idx]">
                <component :is="statIcons[idx]" />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statCardValues[idx] }}</div>
              <div class="stat-label">{{ item.widget?.title || statLabels[idx] }}</div>
            </div>
          </div>
          <div v-show="item.visibility !== false && item.collapsed" class="stat-card collapsed" :style="{ borderLeftColor: statCardColors[idx] }">
            <span class="collapsed-hint">{{ item.widget?.title || statLabels[idx] }}: {{ statCardValues[idx] }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- 系统健康状态 -->
      <div v-if="healthWidget && (healthWidget.visibility !== false)" class="health-card" v-show="!healthWidget.collapsed">
        <div v-if="showCustomize" class="widget-control inline">
          <el-button-group size="small">
            <el-button @click="toggleCollapse(healthWidget)" :type="healthWidget.collapsed ? 'warning' : 'default'" :icon="healthWidget.collapsed ? 'DArrowRight' : 'DArrowLeft'"></el-button>
          </el-button-group>
        </div>
        <div class="health-header">
          <span class="card-title">系统健康状态</span>
          <el-tag :type="healthType" size="small">{{ healthText }}</el-tag>
        </div>
        <div class="health-body" v-show="!healthWidget.collapsed">
          <el-space :size="20" alignment="normal" style="width: 100%; justify-content: space-between;">
            <div class="health-item">
              <span class="health-label">CPU使用率</span>
              <el-progress :percentage="systemHealth.cpu" :status="getProgressStatus(systemHealth.cpu)" :stroke-width="10" />
            </div>
            <div class="health-item">
              <span class="health-label">内存使用率</span>
              <el-progress :percentage="systemHealth.memory" :status="getProgressStatus(systemHealth.memory)" :stroke-width="10" />
            </div>
            <div class="health-item">
              <span class="health-label">磁盘使用率</span>
              <el-progress :percentage="systemHealth.disk" :status="getProgressStatus(systemHealth.disk)" :stroke-width="10" />
            </div>
          </el-space>
        </div>
      </div>

      <!-- 图表区域 -->
      <el-row :gutter="16" class="chart-grid">
        <el-col :xs="24" :md="12" v-for="item in chartWidgets" :key="item.item_id">
          <div v-if="showCustomize" class="widget-control inline">
            <el-button-group size="small">
              <el-button @click="toggleVisibility(item)" :type="item.visibility === false ? 'info' : 'default'" :icon="item.visibility === false ? 'Hide' : 'View'"></el-button>
              <el-button @click="toggleCollapse(item)" :type="item.collapsed ? 'warning' : 'default'" :icon="item.collapsed ? 'DArrowRight' : 'DArrowLeft'"></el-button>
            </el-button-group>
          </div>
          <div v-show="item.visibility !== false && !item.collapsed" class="card">
            <div class="card-header">
              <span class="card-title">{{ item.widget?.title || '图表' }}</span>
              <el-space>
                <template v-if="item.widget?.widget_type === 'alert_chart'">
                  <el-tag type="danger" size="small">严重 {{ alertStats.critical }}</el-tag>
                  <el-tag type="warning" size="small">警告 {{ alertStats.warning }}</el-tag>
                  <el-tag type="info" size="small">提示 {{ alertStats.info }}</el-tag>
                </template>
                <template v-else-if="item.widget?.widget_type === 'device_status_chart'">
                  <el-tag type="success" size="small">在线 {{ deviceStats.online }}</el-tag>
                  <el-tag size="small">离线 {{ deviceStats.offline }}</el-tag>
                  <el-tag type="warning" size="small">告警 {{ deviceStats.warning }}</el-tag>
                </template>
              </el-space>
            </div>
            <div class="card-body">
              <div v-if="item.widget?.widget_type === 'alert_chart'" ref="alertChartRef" class="chart-container"></div>
              <div v-else-if="item.widget?.widget_type === 'device_status_chart'" ref="deviceChartRef" class="chart-container"></div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 表格区域 -->
      <el-row :gutter="16" class="table-grid">
        <el-col :xs="24" :md="12" v-for="item in tableWidgets" :key="item.item_id">
          <div v-if="showCustomize" class="widget-control inline">
            <el-button-group size="small">
              <el-button @click="toggleVisibility(item)" :type="item.visibility === false ? 'info' : 'default'" :icon="item.visibility === false ? 'Hide' : 'View'"></el-button>
              <el-button @click="toggleCollapse(item)" :type="item.collapsed ? 'warning' : 'default'" :icon="item.collapsed ? 'DArrowRight' : 'DArrowLeft'"></el-button>
            </el-button-group>
          </div>
          <div v-show="item.visibility !== false && !item.collapsed" class="card">
            <div class="card-header">
              <span class="card-title">{{ item.widget?.title || '表格' }}</span>
              <el-button v-if="item.widget?.widget_type === 'recent_alerts_table'" type="primary" text @click="$router.push('/monitoring/alerts')">查看更多</el-button>
              <el-button v-else-if="item.widget?.widget_type === 'pending_workorders_table'" type="primary" text @click="$router.push('/workorder/list')">查看更多</el-button>
            </div>
            <div class="card-body">
              <el-table v-if="item.widget?.widget_type === 'recent_alerts_table'" :data="recentAlerts" :border="false" size="small" v-loading="alertsLoading">
                <el-table-column v-for="col in alertColumns" :key="col.key" :="col" />
              </el-table>
              <el-table v-else-if="item.widget?.widget_type === 'pending_workorders_table'" :data="pendingOrders" :border="false" size="small" v-loading="workordersLoading">
                <el-table-column v-for="col in workorderColumns" :key="col.key" :="col" />
              </el-table>
              <el-empty v-if="((item.widget?.widget_type === 'recent_alerts_table' && !alertsLoading && recentAlerts.length === 0) || (item.widget?.widget_type === 'pending_workorders_table' && !workordersLoading && pendingOrders.length === 0))" description="暂无数据" />
            </div>
          </div>
        </el-col>
      </el-row>

    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="error-state">
      <el-result icon="error" title="加载失败" :subTitle="error">
        <template #extra>
          <el-button @click="loadDashboard">重试</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, h, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Monitor,
  Warning,
  Ticket,
  CircleCheck,
  CloseBold,
  WarningFilled,
  Setting,
  RefreshRight,
  Check,
  Loading,
  View,
  Hide,
  DArrowLeft,
  DArrowRight
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import { devices, alerts, workorder } from '@/api'
import { performance as monitorApi } from '@/api/monitoring'
import { ElMessage } from 'element-plus'

const message = ElMessage
const alertChartRef = ref(null)
const deviceChartRef = ref(null)
let alertChart = null
let deviceChart = null

// Loading states
const loading = ref(false)
const alertsLoading = ref(false)
const workordersLoading = ref(false)

// Error handling
const error = ref(null)

// Layout state
const showCustomize = ref(false)
const saving = ref(false)
const layoutModified = ref(false)
const currentLayout = ref(null)
const layoutId = ref(null)

// Stat card data
const statCardColors = ['#165dff', '#00b42a', '#ff7d00', '#f53f3f']
const statCardBgColors = ['#e8f0ff', '#e8ffea', '#fff7e6', '#fff1f0']
const statIcons = [Monitor, CircleCheck, Warning, Ticket]
const statLabels = ['设备总数', '在线设备', '告警数量', '待办工单']
const statCardValues = ref([0, 0, 0, 0])

// Alert statistics
const alertStats = reactive({ critical: 0, warning: 0, info: 0 })

// Device statistics
const deviceStats = reactive({ online: 0, offline: 0, warning: 0 })

// System health
const systemHealth = ref(null)

// Tables data
const recentAlerts = ref([])
const pendingOrders = ref([])

// Widget collections from layout API
const allItems = ref([])

const statWidgets = computed(() => allItems.value.filter(i => i.widget?.widget_type?.startsWith('stat_')))
const healthWidget = computed(() => allItems.value.find(i => i.widget?.widget_type === 'health_status'))
const chartWidgets = computed(() => allItems.value.filter(i => ['alert_chart', 'device_status_chart'].includes(i.widget?.widget_type)))
const tableWidgets = computed(() => allItems.value.filter(i => ['recent_alerts_table', 'pending_workorders_table'].includes(i.widget?.widget_type)))

// Alert severity type map
const severityTypeMap = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info', info: 'info' }
const severityTextMap = { critical: '严重', high: '高', medium: '中', low: '低', info: '提示' }
const severityOrder = ['critical', 'high', 'medium', 'low', 'info']

// Workorder priority type map
const priorityTypeMap = { urgent: 'danger', high: 'warning', medium: 'info', low: 'info' }
const priorityTextMap = { urgent: '紧急', high: '高', medium: '中', low: '低' }

const alertColumns = [
  {
    title: '级别',
    key: 'severity',
    width: 80,
    render(row) {
      const type = severityTypeMap[row.severity] || 'info'
      const text = severityTextMap[row.severity] || row.severity || '未知'
      return h(ElTag, { type, size: 'small' }, () => text)
    }
  },
  { title: '告警信息', key: 'message', showOverflowTooltip: true },
  {
    title: '时间',
    key: 'created_at',
    width: 160,
    render(row) {
      if (!row.created_at) return '-'
      return formatDate(new Date(row.created_at))
    }
  }
]

const workorderColumns = [
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render(row) {
      const type = priorityTypeMap[row.priority] || 'info'
      const text = priorityTextMap[row.priority] || row.priority || '普通'
      return h(ElTag, { type, size: 'small' }, () => text)
    }
  },
  { title: '工单标题', key: 'title', showOverflowTooltip: true },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const statusMap = {
        pending: { type: 'warning', text: '待处理' },
        processing: { type: 'info', text: '处理中' },
        resolved: { type: 'success', text: '已解决' },
        closed: { type: 'info', text: '已关闭' }
      }
      const status = statusMap[row.status] || { type: 'info', text: row.status || '-' }
      return h(ElTag, { type: status.type, size: 'small' }, () => status.text)
    }
  }
]

// Health status helpers
const getProgressStatus = (value) => {
  if (value >= 90) return 'exception'
  if (value >= 70) return 'warning'
  return 'success'
}

const healthType = computed(() => {
  if (!systemHealth.value) return 'info'
  const { cpu, memory, disk } = systemHealth.value
  if (cpu >= 90 || memory >= 90 || disk >= 90) return 'danger'
  if (cpu >= 70 || memory >= 70 || disk >= 70) return 'warning'
  return 'success'
})

const healthText = computed(() => {
  if (!systemHealth.value) return '未知'
  const { cpu, memory, disk } = systemHealth.value
  if (cpu >= 90 || memory >= 90 || disk >= 90) return '危险'
  if (cpu >= 70 || memory >= 70 || disk >= 70) return '警告'
  return '正常'
})

// API call with 3-level error handling
const fetchWithErrorHandling = async (apiCall, fallback = null, showError = true) => {
  try {
    const result = await apiCall()
    return result
  } catch (err) {
    if (err.response) {
      const status = err.response.status
      if (status === 401) {
        message.warning('登录已过期，请重新登录')
        localStorage.removeItem('token')
        window.location.href = '/login'
        return fallback
      }
      if (status === 403) {
        message.warning('没有权限访问')
        return fallback
      }
      if (showError && err.response.data?.msg) {
        message.error(err.response.data.msg)
      }
    } else if (err.request) {
      if (showError) {
        message.error('网络连接失败，请检查网络')
      }
    }
    return fallback
  }
}

// Load layout from API then load dashboard data
const loadDashboard = async () => {
  loading.value = true
  error.value = null

  try {
    // Step 1: Load layout from API (MON-032)
    try {
      const layoutRes = await monitorApi.getDashboardLayout()
      if (layoutRes && layoutRes.items) {
        const layout = layoutRes
        currentLayout.value = layout
        layoutId.value = layout.layout_id
        allItems.value = (layout.items || []).map(item => ({
          ...item,
          collapsed: item.collapsed || false,
          visibility: item.visibility !== false
        }))
      }
    } catch (e) {
      console.warn('Failed to load layout, using defaults:', e)
      allItems.value = []
    }

    // Step 2: Load dashboard data in parallel
    const [statsRes, alertRes, workorderRes, healthRes] = await Promise.allSettled([
      fetchWithErrorHandling(() => devices.getStats(), { total: 0, online: 0, offline: 0, warning: 0 }),
      fetchWithErrorHandling(() => alerts.getList({ page: 1, page_size: 10 }), { items: [], total: 0 }),
      fetchWithErrorHandling(() => workorder.getList({ page: 1, page_size: 10, status: 'pending' }), { items: [], total: 0 }),
      fetchWithErrorHandling(() => devices.getStats(), null, false)
    ])

    // Process device stats
    if (statsRes.status === 'fulfilled' && statsRes.value) {
      const data = statsRes.value
      if (typeof data.total === 'number') {
        statCardValues.value = [
          data.total,
          data.online || 0,
          statCardValues.value[2], // will update below from alerts
          data.pending_orders || 0
        ]
        deviceStats.online = data.online || 0
        deviceStats.offline = data.offline || 0
      }
    }

    // Process alerts
    if (alertRes.status === 'fulfilled' && alertRes.value) {
      const data = alertRes.value
      const items = Array.isArray(data) ? data : (data.items || [])
      recentAlerts.value = items.slice(0, 10)
      alertStats.critical = items.filter(a => ['critical', 'high'].includes(a.severity)).length
      alertStats.warning = items.filter(a => ['medium', 'warning'].includes(a.severity)).length
      alertStats.info = items.filter(a => ['low', 'info'].includes(a.severity)).length
      statCardValues.value[2] = items.length
      deviceStats.warning = items.length
    } else {
      recentAlerts.value = []
    }

    // Process workorders
    if (workorderRes.status === 'fulfilled' && workorderRes.value) {
      const data = workorderRes.value
      const items = Array.isArray(data) ? data : (data.items || [])
      pendingOrders.value = items.slice(0, 10)
      statCardValues.value[3] = data.total || items.length
    } else {
      pendingOrders.value = []
    }

    // Process system health
    if (healthRes.status === 'fulfilled' && healthRes.value) {
      const data = healthRes.value
      if (data.cpu !== undefined) {
        systemHealth.value = { cpu: data.cpu, memory: data.memory, disk: data.disk }
      } else if (data.metrics) {
        systemHealth.value = {
          cpu: data.metrics.cpu || 0,
          memory: data.metrics.memory || 0,
          disk: data.metrics.disk || 0
        }
      }
    }

    layoutModified.value = false

    // Initialize charts after data is loaded
    await nextTick()
    initCharts()

  } catch (err) {
    error.value = '加载仪表盘数据失败，请稍后重试'
    message.error('加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  if (alertChartRef.value) {
    if (!alertChart) alertChart = echarts.init(alertChartRef.value)
    const alertData = generateTrendData(recentAlerts.value, 'created_at')
    alertChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: alertData.dates
      },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        data: alertData.values,
        lineStyle: { color: '#ff7d00' },
        itemStyle: { color: '#ff7d00' }
      }]
    })
  }

  if (deviceChartRef.value) {
    if (!deviceChart) deviceChart = echarts.init(deviceChartRef.value)
    deviceChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: '5%', left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: [
          { value: deviceStats.online, name: '在线', itemStyle: { color: '#00b42a' } },
          { value: deviceStats.offline, name: '离线', itemStyle: { color: '#8c8c8c' } },
          { value: deviceStats.warning, name: '告警', itemStyle: { color: '#ff7d00' } }
        ].filter(d => d.value > 0)
      }]
    })
  }
}

// Generate trend data from items
const generateTrendData = (items, dateField) => {
  const now = new Date()
  const dates = []
  const values = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const dateStr = `${date.getMonth() + 1}/${date.getDate()}`
    dates.push(dateStr)

    const dayStart = new Date(date.setHours(0, 0, 0, 0))
    const dayEnd = new Date(date.setHours(23, 59, 59, 999))

    const count = items.filter(item => {
      if (!item[dateField]) return false
      const itemDate = new Date(item[dateField])
      return itemDate >= dayStart && itemDate <= dayEnd
    }).length

    values.push(count)
  }

  return { dates, values }
}

const handleResize = () => {
  alertChart?.resize()
  deviceChart?.resize()
}

function handleStatClick(key) {
  const routes = { total: '/monitoring/devices', online: '/monitoring/devices', alert: '/monitoring/alerts', workorder: '/workorder/list' }
  const metricMap = { device_count: 'total', online_devices: 'online', alert_count: 'alert', pending_workorders: 'workorder' }
  const route = routes[metricMap[key] || key]
  if (route) window.location.hash = route
}

// Layout customization functions
function toggleVisibility(item) {
  item.visibility = item.visibility === false ? true : false
  layoutModified.value = true
}

function toggleCollapse(item) {
  item.collapsed = !item.collapsed
  layoutModified.value = true
}

async function saveLayout() {
  if (!currentLayout.value) return
  saving.value = true
  try {
    const layoutData = {
      layout_id: layoutId.value,
      name: currentLayout.value.name || '默认布局',
      description: currentLayout.value.description || '',
      grid_size: currentLayout.value.grid_size || 'medium',
      columns: currentLayout.value.columns || 12,
      row_height: currentLayout.value.row_height || 80,
      items: allItems.value.map(item => ({
        item_id: item.item_id,
        widget: item.widget,
        position: item.position,
        visibility: item.visibility,
        collapsed: item.collapsed,
        locked: item.locked || false
      })),
      column_config: currentLayout.value.column_config || [],
      theme: currentLayout.value.theme || 'default',
      is_default: currentLayout.value.is_default || false,
      is_shared: currentLayout.value.is_shared || false,
      tags: currentLayout.value.tags || []
    }
    await monitorApi.saveDashboardLayout(layoutData)
    layoutModified.value = false
    message.success('布局保存成功')
    showCustomize.value = false
  } catch (err) {
    message.error('保存布局失败')
  } finally {
    saving.value = false
  }
}

function resetLayout() {
  allItems.value.forEach(item => {
    item.visibility = true
    item.collapsed = false
  })
  layoutModified.value = true
}

// Dashboard polling timer
let pollTimer = null

function startPoll() {
  stopPoll()
  pollTimer = setInterval(() => {
    loadDashboard()
  }, 30000)
}

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(async () => {
  await loadDashboard()
  startPoll()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopPoll()
  window.removeEventListener('resize', handleResize)
  alertChart?.dispose()
  deviceChart?.dispose()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
  min-height: calc(100vh - 40px);
}
.loading-container {
  width: 100%;
  min-height: 400px;
}
.dashboard-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.widget-control {
  margin-bottom: 6px;
}
.widget-control.inline {
  display: inline-block;
  margin-left: 8px;
}
.stats-grid {
  margin-bottom: 20px;
}
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}
.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-content {
  flex: 1;
  min-width: 0;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1;
}
.stat-label {
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
}
.stat-card.collapsed {
  padding: 12px 16px;
  justify-content: flex-start;
}
.collapsed-hint {
  font-size: 12px;
  color: #86909c;
}
.health-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}
.health-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
}
.health-body {
  padding: 16px 20px;
}
.health-item {
  flex: 1;
  padding: 0 12px;
}
.health-label {
  display: block;
  font-size: 13px;
  color: #86909c;
  margin-bottom: 8px;
}
.chart-grid,
.table-grid {
  margin-bottom: 20px;
}
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-body {
  padding: 16px 20px;
  min-height: 200px;
}
.chart-container {
  width: 100%;
  height: 280px;
}
.error-state {
  padding: 60px 20px;
  text-align: center;
}
@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }
  .stat-card {
    padding: 16px;
  }
  .stat-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .stat-value {
    font-size: 20px;
  }
  .health-body {
    flex-direction: column;
  }
  .health-item {
    padding: 8px 0;
  }
}
</style>
