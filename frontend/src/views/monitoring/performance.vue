<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">性能监控</h1>
        <p class="page-subtitle">实时监控系统性能指标</p>
      </div>
      <div class="page-actions">
        <el-button @click="loadDevices" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 设备选择 -->
    <el-card class="mb-4">
      <template #header>
        <span>选择设备</span>
      </template>
      <el-space align="center" :wrap="true" :size="12">
        <el-select
          v-model="selectedDeviceId"
          :options="deviceOptions"
          placeholder="请选择设备"
          filterable
          style="width: 300px"
          @change="handleDeviceChange"
        />
        <el-date-picker
          v-model="timeRange"
          type="datetimerange"
          clearable
          style="width: 380px"
        />
        <el-button type="primary" @click="loadMetrics" :loading="loading">
          查询
        </el-button>
      </el-space>
    </el-card>

    <!-- 性能概览 -->
    <div v-if="selectedDeviceId" class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f0ff">
          <el-icon size="24" color="#165dff"><Monitor /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :class="{ loading: loading }">
            {{ loading ? '-' : (metrics.cpu ?? '--') }}%
          </div>
          <div class="stat-title">CPU使用率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8ffea">
          <el-icon size="24" color="#00b42a"><TicketOutline /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :class="{ loading: loading }">
            {{ loading ? '-' : (metrics.memory ?? '--') }}%
          </div>
          <div class="stat-title">内存使用率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fff7e6">
          <el-icon size="24" color="#ff7d00"><Folder /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :class="{ loading: loading }">
            {{ loading ? '-' : (metrics.disk ?? '--') }}%
          </div>
          <div class="stat-title">磁盘使用率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fff1f0">
          <el-icon size="24" color="#f53f3f"><Cloudy /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :class="{ loading: loading }">
            {{ loading ? '-' : (metrics.network ?? '--') }}
          </div>
          <div class="stat-title">网络带宽 (Mbps)</div>
        </div>
      </div>
    </div>

    <!-- 空状态：未选择设备 -->
    <el-card v-if="!selectedDeviceId" class="empty-state-card">
      <template #header>
        <span></span>
      </template>
      <div class="empty-state">
        <el-icon size="64" color="#c0c4cc"><Odometer /></el-icon>
        <p class="empty-title">请选择设备</p>
        <p class="empty-desc">从上方下拉框选择一个设备，即可查看其性能指标和历史趋势</p>
      </div>
    </el-card>

    <!-- 性能图表 -->
    <div v-if="selectedDeviceId" class="performance-grid">
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>CPU使用率趋势</span>
            <span v-if="lastUpdateTime" class="update-time">更新于 {{ lastUpdateTime }}</span>
          </div>
        </template>
        <div ref="cpuChartRef" class="chart-container"></div>
      </el-card>
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>内存使用率趋势</span>
            <span v-if="lastUpdateTime" class="update-time">更新于 {{ lastUpdateTime }}</span>
          </div>
        </template>
        <div ref="memoryChartRef" class="chart-container"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Monitor, Folder, Cloudy, Refresh, Odometer
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import { devices } from '@/api/monitoring'
import { performance } from '@/api/monitoring'

const message = ElMessage

const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
let cpuChart = null
let memoryChart = null
let refreshTimer = null

const loading = ref(false)
const selectedDeviceId = ref(null)
const timeRange = ref(null)
const deviceList = ref([])
const deviceOptions = ref([])
const lastUpdateTime = ref('')

const metrics = reactive({ cpu: null, memory: null, disk: null, network: null })

onMounted(() => {
  loadDevices()
  startRefresh()
})

