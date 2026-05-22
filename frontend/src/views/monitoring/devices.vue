<template>
  <div class="devices-container">
    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16" class="stats-grid">
      <n-gi v-for="stat in stats" :key="stat.key">
        <n-card class="stat-card" :style="{ borderLeft: `3px solid ${stat.color}` }" content-style="padding: 16px;">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- 设备列表 -->
    <n-card title="设备列表" :bordered="false">
      <template #header-extra>
        <n-space :size="12" align="center">
          <n-input v-model:value="searchKeyword" placeholder="搜索名称/IP" clearable style="width: 200px" @keydown.enter="handleSearch" @clear="handleSearchClear">
            <template #prefix>
              <n-icon><Search /></n-icon>
            </template>
          </n-input>
          <n-button type="primary" @click="loadDevices" :loading="loading">
            <template #icon><n-icon><RefreshOutline /></n-icon></template>
            刷新
          </n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="deviceList"
        :loading="loading"
        :pagination="getPaginationConfig()"
        :row-key="row => row.id"
        :remote="true"
        :key="paginationVersion"
        @row-click="handleRowClick"
      />
    </n-card>

    <!-- 设备详情抽屉 -->
    <n-drawer v-model:show="drawerVisible" :width="860" placement="right" :preset="null">
      <n-drawer-content :title="selectedDevice?.name || '设备详情'" closable>
        <template #header-extra>
          <n-spin :show="metricsLoading" size="small" />
        </template>

        <n-tabs type="line" animated v-model:value="activeDeviceTab" size="small">
          <!-- 基本信息Tab -->
          <n-tab-pane name="info" tab="基本信息">
            <n-descriptions label-placement="left" :column="2" size="small" bordered>
              <n-descriptions-item label="IP地址">{{ selectedDevice?.ip_address || '-' }}</n-descriptions-item>
              <n-descriptions-item label="设备类型">{{ selectedDevice?.type || '-' }}</n-descriptions-item>
              <n-descriptions-item label="操作系统">{{ nullOrDefault(selectedDevice?.os_type) }} {{ nullOrDefault(selectedDevice?.os_version) }}</n-descriptions-item>
              <n-descriptions-item label="位置">{{ selectedDevice?.location || '-' }}</n-descriptions-item>
              <n-descriptions-item label="状态">
                <n-tag :type="statusType(selectedDevice?.status)" size="small">{{ statusText(selectedDevice?.status) }}</n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="厂商">{{ selectedDevice?.manufacturer || '-' }}</n-descriptions-item>
              <n-descriptions-item label="型号">{{ selectedDevice?.model || '-' }}</n-descriptions-item>
              <n-descriptions-item label="序列号">{{ selectedDevice?.serial_number || '-' }}</n-descriptions-item>
              <n-descriptions-item label="最近采集">{{ selectedDevice?.last_collect_time ? formatDate(new Date(selectedDevice.last_collect_time)) : '-' }}</n-descriptions-item>
              <n-descriptions-item label="创建时间">{{ selectedDevice?.created_at ? formatDate(new Date(selectedDevice.created_at)) : '-' }}</n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>

          <!-- 系统信息Tab -->
          <n-tab-pane name="system" tab="系统信息">
            <n-descriptions label-placement="left" :column="2" size="small" bordered>
              <n-descriptions-item label="发行版">{{ nullOrDefault(selectedDevice?.distro) }}</n-descriptions-item>
              <n-descriptions-item label="操作系统">{{ nullOrDefault(selectedDevice?.os_name) }}</n-descriptions-item>
              <n-descriptions-item label="内核版本">{{ nullOrDefault(selectedDevice?.kernel) }}</n-descriptions-item>
              <n-descriptions-item label="运行时间">{{ nullOrDefault(selectedDevice?.uptime) }}</n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>

          <!-- 硬件信息Tab -->
          <n-tab-pane name="hardware" tab="硬件信息">
            <n-descriptions label-placement="left" :column="2" size="small" bordered>
              <n-descriptions-item label="产品名称">{{ nullOrDefault(selectedDevice?.hardware?.product_name) }}</n-descriptions-item>
              <n-descriptions-item label="厂商">{{ nullOrDefault(selectedDevice?.hardware?.vendor) }}</n-descriptions-item>
              <n-descriptions-item label="BIOS版本">{{ nullOrDefault(selectedDevice?.hardware?.bios_version) }}</n-descriptions-item>
              <n-descriptions-item label="CPU型号">{{ nullOrDefault(selectedDevice?.cpu?.model) }}</n-descriptions-item>
              <n-descriptions-item label="CPU核心数">{{ nullOrDefault(selectedDevice?.cpu?.cores) }}</n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>

          <!-- 性能Tab -->
          <n-tab-pane name="performance" tab="性能">
            <div v-if="metricsData" class="metrics-charts">
              <div class="metrics-grid">
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">CPU 使用率</span>
                    <span class="metric-value">{{ metricsData.cpu?.toFixed(1) || '0' }}%</span>
                  </div>
                  <div ref="cpuChartRef" class="metric-chart"></div>
                </div>
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">内存使用率</span>
                    <span class="metric-value">{{ metricsData.memory?.toFixed(1) || '0' }}%</span>
                  </div>
                  <div ref="memoryChartRef" class="metric-chart"></div>
                </div>
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">磁盘使用率</span>
                    <span class="metric-value">{{ metricsData.disk?.toFixed(1) || '0' }}%</span>
                  </div>
                  <div ref="diskChartRef" class="metric-chart"></div>
                </div>
              </div>
            </div>
            <div v-else-if="!metricsLoading && metricsError" class="no-data">
              <n-result status="error" title="加载失败" :description="metricsError">
                <template #footer>
                  <n-button size="small" @click="loadMetrics(selectedDevice)">重试</n-button>
                </template>
              </n-result>
            </div>
            <div v-else-if="!metricsLoading" class="no-data">
              <n-empty description="暂无性能数据" />
            </div>
          </n-tab-pane>

          <!-- 磁盘Tab -->
          <n-tab-pane name="disk" tab="磁盘">
            <n-data-table
              v-if="selectedDevice?.disks?.length"
              :columns="diskColumns"
              :data="selectedDevice.disks"
              size="small"
              :row-key="(row, index) => index"
            />
            <n-empty v-else description="暂无磁盘信息" />
          </n-tab-pane>

          <!-- 网络Tab -->
          <n-tab-pane name="network" tab="网络">
            <n-data-table
              v-if="selectedDevice?.network?.length"
              :columns="networkColumns"
              :data="selectedDevice.network"
              size="small"
              :row-key="(row, index) => index"
            />
            <n-empty v-else description="暂无网络信息" />
          </n-tab-pane>

          <!-- 容器Tab -->
          <n-tab-pane name="container" tab="容器">
            <n-descriptions label-placement="left" :column="2" size="small" bordered>
              <n-descriptions-item label="Docker容器数">{{ nullOrDefault(selectedDevice?.containers?.docker?.count) }}</n-descriptions-item>
              <n-descriptions-item label="Containerd容器数">{{ nullOrDefault(selectedDevice?.containers?.containerd?.count) }}</n-descriptions-item>
            </n-descriptions>
            <template v-if="selectedDevice?.containers?.docker?.containers?.length">
              <div class="sub-title">Docker容器列表</div>
              <n-data-table
                :columns="dockerContainerColumns"
                :data="selectedDevice.containers.docker.containers"
                size="small"
                :row-key="(row, index) => index"
              />
            </template>
          </n-tab-pane>
        </n-tabs>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, h, nextTick, watchEffect } from 'vue'
