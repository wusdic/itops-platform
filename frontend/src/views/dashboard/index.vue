<template>
  <div class="page-container">
    <!-- 自定义工具栏 -->
    <div class="dashboard-toolbar">
      <el-space>
        <el-button type="primary" plain size="small" @click="dashboardStore.showCustomize = !dashboardStore.showCustomize">
          <el-icon><Setting /></el-icon> 自定义布局
        </el-button>
        <el-button size="small" @click="dashboardStore.resetLayout()" :disabled="dashboardStore.saving">
          <el-icon><RefreshRight /></el-icon> 重置默认
        </el-button>
        <el-button type="success" size="small" @click="dashboardStore.saveLayout()" :disabled="dashboardStore.saving || !dashboardStore.layoutModified">
          <el-icon v-if="dashboardStore.saving"><Loading /></el-icon>
          <el-icon v-else><Check /></el-icon> {{ dashboardStore.saving ? '保存中...' : '保存布局' }}
        </el-button>
      </el-space>
      <el-tag v-if="dashboardStore.layoutModified" type="warning" size="small">有未保存的更改</el-tag>
    </div>

    <!-- Loading State -->
    <div v-loading="dashboardStore.loading" class="loading-container" element-loading-text="加载数据中...">

      <!-- 统计卡片（始终显示） -->
      <el-row :gutter="16" class="stats-grid">
        <el-col :xs="24" :sm="12" :md="6" v-for="(item, idx) in dashboardStore.statWidgets" :key="item.item_id">
          <!-- 自定义模式：可拖拽/隐藏/折叠 -->
          <div v-if="dashboardStore.showCustomize" class="widget-control">
            <el-button-group size="small">
              <el-button
                @click="dashboardStore.toggleVisibility(item)"
                :type="item.visibility === false ? 'info' : 'default'"
                :icon="item.visibility === false ? Hide : View"
              />
              <el-button
                @click="dashboardStore.toggleCollapse(item)"
                :type="item.collapsed ? 'warning' : 'default'"
                :icon="item.collapsed ? DArrowRight : DArrowLeft"
              />
            </el-button-group>
          </div>
          <StatCard
            v-show="item.visibility !== false && !item.collapsed"
            :value="statCardValues[idx]"
            :label="item.widget?.title || statLabels[idx]"
            :icon="statIcons[idx]"
            :color="statCardColors[idx]"
            :clickable="true"
            :show-controls="dashboardStore.showCustomize"
            :visible="item.visibility"
            :collapsed="item.collapsed"
            @click="handleStatClick(item.widget?.metric_names?.[0])"
            @visibility-change="(v) => { item.visibility = v; dashboardStore.layoutModified = true }"
            @collapse-change="(v) => { item.collapsed = v; dashboardStore.layoutModified = true }"
          />
          <div v-show="item.visibility !== false && item.collapsed" class="stat-card collapsed" :style="{ borderLeftColor: statCardColors[idx] }">
            <span class="collapsed-hint">{{ item.widget?.title || statLabels[idx] }}: {{ statCardValues[idx] }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- 系统健康状态 -->
      <div v-if="dashboardStore.healthWidget && (dashboardStore.healthWidget.visibility !== false)" class="health-card" v-show="!dashboardStore.healthWidget.collapsed">
        <div v-if="dashboardStore.showCustomize" class="widget-control inline">
          <el-button-group size="small">
            <el-button
              @click="dashboardStore.toggleCollapse(dashboardStore.healthWidget)"
              :type="dashboardStore.healthWidget.collapsed ? 'warning' : 'default'"
              :icon="dashboardStore.healthWidget.collapsed ? DArrowRight : DArrowLeft"
            />
          </el-button-group>
        </div>
        <div class="health-header">
          <span class="card-title">系统健康状态</span>
          <el-tag :type="healthType" size="small">{{ healthText }}</el-tag>
        </div>
        <div class="health-body" v-show="!dashboardStore.healthWidget.collapsed">
          <el-space :size="20" alignment="normal" style="width: 100%; justify-content: space-between;">
            <div class="health-item">
              <span class="health-label">CPU使用率</span>
              <el-progress :percentage="dashboardStore.systemHealth.cpu" :status="getProgressStatus(dashboardStore.systemHealth.cpu)" :stroke-width="10" />
            </div>
            <div class="health-item">
              <span class="health-label">内存使用率</span>
              <el-progress :percentage="dashboardStore.systemHealth.memory" :status="getProgressStatus(dashboardStore.systemHealth.memory)" :stroke-width="10" />
            </div>
            <div class="health-item">
              <span class="health-label">磁盘使用率</span>
              <el-progress :percentage="dashboardStore.systemHealth.disk" :status="getProgressStatus(dashboardStore.systemHealth.disk)" :stroke-width="10" />
            </div>
          </el-space>
        </div>
      </div>

      <!-- 图表区域：直接用 class 标记类型，不依赖 Vue ref -->
      <el-row :gutter="16" class="chart-grid">
        <el-col :xs="24" :md="12" v-for="item in dashboardStore.chartWidgets" :key="item.item_id">
          <ChartCard
            :title="item.widget?.title || '图表'"
            :chart-class="'chart-' + item.widget?.widget_type"
            :show-controls="dashboardStore.showCustomize"
            :visible="item.visibility"
            :collapsed="item.collapsed"
            @visibility-change="(v) => { item.visibility = v; dashboardStore.layoutModified = true }"
            @collapse-change="(v) => { item.collapsed = v; dashboardStore.layoutModified = true }"
            @chart-ready="onChartReady"
          >
            <template #extra>
              <template v-if="item.widget?.widget_type === 'alert_chart'">
                <el-tag type="danger" size="small">严重 {{ dashboardStore.alertStats.critical }}</el-tag>
                <el-tag type="warning" size="small">警告 {{ dashboardStore.alertStats.warning }}</el-tag>
                <el-tag type="info" size="small">提示 {{ dashboardStore.alertStats.info }}</el-tag>
              </template>
              <template v-else-if="item.widget?.widget_type === 'device_status_chart'">
                <el-tag type="success" size="small">在线 {{ dashboardStore.deviceStats.online }}</el-tag>
                <el-tag size="small">离线 {{ dashboardStore.deviceStats.offline }}</el-tag>
                <el-tag type="warning" size="small">告警 {{ dashboardStore.deviceStats.warning }}</el-tag>
              </template>
            </template>
          </ChartCard>
        </el-col>
      </el-row>

      <!-- 表格区域 -->
      <el-row :gutter="16" class="table-grid">
        <el-col :xs="24" :md="12" v-for="item in dashboardStore.tableWidgets" :key="item.item_id">
          <div v-if="dashboardStore.showCustomize" class="widget-control inline">
            <el-button-group size="small">
              <el-button
                @click="dashboardStore.toggleVisibility(item)"
                :type="item.visibility === false ? 'info' : 'default'"
                :icon="item.visibility === false ? Hide : View"
              />
              <el-button
                @click="dashboardStore.toggleCollapse(item)"
                :type="item.collapsed ? 'warning' : 'default'"
                :icon="item.collapsed ? DArrowRight : DArrowLeft"
              />
            </el-button-group>
          </div>
          <div v-show="item.visibility !== false && !item.collapsed" class="card">
            <div class="card-header">
              <span class="card-title">{{ item.widget?.title || '表格' }}</span>
              <el-button v-if="item.widget?.widget_type === 'recent_alerts_table'" type="primary" text @click="$router.push('/monitoring/alerts')">查看更多</el-button>
              <el-button v-else-if="item.widget?.widget_type === 'pending_workorders_table'" type="primary" text @click="$router.push('/workorder/list')">查看更多</el-button>
            </div>
            <div class="card-body">
              <el-table
                v-if="item.widget?.widget_type === 'recent_alerts_table'"
                :data="dashboardStore.recentAlerts"
                :border="false"
                size="small"
                v-loading="dashboardStore.alertsLoading"
              >
                <el-table-column title="级别" key="level" width="80">
                  <template #default="{ row }">
                    <el-tag :type="severityTypeMap[row.level] || 'info'" size="small">
                      {{ severityTextMap[row.level] || row.level || '未知' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column title="告警信息" key="message" showOverflowTooltip prop="message" />
                <el-table-column title="时间" key="created_at" width="160" prop="created_at" :formatter="(row) => row.created_at ? formatDate(new Date(row.created_at)) : '-'" />
              </el-table>
              <el-table
                v-else-if="item.widget?.widget_type === 'pending_workorders_table'"
                :data="dashboardStore.pendingOrders"
                :border="false"
                size="small"
                v-loading="dashboardStore.workordersLoading"
              >
                <el-table-column title="优先级" key="priority" width="80">
                  <template #default="{ row }">
                    <el-tag :type="priorityTypeMap[row.priority] || 'info'" size="small">
                      {{ priorityTextMap[row.priority] || row.priority || '普通' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column title="工单标题" key="title" showOverflowTooltip prop="title" />
                <el-table-column title="状态" key="status" width="100">
                  <template #default="{ row }">
                    <el-tag :type="{ pending: 'warning', processing: 'info', resolved: 'success', closed: 'info' }[row.status] || 'info'" size="small">
                      {{ { pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' }[row.status] || row.status || '-' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="((item.widget?.widget_type === 'recent_alerts_table' && !dashboardStore.alertsLoading && dashboardStore.recentAlerts.length === 0) || (item.widget?.widget_type === 'pending_workorders_table' && !dashboardStore.workordersLoading && dashboardStore.pendingOrders.length === 0))" description="暂无数据" />
            </div>
          </div>
        </el-col>
      </el-row>

    </div>

    <!-- Error State -->
    <div v-if="dashboardStore.error && !dashboardStore.loading" class="error-state">
      <el-result icon="error" title="加载失败" :subTitle="dashboardStore.error">
        <template #extra>
          <el-button @click="dashboardStore.loadDashboard()">重试</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Monitor, CircleCheck, Warning, Ticket,
  Setting, RefreshRight, Check, Loading, View, Hide, DArrowLeft, DArrowRight
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import { useDashboardStore } from '@/stores/dashboard'
import { StatCard, ChartCard } from '@/components/common'

const dashboardStore = useDashboardStore()

// Stat card data
const statCardColors = ['#165dff', '#00b42a', '#ff7d00', '#f53f3f']
const statCardBgColors = ['#e8f0ff', '#e8ffea', '#fff7e6', '#fff1f0']
const statIcons = [Monitor, CircleCheck, Warning, Ticket]
const statLabels = ['设备总数', '在线设备', '告警数量', '待办工单']

// 从 store 获取统计数据（ref 会自动解包）
const statCardValues = dashboardStore.statCardValues

// Alert severity
const severityTypeMap = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info', info: 'info' }
const severityTextMap = { critical: '严重', high: '高', medium: '中', low: '低', info: '提示' }

// Workorder priority
const priorityTypeMap = { urgent: 'danger', high: 'warning', medium: 'info', low: 'info' }
const priorityTextMap = { urgent: '紧急', high: '高', medium: '中', low: '低' }

const getProgressStatus = (value) => {
  if (value >= 90) return 'exception'
  if (value >= 70) return 'warning'
  return 'success'
}

const healthType = computed(() => {
  if (!dashboardStore.systemHealth) return 'info'
  const { cpu, memory, disk } = dashboardStore.systemHealth
  if (cpu >= 90 || memory >= 90 || disk >= 90) return 'danger'
  if (cpu >= 70 || memory >= 70 || disk >= 70) return 'warning'
  return 'success'
})

const healthText = computed(() => {
  if (!dashboardStore.systemHealth) return '未知'
  const { cpu, memory, disk } = dashboardStore.systemHealth
  if (cpu >= 90 || memory >= 90 || disk >= 90) return '危险'
  if (cpu >= 70 || memory >= 70 || disk >= 70) return '警告'
  return '正常'
})

const handleStatClick = (key) => {
  const routes = { total: '/monitoring/devices', online: '/monitoring/devices', alert: '/monitoring/alerts', workorder: '/workorder/list' }
  const metricMap = { device_count: 'total', online_devices: 'online', alert_count: 'alert', pending_workorders: 'workorder' }
  const route = routes[metricMap[key] || key]
  if (route) window.location.hash = route
}

// ========== 图表初始化 ==========
let alertChart = null
let deviceChart = null

const onChartReady = (chartInstance) => {
  // 图表准备就绪时的处理
  console.log('Chart ready:', chartInstance)
}

const initCharts = () => {
  if (typeof window.echarts === 'undefined') {
    console.warn('ECharts not loaded, skipping chart init')
    return
  }

  // 告警趋势图
  const alertContainer = document.querySelector('.chart-alert_chart')
  if (alertContainer) {
    const w = alertContainer.clientWidth
    if (w > 0) {
      alertChart = window.echarts.init(alertContainer)
      const alertData = dashboardStore.generateTrendData(dashboardStore.recentAlerts, 'created_at')
      alertChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: alertData.dates },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{
          type: 'line', smooth: true, areaStyle: { opacity: 0.3 },
          data: alertData.values, lineStyle: { color: '#ff7d00' }, itemStyle: { color: '#ff7d00' }
        }]
      })
    }
  }

  // 设备状态饼图
  const deviceContainer = document.querySelector('.chart-device_status_chart')
  if (deviceContainer) {
    const w = deviceContainer.clientWidth
    if (w > 0) {
      deviceChart = window.echarts.init(deviceContainer)
      deviceChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: '5%', left: 'center' },
        series: [{
          type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
          data: [
            { value: dashboardStore.deviceStats.online, name: '在线', itemStyle: { color: '#00b42a' } },
            { value: dashboardStore.deviceStats.offline, name: '离线', itemStyle: { color: '#8c8c8c' } },
            { value: dashboardStore.deviceStats.warning, name: '告警', itemStyle: { color: '#ff7d00' } }
          ].filter(d => d.value > 0)
        }]
      })
    }
  }
}

const handleResize = () => {
  alertChart?.resize()
  deviceChart?.resize()
}

let pollTimer = null

const startPoll = () => {
  stopPoll()
  pollTimer = setInterval(() => { dashboardStore.loadDashboard() }, 30000)
}

const stopPoll = () => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onMounted(async () => {
  await dashboardStore.loadDashboard()
  startPoll()
  window.addEventListener('resize', handleResize)
  // 等待 DOM 渲染完成后初始化图表
  await nextTick()
  initCharts()
})

onUnmounted(() => {
  stopPoll()
  window.removeEventListener('resize', handleResize)
  alertChart?.dispose()
  deviceChart?.dispose()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; min-height: calc(100vh - 40px); }
.loading-container { width: 100%; min-height: 400px; }
.dashboard-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px; padding: 12px 16px; background: #f5f7fa; border-radius: 8px;
}
.widget-control { margin-bottom: 6px; }
.widget-control.inline { display: inline-block; margin-left: 8px; }
.stats-grid { margin-bottom: 20px; }
.stat-card {
  background: #fff; border-radius: 8px; padding: 20px;
  display: flex; align-items: center; gap: 16px; cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 4px solid;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.stat-card.collapsed { padding: 12px 16px; justify-content: flex-start; }
.collapsed-hint { font-size: 12px; color: #86909c; }
.health-card {
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px;
}
.health-header {
  padding: 16px 20px; border-bottom: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
}
.card-title { font-size: 16px; font-weight: 500; color: #1d2129; }
.health-body { padding: 16px 20px; }
.health-item { flex: 1; padding: 0 12px; }
.health-label { display: block; font-size: 13px; color: #86909c; margin-bottom: 8px; }
.chart-grid, .table-grid { margin-bottom: 20px; }
.card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.card-header {
  padding: 16px 20px; border-bottom: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
}
.card-body { padding: 16px 20px; min-height: 200px; }
.chart-container { width: 100%; height: 280px; }
.error-state { padding: 60px 20px; text-align: center; }
@media (max-width: 768px) {
  .page-container { padding: 12px; }
  .stat-card { padding: 16px; }
  .health-body { flex-direction: column; }
  .health-item { padding: 8px 0; }
}
</style>
