<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">监控与事件台</h1>
        <p class="page-subtitle">指标监控、事件流、告警中心、告警规则一体化视图</p>
      </div>
    </div>

    <!-- 统计卡片：告警 | 事件 | 指标 | 日志 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="activeTab = 'alerts'">
          <div class="stat-icon alert-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.alerts.active }}</div>
            <div class="stat-label">活跃告警</div>
            <div class="stat-sub">
              <span class="critical">{{ stats.alerts.critical }} 严重</span>
              <span class="warning">{{ stats.alerts.warning }} 警告</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="activeTab = 'events'">
          <div class="stat-icon event-icon"><el-icon><Bell /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.events.total }}</div>
            <div class="stat-label">事件总数</div>
            <div class="stat-sub">
              <span class="critical">{{ stats.events.critical }} 严重</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="activeTab = 'metrics'">
          <div class="stat-icon metric-icon"><el-icon><DataLine /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.devices.monitored }}</div>
            <div class="stat-label">已监控设备</div>
            <div class="stat-sub">
              <span class="online">{{ stats.devices.online }} 在线</span>
              <span class="offline">{{ stats.devices.offline }} 离线</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon log-icon"><el-icon><Document /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">—</div>
            <div class="stat-label">日志接入</div>
            <div class="stat-sub">
              <span>查看详情</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页：告警列表 | 事件流 | 指标监控 | 告警规则 -->
    <el-card class="mt-4">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 告警列表 -->
        <el-tab-pane label="告警列表" name="alerts">
          <!-- 告警统计栏 -->
          <div class="alert-stats-bar">
            <div class="stat-badge critical" @click="quickFilter('critical')">
              <span class="stat-count">{{ stats.alerts.critical }}</span>
              <span class="stat-label">严重</span>
            </div>
            <div class="stat-badge warning" @click="quickFilter('warning')">
              <span class="stat-count">{{ stats.alerts.warning }}</span>
              <span class="stat-label">警告</span>
            </div>
            <div class="stat-badge info" @click="quickFilter('info')">
              <span class="stat-count">{{ stats.alerts.info }}</span>
              <span class="stat-label">提示</span>
            </div>
            <div class="stat-badge active" @click="quickFilter('active')">
              <span class="stat-count">{{ stats.alerts.active }}</span>
              <span class="stat-label">待处理</span>
            </div>
            <el-button type="primary" size="small" :loading="loading.alerts" @click="loadAlerts" style="margin-left: auto">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>

          <!-- 告警表格 -->
          <el-table :data="alerts" v-loading="loading.alerts" :row-key="row => row.id" :row-class-name="getAlertRowClass" border style="width: 100%; margin-top: 12px">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="告警名称" :show-overflow-tooltip="true" min-width="160" />
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
            <el-table-column prop="device_name" label="设备" :show-overflow-tooltip="true" width="130" />
            <el-table-column prop="occurred_at" label="发生时间" width="170">
              <template #default="{ row }">{{ formatTime(row.occurred_at || row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-space :size="4">
                  <el-button type="primary" link size="small" @click="openAlertDetail(row)">查看</el-button>
                  <el-button v-if="row.status !== 'acknowledged'" type="warning" link size="small" :loading="actionLoading" @click="acknowledgeAlert(row)">确认</el-button>
                  <el-button v-if="row.status !== 'resolved'" type="success" link size="small" :loading="actionLoading" @click="resolveAlert(row)">解决</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <el-pagination
            v-model:current-page="alertPage"
            v-model:page-size="alertPageSize"
            :total="alertTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            style="margin-top: 12px; justify-content: flex-end"
            @current-change="loadAlerts"
            @size-change="loadAlerts"
          />
        </el-tab-pane>

        <!-- 事件流 -->
        <el-tab-pane label="事件流" name="events">
          <div class="toolbar-row">
            <el-button type="primary" size="small" :loading="loading.events" @click="loadEvents">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
          <el-table :data="events" v-loading="loading.events" :row-key="row => row.id" border style="width: 100%; margin-top: 12px">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="event_id" label="事件ID" width="200" :show-overflow-tooltip="true" />
            <el-table-column prop="event_type" label="类型" width="120" />
            <el-table-column prop="source" label="来源" width="90" />
            <el-table-column prop="severity" label="严重性" width="90">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="timestamp" label="时间" width="170">
              <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openEventDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="eventPage"
            v-model:page-size="eventPageSize"
            :total="eventTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            style="margin-top: 12px; justify-content: flex-end"
            @current-change="loadEvents"
            @size-change="loadEvents"
          />
        </el-tab-pane>

        <!-- 指标监控 -->
        <el-tab-pane label="指标监控" name="metrics">
          <div class="toolbar-row">
            <el-select v-model="metricType" size="small" style="width: 120px; margin-right: 8px">
              <el-option label="CPU" value="cpu" />
              <el-option label="内存" value="memory" />
              <el-option label="磁盘" value="disk" />
              <el-option label="网络" value="network" />
            </el-select>
            <el-select v-model="metricDevice" size="small" style="width: 160px; margin-right: 8px" clearable placeholder="选择设备">
              <el-option v-for="d in deviceList" :key="d.device_name" :label="d.device_name" :value="d.device_name" />
            </el-select>
            <el-button type="primary" size="small" :loading="loading.metrics" @click="loadMetrics">
              <el-icon><Refresh /></el-icon> 查询
            </el-button>
            <el-button type="primary" size="small" :loading="loading.topMetrics" @click="loadTopMetrics" style="margin-left: 8px">
              <el-icon><Top /></el-icon> TopN
            </el-button>
          </div>

          <!-- 最新指标 -->
          <div v-if="latestMetric" class="metric-panel">
            <el-descriptions title="最新指标" :column="3" border size="small" style="margin-top: 12px">
              <el-descriptions-item label="设备">{{ latestMetric.device_name || latestMetric.host }}</el-descriptions-item>
              <el-descriptions-item label="指标名">{{ latestMetric.metric_name || latestMetric.metric }}</el-descriptions-item>
              <el-descriptions-item label="当前值">{{ latestMetric.value ?? latestMetric.current_value ?? '—' }}</el-descriptions-item>
              <el-descriptions-item label="时间">{{ formatTime(latestMetric.timestamp || latestMetric.collected_at) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- TopN 指标表格 -->
          <div v-if="topMetrics.length > 0" style="margin-top: 12px">
            <h4 style="margin: 0 0 8px 0; color: var(--el-text-color-regular)">TopN {{ metricType }} 使用</h4>
            <el-table :data="topMetrics" border size="small" max-height="300">
              <el-table-column prop="rank" label="排名" width="70" />
              <el-table-column prop="device_name" label="设备" min-width="140" :show-overflow-tooltip="true" />
              <el-table-column prop="value" label="值" width="120">
                <template #default="{ row }">{{ row.value != null ? row.value.toFixed(2) : '—' }}</template>
              </el-table-column>
              <el-table-column prop="timestamp" label="采集时间" width="170">
                <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 指标历史趋势 -->
          <div v-if="metricHistory.length > 0" style="margin-top: 12px">
            <h4 style="margin: 0 0 8px 0; color: var(--el-text-color-regular)">历史趋势</h4>
            <div ref="metricChartRef" class="metric-chart" />
          </div>
        </el-tab-pane>

        <!-- 告警规则 -->
        <el-tab-pane label="告警规则" name="rules">
          <div class="toolbar-row">
            <el-button type="primary" size="small" :loading="loading.rules" @click="loadRules">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
          <el-table :data="rules" v-loading="loading.rules" border style="width: 100%; margin-top: 12px">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="规则名称" min-width="160" :show-overflow-tooltip="true" />
            <el-table-column prop="metric_type" label="指标类型" width="100" />
            <el-table-column prop="threshold" label="阈值" width="80" />
            <el-table-column prop="severity" label="严重性" width="90">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.enabled !== false ? 'success' : 'info'" size="small">{{ row.enabled !== false ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="testRule(row)">测试</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { monitoringEvent } from './api'
import { Warning, Bell, DataLine, Document, Refresh, Top } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 状态
const activeTab = ref('alerts')
const loading = reactive({ alerts: false, events: false, metrics: false, topMetrics: false, rules: false })
const actionLoading = ref(false)

// 统计
const stats = reactive({
  alerts: { total: 0, critical: 0, warning: 0, info: 0, active: 0 },
  events: { total: 0, critical: 0 },
  devices: { total: 0, online: 0, offline: 0, maintenance: 0, monitored: 0 }
})

// 告警
const alerts = ref([])
const alertPage = ref(1)
const alertPageSize = ref(20)
const alertTotal = ref(0)
const filterLevel = ref('')
const filterStatus = ref('')

// 事件
const events = ref([])
const eventPage = ref(1)
const eventPageSize = ref(20)
const eventTotal = ref(0)

// 指标
const metricType = ref('cpu')
const metricDevice = ref('')
const deviceList = ref([])
const latestMetric = ref(null)
const topMetrics = ref([])
const metricHistory = ref([])
const metricChartRef = ref(null)
let metricChart = null

// 规则
const rules = ref([])

// 加载统计数据
const loadStats = async () => {
  try {
    // 告警统计：GET /monitoring/alerts/statistics → {total, critical, warning, info, active}
    const alertRes = await monitoringEvent.alerts.getStatistics()
    if (alertRes.data) {
      const d = alertRes.data
      stats.alerts = {
        total: d.total || 0,
        critical: d.critical || 0,
        warning: d.warning || 0,
        info: d.info || 0,
        active: d.active || 0
      }
    } else if (alertRes.active !== undefined) {
      // 直接返回对象（无 .data 包装）
      stats.alerts = {
        total: alertRes.total || 0,
        critical: alertRes.critical || 0,
        warning: alertRes.warning || 0,
        info: alertRes.info || 0,
        active: alertRes.active || 0
      }
    }
    // 设备统计：GET /devices/stats → {total, online, offline, maintenance}
    const deviceRes = await monitoringEvent.devices.getStats()
    if (deviceRes.data) {
      const d = deviceRes.data
      stats.devices = {
        total: d.total || 0,
        online: d.online || 0,
        offline: d.offline || 0,
        maintenance: d.maintenance || 0,
        monitored: d.total || 0
      }
    } else if (deviceRes.total !== undefined) {
      // 直接返回对象（无 .data 包装）
      stats.devices = {
        total: deviceRes.total || 0,
        online: deviceRes.online || 0,
        offline: deviceRes.offline || 0,
        maintenance: deviceRes.maintenance || 0,
        monitored: deviceRes.total || 0
      }
    }
  } catch (e) {
    console.error('loadStats error:', e)
  }
}

// 加载告警列表
const loadAlerts = async () => {
  loading.alerts = true
  try {
    const params = {
      page: alertPage.value,
      page_size: alertPageSize.value
    }
    if (filterLevel.value) params.level = filterLevel.value
    if (filterStatus.value) params.status = filterStatus.value

    const res = await monitoringEvent.alerts.getList(params)
    if (res.data) {
      alerts.value = Array.isArray(res.data) ? res.data : (res.data.items || res.data.list || [])
      alertTotal.value = res.data.total || alerts.value.length
    }
  } catch (e) {
    console.error('loadAlerts error:', e)
  } finally {
    loading.alerts = false
  }
}

// 加载事件流
const loadEvents = async () => {
  loading.events = true
  try {
    const res = await monitoringEvent.events.getList({
      page: eventPage.value,
      page_size: eventPageSize.value
    })
    if (res.data) {
      events.value = Array.isArray(res.data) ? res.data : (res.data.items || res.data.list || [])
      eventTotal.value = res.data.total || events.value.length
      stats.events.total = eventTotal.value
      stats.events.critical = events.value.filter(e => e.severity === 'critical').length
    }
  } catch (e) {
    console.error('loadEvents error:', e)
  } finally {
    loading.events = false
  }
}

// 加载设备列表（用于指标筛选）
const loadDeviceList = async () => {
  try {
    const res = await monitoringEvent.devices.getList({ page: 1, page_size: 100 })
    if (res.data) {
      deviceList.value = Array.isArray(res.data) ? res.data : (res.data.items || res.data.list || [])
    }
  } catch (e) {
    console.error('loadDeviceList error:', e)
  }
}

// 加载指标
const loadMetrics = async () => {
  if (!metricDevice.value) {
    ElMessage.warning('请先选择设备')
    return
  }
  loading.metrics = true
  try {
    const res = await monitoringEvent.metrics.getLatest(metricDevice.value)
    latestMetric.value = res.data || res
    metricHistory.value = []
  } catch (e) {
    console.error('loadMetrics error:', e)
    ElMessage.error('加载指标失败')
  } finally {
    loading.metrics = false
  }
}

// 加载 TopN 指标
const loadTopMetrics = async () => {
  loading.topMetrics = true
  try {
    const res = await monitoringEvent.metrics.getTop(metricType.value, { page: 1, page_size: 10 })
    if (res.data || res.items) {
      const items = res.data?.items || res.data || []
      topMetrics.value = items.map((item, idx) => ({ ...item, rank: idx + 1 }))
    }
  } catch (e) {
    console.error('loadTopMetrics error:', e)
    ElMessage.error('加载TopN指标失败')
  } finally {
    loading.topMetrics = false
  }
}

// 加载告警规则
const loadRules = async () => {
  loading.rules = true
  try {
    const res = await monitoringEvent.alerts.getRules()
    if (res.data) {
      rules.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
    }
  } catch (e) {
    console.error('loadRules error:', e)
  } finally {
    loading.rules = false
  }
}

// 确认告警
const acknowledgeAlert = async (row) => {
  actionLoading.value = true
  try {
    await monitoringEvent.alerts.acknowledge(row.id, { comment: '已确认' })
    ElMessage.success('已确认告警')
    loadAlerts()
    loadStats()
  } catch (e) {
    ElMessage.error('操作失败: ' + (e.message || '未知错误'))
  } finally {
    actionLoading.value = false
  }
}

// 解决告警
const resolveAlert = async (row) => {
  actionLoading.value = true
  try {
    await monitoringEvent.alerts.resolve(row.id, { resolution: '已处理' })
    ElMessage.success('已解决告警')
    loadAlerts()
    loadStats()
  } catch (e) {
    ElMessage.error('操作失败: ' + (e.message || '未知错误'))
  } finally {
    actionLoading.value = false
  }
}

// 快速筛选
const quickFilter = (level) => {
  filterLevel.value = level
  alertPage.value = 1
  loadAlerts()
}

// 打开告警详情
const openAlertDetail = (row) => {
  ElMessageBox.alert(
    `告警: ${row.title}\n级别: ${row.level}\n状态: ${row.status}\n设备: ${row.device_name}\n时间: ${formatTime(row.occurred_at || row.created_at)}`,
    '告警详情',
    { confirmButtonText: '确定' }
  )
}

// 打开事件详情
const openEventDetail = (row) => {
  ElMessageBox.alert(
    `事件ID: ${row.event_id}\n类型: ${row.event_type}\n来源: ${row.source}\n严重性: ${row.severity}\n状态: ${row.status}\n时间: ${formatTime(row.timestamp)}`,
    '事件详情',
    { confirmButtonText: '确定' }
  )
}

// 测试规则
const testRule = (row) => {
  ElMessage.info(`规则 "${row.name}" 测试功能开发中`)
}

// Tab 切换
const onTabChange = (tab) => {
  if (tab === 'alerts' && alerts.value.length === 0) loadAlerts()
  if (tab === 'events' && events.value.length === 0) loadEvents()
  if (tab === 'metrics' && deviceList.value.length === 0) loadDeviceList()
  if (tab === 'rules' && rules.value.length === 0) loadRules()
}

// 工具方法
const formatTime = (ts) => {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const getLevelType = (level) => {
  const map = { critical: 'danger', warning: 'warning', info: 'info', high: 'danger', medium: 'warning', low: 'info' }
  return map[level?.toLowerCase()] || 'info'
}
const getLevelLabel = (level) => {
  const map = { critical: '严重', warning: '警告', info: '提示', high: '高', medium: '中', low: '低' }
  return map[level?.toLowerCase()] || level || '—'
}
const getStatusType = (status) => {
  const map = { active: 'danger', acknowledged: 'warning', resolved: 'success', closed: 'info' }
  return map[status?.toLowerCase()] || 'info'
}
const getStatusLabel = (status) => {
  const map = { active: '待处理', acknowledged: '已确认', resolved: '已解决', closed: '已关闭', processing: '处理中' }
  return map[status?.toLowerCase()] || status || '—'
}
const getSeverityType = (sev) => {
  const map = { critical: 'danger', warning: 'warning', info: 'info', high: 'danger', medium: 'warning', low: 'info' }
  return map[sev?.toLowerCase()] || 'info'
}
const getAlertRowClass = ({ row }) => {
  if (row.level === 'critical' || row.level === 'high') return 'critical-row'
  if (row.status === 'active') return 'active-row'
  return ''
}

onMounted(() => {
  loadStats()
  loadAlerts()
  loadDeviceList()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: var(--el-text-color-primary); margin: 0; }
.page-subtitle { font-size: 14px; color: var(--el-text-color-secondary); margin: 4px 0 0 0; }
.stats-row { margin-bottom: 16px; }
.stat-card { cursor: pointer; display: flex; align-items: center; gap: 12px; }
.stat-icon { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.alert-icon { background: #fef0f0; color: #f56c6c; }
.event-icon { background: #f0f9ff; color: #409eff; }
.metric-icon { background: #f0fdf4; color: #67c23a; }
.log-icon { background: #fdf6ec; color: #e6a23c; }
.stat-content { flex: 1; }
.stat-value { font-size: 24px; font-weight: 600; color: var(--el-text-color-primary); line-height: 1.2; }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }
.stat-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; display: flex; gap: 8px; }
.stat-sub .critical { color: #f56c6c; }
.stat-sub .warning { color: #e6a23c; }
.stat-sub .online { color: #67c23a; }
.stat-sub .offline { color: #909399; }
.mt-4 { margin-top: 16px; }
.alert-stats-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.stat-badge { display: inline-flex; flex-direction: column; align-items: center; padding: 8px 16px; border-radius: 8px; cursor: pointer; min-width: 60px; }
.stat-badge.critical { background: #fef0f0; border: 1px solid #fde2e2; }
.stat-badge.warning { background: #fdf6ec; border: 1px solid #f5e6d3; }
.stat-badge.info { background: #f0f9ff; border: 1px solid #d9ecff; }
.stat-badge.active { background: #f4f4f5; border: 1px solid #e4e7ed; }
.stat-badge .stat-count { font-size: 20px; font-weight: 600; line-height: 1.2; }
.stat-badge .stat-label { font-size: 12px; margin-top: 2px; }
.critical .stat-count { color: #f56c6c; }
.warning .stat-count { color: #e6a23c; }
.info .stat-count { color: #409eff; }
.active .stat-count { color: #909399; }
.toolbar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.metric-panel { background: var(--el-fill-color-light); border-radius: 4px; padding: 12px; }
.metric-chart { width: 100%; height: 250px; }
</style>
