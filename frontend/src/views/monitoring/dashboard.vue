<template>
  <div class="dashboard-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">自定义仪表盘</h1>
        <p class="page-subtitle">可视化展示监控指标</p>
      </div>
      <div class="page-actions">
        <el-button @click="loadLayout" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button type="primary" @click="saveLayout">
          <el-icon><DocumentChecked /></el-icon> 保存布局
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in statsData" :key="stat.key">
        <div class="stat-icon" :style="{ background: stat.bgColor }">
          <el-icon size="24" :color="stat.color"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :class="{ loading: loading }">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
        </div>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div class="dashboard-grid">
      <!-- CPU 趋势 -->
      <el-card class="chart-card">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>CPU 使用率趋势</span>
            <el-tag size="small" type="info">{{ cpuAvg }}%</el-tag>
          </div>
        </template>
        <div ref="cpuChartRef" class="chart-container"></div>
      </el-card>

      <!-- 内存趋势 -->
      <el-card class="chart-card">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>内存使用率趋势</span>
            <el-tag size="small" type="info">{{ memoryAvg }}%</el-tag>
          </div>
        </template>
        <div ref="memoryChartRef" class="chart-container"></div>
      </el-card>

      <!-- 告警分布 -->
      <el-card class="chart-card">
        <template #header>
          <span>告警级别分布</span>
        </template>
        <div ref="alertPieChartRef" class="chart-container"></div>
      </el-card>

      <!-- 设备状态 -->
      <el-card class="chart-card">
        <template #header>
          <span>设备状态分布</span>
        </template>
        <div ref="devicePieChartRef" class="chart-container"></div>
      </el-card>

      <!-- 磁盘使用 -->
      <el-card class="chart-card wide">
        <template #header>
          <span>磁盘使用率</span>
        </template>
        <div ref="diskChartRef" class="chart-container"></div>
      </el-card>

      <!-- 网络带宽 -->
      <el-card class="chart-card wide">
        <template #header>
          <span>网络带宽趋势</span>
        </template>
        <div ref="networkChartRef" class="chart-container"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Refresh, DocumentChecked, Monitor, Tickets, Warning, Cloudy, Odometer } from '@element-plus/icons-vue'
import { dashboards } from '@/api/monitoring'

const loading = ref(false)
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const alertPieChartRef = ref(null)
const devicePieChartRef = ref(null)
const diskChartRef = ref(null)
const networkChartRef = ref(null)

let cpuChart = null
let memoryChart = null
let alertPieChart = null
let devicePieChart = null
let diskChart = null
let networkChart = null

const statsData = reactive([
  { key: 'devices', title: '监控设备', value: 0, icon: Monitor, color: '#165dff', bgColor: '#e8f0ff' },
  { key: 'alerts', title: '活跃告警', value: 0, icon: Warning, color: '#f53f3f', bgColor: '#fff1f0' },
  { key: 'cpu', title: 'CPU 平均', value: '0%', icon: Odometer, color: '#ff7d00', bgColor: '#fff7e6' },
  { key: 'memory', title: '内存平均', value: '0%', icon: Tickets, color: '#00b42a', bgColor: '#e8ffea' }
])

const cpuAvg = computed(() => statsData.find(s => s.key === 'cpu')?.value || '0%')
const memoryAvg = computed(() => statsData.find(s => s.key === 'memory')?.value || '0%')

onMounted(() => {
  loadLayout()
  loadStats()
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  cpuChart?.dispose()
  memoryChart?.dispose()
  alertPieChart?.dispose()
  devicePieChart?.dispose()
  diskChart?.dispose()
  networkChart?.dispose()
})

const handleResize = () => {
  cpuChart?.resize()
  memoryChart?.resize()
  alertPieChart?.resize()
  devicePieChart?.resize()
  diskChart?.resize()
  networkChart?.resize()
}

const initCharts = () => {
  // Initialize with empty data
  if (cpuChartRef.value) {
    cpuChart = echarts.init(cpuChartRef.value)
    cpuChart.setOption(getLineOption('CPU', '#165dff'))
  }
  if (memoryChartRef.value) {
    memoryChart = echarts.init(memoryChartRef.value)
    memoryChart.setOption(getLineOption('内存', '#00b42a'))
  }
  if (alertPieChartRef.value) {
    alertPieChart = echarts.init(alertPieChartRef.value)
    alertPieChart.setOption(getPieOption('告警分布'))
  }
  if (devicePieChartRef.value) {
    devicePieChart = echarts.init(devicePieChartRef.value)
    devicePieChart.setOption(getPieOption('设备状态'))
  }
  if (diskChartRef.value) {
    diskChart = echarts.init(diskChartRef.value)
    diskChart.setOption(getBarOption('磁盘使用率'))
  }
  if (networkChartRef.value) {
    networkChart = echarts.init(networkChartRef.value)
    networkChart.setOption(getLineOption('网络带宽', '#722ed1'))
  }
}

const getLineOption = (name, color) => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
  xAxis: { type: 'category', data: [], boundaryGap: false },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [{
    type: 'line', smooth: true, areaStyle: { opacity: 0.3 },
    data: [], lineStyle: { color }, itemStyle: { color }
  }]
})

const getPieOption = (title) => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0 },
  series: [{ type: 'pie', radius: ['40%', '70%'], data: [] }]
})

const getBarOption = (title) => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [{ type: 'bar', data: [], itemStyle: { color: '#ff7d00' } }]
})