import { NGrid, NGi, NCard, NButton, NDataTable, NTag, NIcon, NSpace, NTooltip, useMessage, useDialog, NDrawer, NDrawerContent, NSpin, NEmpty, NResult, NTabs, NTabPane, NDescriptions, NDescriptionsItem } from 'naive-ui'
import * as echarts from 'echarts'
import { devices } from '@/api'
import { RefreshOutline, Search } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

// 空值处理方法
const nullOrDefault = (val, defaultStr = '-') => {
  if (val === null || val === undefined || val === '') return defaultStr
  return val
}

// 日期格式化函数
const formatDate = (date) => {
  if (!date) return '-'
  try {
    const d = new Date(date)
    if (isNaN(d.getTime())) return '-'
    return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return '-'
  }
}
const loading = ref(false)
const deviceList = ref([])
const searchKeyword = ref('')
// 分页状态（纯 JS 对象 + ref + version 触发重渲染）
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
// itemCount 必须是 ref，Naive UI 内部追踪同一个 ref
const itemCountRef = ref(0)
const pageCountRef = ref(1)
// version 用于强制 Naive UI 重新读取 config
const paginationVersion = ref(0)
// paginationConfig 是共享的纯 JS 对象，getPaginationConfig() 每次返回同一引用
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
    loadDevices()
  },
  onUpdatePageSize: (s) => {
    pageSize.value = s
    page.value = 1
    paginationConfig.pageSize = s
    paginationConfig.page = 1
    paginationVersion.value++
    loadDevices()
  }
}
// getPaginationConfig 返回共享对象的引用，Naive UI 内部 Object.assign 作用在同一引用上
// 使用 watchEffect 主动同步，确保 total/page/pageSize 变化时 Naive UI 收到最新值