onUnmounted(() => {
  stopRefresh()
  cpuChart?.dispose()
  memoryChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

const loadDevices = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const data = await devices.getList({ page: 1, page_size: 100 })
    const newDevices = data.items || data.data?.items || []
    deviceList.value = newDevices
    deviceOptions.value = deviceList.value.map(d => ({
      label: `${d.name} (${d.ip_address})`,
      value: d.id
    }))
  } catch (e) {
    message.error(`加载设备失败: ${e.message}`)
    deviceList.value = []
  } finally {
    loading.value = false
  }
}

const handleDeviceChange = (value) => {
  selectedDeviceId.value = value
  metrics.cpu = null
  metrics.memory = null
  metrics.disk = null
  metrics.network = null
  lastUpdateTime.value = ''
  if (value) {
    loadMetrics()
  }
}

const loadMetrics = async () => {
  if (!selectedDeviceId.value) return
  if (loading.value) return

  loading.value = true
  try {
    const body = {
      device_id: selectedDeviceId.value,
      metrics: ['cpu', 'memory', 'disk', 'network'],
      start_time: timeRange.value ? timeRange.value[0] : Date.now() - 3600000,
      end_time: timeRange.value ? timeRange.value[1] : Date.now()
    }
    const data = await performance.query(body)

    metrics.cpu = data.cpu ?? 0
    metrics.memory = data.memory ?? 0
    metrics.disk = data.disk ?? 0
    metrics.network = data.network ?? 0

    lastUpdateTime.value = formatDate(new Date(), 'HH:mm:ss')

    updateCharts(data)
  } catch (e) {
    message.error(`加载指标失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

const updateCharts = (data) => {
  const dataLen = (data.cpu_history || []).length || 24
  const hours = Array.from({ length: dataLen }, (_, i) => {
    const totalPoints = dataLen
    const timeSpan = timeRange.value
      ? (timeRange.value[1] - timeRange.value[0]) / 3600000
      : 24
    const hour = new Date(timeRange.value ? timeRange.value[0] : Date.now() - 3600000)
    hour.setHours(hour.getHours() + Math.floor((i / totalPoints) * timeSpan))
    return `${hour.getHours().toString().padStart(2, '0')}:00`
  })

  const cpuData = data.cpu_history || []
  const memData = data.memory_history || []

  if (cpuChartRef.value) {
    if (!cpuChart) cpuChart = echarts.init(cpuChartRef.value)
    cpuChart.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => {
        const p = params[0]
        return `${p.axisValue}<br/>${p.marker} CPU: ${p.value}%`
      }},
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: hours, boundaryGap: false },
      yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        data: cpuData,
        lineStyle: { color: '#165dff' },
        itemStyle: { color: '#165dff' },
        showSymbol: cpuData.length < 20,
        emphasis: { focus: 'series' }
      }]
    })
  }

  if (memoryChartRef.value) {
    if (!memoryChart) memoryChart = echarts.init(memoryChartRef.value)
    memoryChart.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => {
        const p = params[0]
        return `${p.axisValue}<br/>${p.marker} 内存: ${p.value}%`
      }},
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: hours, boundaryGap: false },
      yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        data: memData,
        lineStyle: { color: '#00b42a' },
        itemStyle: { color: '#00b42a' },
        showSymbol: memData.length < 20,
        emphasis: { focus: 'series' }
      }]
    })
  }
}

const handleResize = () => {
  cpuChart?.resize()
  memoryChart?.resize()
}

window.addEventListener('resize', handleResize)

const startRefresh = () => {
  refreshTimer = setInterval(() => {
    if (selectedDeviceId.value) loadMetrics()
  }, 30000)
}

const stopRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}
</script>

<style lang="scss" scoped>
.mb-4 { margin-bottom: 16px; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.performance-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 20px 0;
}
.chart-container { width: 100%; height: 300px; }

.empty-state-card {
  margin: 20px 0;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}
.empty-title {
  margin-top: 16px;
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}
.empty-desc {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  transition: color 0.3s;
  &.loading {
    color: #c0c4cc;
  }
}

.update-time {
  font-size: 12px;
  color: #909399;
}
</style>