const loadLayout = async () => {
  loading.value = true
  try {
    const res = await dashboards.getLayout()
    if (res.data) {
      updateChartsWithData(res.data)
    } else {
      // Use mock data if no layout saved
      loadMockData()
    }
  } catch (e) {
    console.error('加载布局失败:', e)
    loadMockData()
  } finally {
    loading.value = false
  }
}

const loadMockData = () => {
  const hours = Array.from({ length: 12 }, (_, i) => `${i.toString().padStart(2, '0')}:00`)
  const cpuData = Array.from({ length: 12 }, () => Math.round(30 + Math.random() * 50))
  const memData = Array.from({ length: 12 }, () => Math.round(40 + Math.random() * 40))
  const netData = Array.from({ length: 12 }, () => Math.round(10 + Math.random() * 90))
  const diskData = ['C:/', 'D:/', 'E:/'].map((label, i) => ({
    name: label,
    value: Math.round(30 + Math.random() * 60)
  }))

  updateChartsWithData({
    hours,
    cpuData,
    memoryData: memData,
    networkData: netData,
    diskData,
    alertData: [
      { name: '严重', value: 3 },
      { name: '警告', value: 8 },
      { name: '提示', value: 12 }
    ],
    deviceData: [
      { name: '在线', value: 45 },
      { name: '离线', value: 3 },
      { name: '维护中', value: 2 }
    ]
  })
}

const updateChartsWithData = (data) => {
  const { hours, cpuData, memoryData, networkData, diskData, alertData, deviceData } = data

  // Update CPU chart
  if (cpuChart) {
    cpuChart.setOption({
      xAxis: { data: hours || [] },
      series: [{ data: cpuData || [] }]
    })
    const avg = cpuData?.length ? Math.round(cpuData.reduce((a, b) => a + b, 0) / cpuData.length) : 0
    const stat = statsData.find(s => s.key === 'cpu')
    if (stat) stat.value = `${avg}%`
  }

  // Update Memory chart
  if (memoryChart) {
    memoryChart.setOption({
      xAxis: { data: hours || [] },
      series: [{ data: memoryData || [] }]
    })
    const avg = memoryData?.length ? Math.round(memoryData.reduce((a, b) => a + b, 0) / memoryData.length) : 0
    const stat = statsData.find(s => s.key === 'memory')
    if (stat) stat.value = `${avg}%`
  }

  // Update Alert Pie chart
  if (alertPieChart) {
    alertPieChart.setOption({
      series: [{ data: alertData || [] }]
    })
    const total = alertData?.reduce((a, b) => a + b.value, 0) || 0
    const stat = statsData.find(s => s.key === 'alerts')
    if (stat) stat.value = total
  }

  // Update Device Pie chart
  if (devicePieChart) {
    devicePieChart.setOption({
      series: [{ data: deviceData || [] }]
    })
    const online = deviceData?.find(d => d.name === '在线')?.value || 0
    const stat = statsData.find(s => s.key === 'devices')
    if (stat) stat.value = online
  }

  // Update Disk chart
  if (diskChart) {
    diskChart.setOption({
      xAxis: { data: diskData?.map(d => d.name) || [] },
      series: [{ data: diskData?.map(d => d.value) || [] }]
    })
  }

  // Update Network chart
  if (networkChart) {
    networkChart.setOption({
      xAxis: { data: hours || [] },
      series: [{ data: networkData || [] }]
    })
  }
}

const loadStats = async () => {
  try {
    const res = await dashboards.getStats()
    if (res.data) {
      const stat = statsData.find(s => s.key === 'devices')
      if (stat) stat.value = res.data.total_devices || 0
    }
  } catch (e) {
    // silent - use default stats
  }
}

const saveLayout = async () => {
  try {
    const layout = {
      hours: Array.from({ length: 12 }, (_, i) => `${i.toString().padStart(2, '0')}:00`),
      cpuData: Array.from({ length: 12 }, () => Math.round(30 + Math.random() * 50)),
      memoryData: Array.from({ length: 12 }, () => Math.round(40 + Math.random() * 40)),
      networkData: Array.from({ length: 12 }, () => Math.round(10 + Math.random() * 90)),
      diskData: [
        { name: 'C:/', value: 45 },
        { name: 'D:/', value: 32 },
        { name: 'E:/', value: 68 }
      ],
      alertData: [
        { name: '严重', value: 3 },
        { name: '警告', value: 8 },
        { name: '提示', value: 12 }
      ],
      deviceData: [
        { name: '在线', value: 45 },
        { name: '离线', value: 3 },
        { name: '维护中', value: 2 }
      ]
    }
    await dashboards.saveLayout(layout)
    ElMessage.success('布局已保存')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.message || '未知错误'))
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container { padding: 16px; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.page-title { font-size: 20px; font-weight: 600; color: #e8e8e8; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }
.page-actions { display: flex; gap: 8px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex; align-items: center; gap: 12px;
  padding: 16px; border-radius: 8px;
  background: #1e1e1e; border: 1px solid #333;
}
.stat-icon {
  display: flex; align-items: center; justify-content: center;
  width: 48px; height: 48px; border-radius: 8px;
}
.stat-value {
  font-size: 24px; font-weight: 700; color: #e8e8e8;
  &.loading { color: #666; }
}
.stat-title { font-size: 13px; color: #888; margin-top: 4px; }

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: #1e1e1e; border: 1px solid #333;
  &.wide { grid-column: span 2; }
  :deep(.el-card__header) { background: #252525; border-color: #333; color: #e8e8e8; }
  :deep(.el-card__body) { background: #1e1e1e; }
}

.chart-container { width: 100%; height: 250px; }
</style>