watchEffect(() => {
  // 读取所有响应式值建立依赖
  paginationConfig.page = page.value
  paginationConfig.pageSize = pageSize.value
  paginationConfig.total = total.value
  paginationConfig.itemCount = total.value
  paginationConfig.pageCount = Math.max(1, Math.ceil((total.value || 0) / (pageSize.value || 1)))
})

const getPaginationConfig = () => paginationConfig

// 抽屉相关
const drawerVisible = ref(false)
const selectedDevice = ref(null)
const metricsLoading = ref(false)
const metricsData = ref(null)
const metricsError = ref(null)

// 图表 ref
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskChartRef = ref(null)
let cpuChart = null
let memoryChart = null
let diskChart = null

// 设备详情标签页
const activeDeviceTab = ref('info')

// 磁盘列定义
const diskColumns = [
  { title: '设备', key: 'device', render: (row) => nullOrDefault(row.device) },
  { title: '挂载点', key: 'mount_point', render: (row) => nullOrDefault(row.mount_point) },
  { title: '文件系统', key: 'filesystem', render: (row) => nullOrDefault(row.filesystem) },
  { title: '总大小', key: 'total', render: (row) => row.total ? (row.total / 1024 / 1024 / 1024).toFixed(1) + ' GB' : '-' },
  { title: '已用', key: 'used', render: (row) => row.used ? (row.used / 1024 / 1024 / 1024).toFixed(1) + ' GB' : '-' },
  { title: '使用率', key: 'usage_percent', render: (row) => row.usage_percent ? row.usage_percent + '%' : '-' },
]

// 网络列定义
const networkColumns = [
  { title: '接口名', key: 'name', render: (row) => nullOrDefault(row.name) },
  { title: 'IP地址', key: 'ip_address', render: (row) => nullOrDefault(row.ip_address) },
  { title: 'MAC地址', key: 'mac', render: (row) => nullOrDefault(row.mac) },
  { title: '状态', key: 'status', render: (row) => nullOrDefault(row.status) },
  { title: '接收速率', key: 'rx_rate', render: (row) => row.rx_rate ? row.rx_rate + ' KB/s' : '-' },
  { title: '发送速率', key: 'tx_rate', render: (row) => row.tx_rate ? row.tx_rate + ' KB/s' : '-' },
]

// Docker容器列定义
const dockerContainerColumns = [
  { title: '名称', key: 'name', ellipsis: { tooltip: true }, render: (row) => nullOrDefault(row.name) },
  { title: '镜像', key: 'image', ellipsis: { tooltip: true }, render: (row) => nullOrDefault(row.image) },
  { title: '状态', key: 'status', render: (row) => h(NTag, { type: row.status === 'running' ? 'success' : 'default', size: 'small' }, () => nullOrDefault(row.status)) },
  { title: '端口映射', key: 'ports', render: (row) => nullOrDefault(row.ports) },
]

const stats = reactive([
  { key: 'total', label: '设备总数', value: 0, color: '#18a058' },
  { key: 'online', label: '在线', value: 0, color: '#00b42a' },
  { key: 'offline', label: '离线', value: 0, color: '#86909c' },
  { key: 'unknown', label: '未知', value: 0, color: '#ff7d00' }
])

// 轮询定时器
let pollTimer = null

const statusType = (s) => ({ online: 'success', offline: 'warning', unknown: 'default' })[s] || 'default'
const statusText = (s) => ({ online: '在线', offline: '离线', unknown: '未知' })[s] || s

const getRowClassName = ({ row }) => {
  if (row.status === 'offline') return 'row-offline'
  if (row.status === 'online') return 'row-online'
  return ''
}

// CPU列渲染
const renderCpu = (row) => {
  const model = row.cpu?.model || ''
  const cores = row.cpu?.cores
  if (!model && cores === undefined) return '-'
  return model ? `${model} (${cores}核)` : `${cores}核`
}

// 内存列渲染
const renderMemory = (row) => {
  const total = row.memory?.total_mb
  if (!total) return '-'
  return (total / 1024).toFixed(1) + ' GB'
}

// 负载列渲染
const renderLoad = (row) => {
  const load = row.cpu?.load_avg_1m
  if (load === undefined || load === null) return '-'
  return load.toFixed(2)
}

const columns = [
  { title: '名称', key: 'name', ellipsis: { tooltip: true }, render: (row) => h('a', { style: 'color: #18a058; cursor: pointer', onClick: () => handleRowClick(row) }, row.name) },
  { title: 'IP地址', key: 'ip_address', width: 140, render: (r) => nullOrDefault(r.ip_address) },
  { title: 'CPU', key: 'cpu', width: 180, ellipsis: { tooltip: true }, render: renderCpu },
  { title: '内存', key: 'memory', width: 100, render: renderMemory },
  { title: '负载', key: 'load', width: 80, render: renderLoad },
  { title: '系统', key: 'os_type', width: 100, render: (r) => nullOrDefault(r.os_type) },
  { title: '系统版本', key: 'os_version', width: 150, ellipsis: { tooltip: true }, render: (r) => nullOrDefault(r.os_version) },
  { title: '厂商型号', key: 'manufacturer', width: 160, render: (r) => r.manufacturer ? r.manufacturer + ' ' + (r.model || '') : '-' },
  { title: '状态', key: 'status', width: 90, render: (r) => h(NTag, { type: statusType(r.status), size: 'small' }, () => statusText(r.status)) },
  { title: '最近探测', key: 'last_collect_time', width: 170, render: (r) => r.last_collect_time ? formatDate(new Date(r.last_collect_time)) : '-' },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render(row) {
      return h(NSpace, { size: 8 }, () => [
        h(NButton, { size: 'small', type: 'primary', ghost: true, onClick: () => handleRowClick(row) }, () => '详情'),
        h(NButton, { size: 'small', type: 'warning', onClick: () => handleCollect(row) }, () => '采集'),
        h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除')
      ])
    }
  }
]

async function loadDevices() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')

    // 统计
    try {
      const statsRes = await fetch('/api/v1/assets/stats', { headers: { Authorization: `Bearer ${token}` } })
      if (statsRes.status === 401) {
        message.warning('登录已过期，请重新登录')
        localStorage.removeItem('token')
        window.location.href = '/login'
        return
      }
      if (statsRes.ok) {
        const statsData = await statsRes.json()
        stats[0].value = statsData.total_devices || 0
        stats[1].value = statsData.online_devices || 0
        stats[2].value = statsData.offline_devices || 0
        stats[3].value = (statsData.total_devices || 0) - (statsData.online_devices || 0) - (statsData.offline_devices || 0) - (statsData.maintenance_devices || 0)
      } else {
        const listRes = await fetch('/api/v1/assets/device?page=1&page_size=100', { headers: { Authorization: `Bearer ${token}` } })
        if (listRes.status === 401) {
          message.warning('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          return
        }
        if (listRes.ok) {
          const listData = await listRes.json()
          const devices = listData.items || listData.data?.items || []
          stats[0].value = devices.length
          stats[1].value = devices.filter(d => d.status === 'online').length
          stats[2].value = devices.filter(d => d.status === 'offline').length
          stats[3].value = devices.filter(d => d.status !== 'online' && d.status !== 'offline').length
        }
      }
    } catch { /* ignore */ }

    const res = await fetch(`/api/v1/assets/device?page=${page.value}&page_size=${pageSize.value}${searchKeyword.value ? '&keyword=' + encodeURIComponent(searchKeyword.value) : ''}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.status === 401) {
      message.warning('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
      return
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (!data || typeof data !== 'object') throw new Error('响应格式异常')

    deviceList.value = data.items || data.data?.items || []
    total.value = data.total || data.data?.total || 0
    paginationConfig.total = total.value
    paginationConfig.itemCount = total.value
    paginationConfig.pageCount = Math.max(1, Math.ceil((total.value || 0) / (pageSize.value || 1)))
    itemCountRef.value = total.value
    pageCountRef.value = paginationConfig.pageCount
    paginationVersion.value++
  } catch (e) {
    message.error(`加载设备列表失败: ${e.message}`)
    deviceList.value = []
    console.error('[devices] loadDevices error:', e)
  } finally {
    loading.value = false
  }
}

function handleRowClick(row) {
  selectedDevice.value = row
  drawerVisible.value = true
  activeDeviceTab.value = 'info'
  loadMetrics(row)
}

function handleDelete(row) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除设备 "${row.name}" 吗？此操作不可恢复。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await devices.delete(row.id)
        message.success('删除成功')
        loadDevices()
      } catch (e) {
        message.error('删除失败: ' + (e.message || e))
      }
    }
  })
}

function handleCollect(row) {
  dialog.warning({
    title: '确认采集',
    content: `确定要采集设备 "${row.name}" 的指标数据吗？`,
    positiveText: '确认采集',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await devices.collect({ device_id: row.id })
        message.success('采集任务已触发')
      } catch (e) {
        message.error('采集失败: ' + (e.message || e))
      }
    }
  })
}

async function loadMetrics(device) {
  if (!device?.id) return
  metricsLoading.value = true
  metricsError.value = null
  metricsData.value = null

  // 销毁旧图表
  cpuChart?.dispose()
  memoryChart?.dispose()
  diskChart?.dispose()
  cpuChart = null
  memoryChart = null
  diskChart = null

  try {
    const token = localStorage.getItem('token')
    const now = new Date()
    const startTime = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString()
    const endTime = now.toISOString()

    const [cpuRes, memRes, diskRes] = await Promise.all([
      fetch('/api/v1/monitoring/metrics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ device_id: device.id, metric_type: 'cpu', start_time: startTime, end_time: endTime })
      }),
      fetch('/api/v1/monitoring/metrics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ device_id: device.id, metric_type: 'memory', start_time: startTime, end_time: endTime })
      }),
      fetch('/api/v1/monitoring/metrics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ device_id: device.id, metric_type: 'disk', start_time: startTime, end_time: endTime })
      })
    ])

    if (!cpuRes.ok || !memRes.ok || !diskRes.ok) {
      throw new Error(`HTTP ${cpuRes.status || memRes.status || diskRes.status}`)
    }

    const [cpuData, memData, diskData] = await Promise.all([cpuRes.json(), memRes.json(), diskRes.json()])

    const calcAvg = (data) => {
      if (!data?.data?.values || data.data.values.length === 0) return 0
      const sum = data.data.values.reduce((acc, v) => acc + (v.value ?? 0), 0)
      return sum / data.data.values.length
    }

    metricsData.value = {
      cpu: calcAvg(cpuData),
      memory: calcAvg(memData),
      disk: calcAvg(diskData)
    }

    // 等 DOM 更新后初始化图表
    await nextTick()
    initCharts(cpuData, memData, diskData)
  } catch (e) {
    metricsError.value = e.message
    message.error(`加载性能指标失败: ${e.message}`)
    console.error('[devices] loadMetrics error:', e)
  } finally {
    metricsLoading.value = false
  }
}

function initCharts(cpuData, memData, diskData) {
  const chartData = [
    { ref: cpuChartRef, data: cpuData, color: '#18a058', label: 'CPU' },
    { ref: memoryChartRef, data: memData, color: '#2080f0', label: '内存' },
    { ref: diskChartRef, data: diskData, color: '#f0a020', label: '磁盘' },
  ]

  chartData.forEach(({ ref, data, color, label }) => {
    if (!ref.value) return
    const values = data.data?.values || []
    const currentValue = values.length > 0 ? values[values.length - 1].value ?? 0 : 0

    const chart = echarts.init(ref.value)
    const option = {
      series: [
        // 仪表盘
        {
          type: 'gauge',
          startAngle: 200,
          endAngle: -20,
          radius: '90%',
          center: ['50%', '60%'],
          min: 0,
          max: 100,
          splitNumber: 4,
          itemStyle: { color },
          progress: { show: true, width: 8, itemStyle: { color } },
          pointer: { show: false },
          axisLine: { lineStyle: { width: 8, color: [[1, '#e8e8e8']] } },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          anchor: { show: false },
          title: { show: false },
          detail: {
            valueAnimation: true,
            fontSize: 14,
            fontWeight: 'bold',
            offsetCenter: [0, '10%'],
            formatter: '{value}%',
            color: '#303133',
          },
          data: [{ value: currentValue }],
        },
        // 迷你趋势线
        {
          type: 'line',
          smooth: true,
          symbol: 'none',
          areaStyle: { opacity: 0.3, color },
          lineStyle: { color, width: 1.5 },
          data: values.map(v => v.value ?? 0),
          xAxis: { show: false },
          yAxis: { show: false },
          grid: { left: 0, right: 0, top: 0, bottom: 0 },
        },
      ],
    }
    chart.setOption(option)
  })

  // 保存图表实例
  cpuChart = cpuChartRef.value ? echarts.getInstanceByDom(cpuChartRef.value) : null
  memoryChart = memoryChartRef.value ? echarts.getInstanceByDom(memoryChartRef.value) : null
  diskChart = diskChartRef.value ? echarts.getInstanceByDom(diskChartRef.value) : null
}

function startPoll() {
  stopPoll()
  pollTimer = setInterval(() => { loadDevices() }, 30000)
}

function stopPoll() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onMounted(() => {
  loadDevices()
  startPoll()

  // 监听窗口 resize
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopPoll()
  cpuChart?.dispose()
  memoryChart?.dispose()
  diskChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  cpuChart?.resize()
  memoryChart?.resize()
  diskChart?.resize()
}
</script>

<style scoped>
.devices-container { padding: 16px; }
.stat-card { text-align: center; cursor: default; transition: transform 0.2s, box-shadow 0.2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-value { font-size: 28px; font-weight: 700; color: #1d2129; }
.stat-label { font-size: 13px; color: #86909c; margin-top: 4px; }

.metrics-charts { padding: 8px 0; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.metric-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}
.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.metric-label { font-size: 13px; color: #606266; }
.metric-value { font-size: 18px; font-weight: 700; color: #303133; }
.metric-chart { width: 100%; height: 60px; }

.no-data { padding: 24px 0; text-align: center; }

.sub-title { font-size: 14px; font-weight: 500; color: #303133; margin: 16px 0 8px 0; }

/* Row status */
:deep(.row-offline) { background-color: #fff1f0 !important; }
:deep(.row-online) { background-color: #f0f9eb !important; }
</style>
