<template>
  <div class="logs-container">
    <n-tabs type="line" animated v-model:value="activeTab">
      <!-- 操作日志 -->
      <n-tab-pane name="operation" tab="操作日志">
        <n-card title="操作日志" :bordered="false">
          <template #header-extra>
            <n-space>
              <n-input v-model:value="filters.keyword" placeholder="搜索操作/路径" clearable style="width: 180px" />
              <n-select v-model:value="filters.action" :options="actionOptions" placeholder="操作类型" clearable style="width: 120px" />
              <n-date-picker v-model:value="filters.dateRange" type="daterange" clearable placeholder="日期范围" style="width: 240px" />
              <n-button @click="loadOperationLogs" :loading="loading">
                <template #icon><n-icon><RefreshOutline /></n-icon></template>
                刷新
              </n-button>
            </n-space>
          </template>

          <n-data-table
            :columns="operationColumns"
            :data="operationLogs"
            :loading="loading"
            :pagination="getLogPagination()"
            :key="logPaginationVersion"
            :remote="true"
            :row-key="row => row.id"
            :scroll-x="1200"
            size="small"
          />
        </n-card>
      </n-tab-pane>

      <!-- 系统日志 -->
      <n-tab-pane name="system" tab="系统日志">
        <n-card title="系统日志" :bordered="false">
          <template #header-extra>
            <n-space>
              <n-select v-model:value="systemFilters.level" :options="logLevelOptions" placeholder="日志级别" clearable style="width: 120px" />
              <n-input v-model:value="systemFilters.keyword" placeholder="搜索日志内容" clearable style="width: 200px" />
              <n-button @click="loadSystemLogs" :loading="systemLoading">
                <template #icon><n-icon><RefreshOutline /></n-icon></template>
                刷新
              </n-button>
            </n-space>
          </template>

          <n-data-table
            :columns="systemColumns"
            :data="systemLogs"
            :loading="systemLoading"
            :pagination="getLogPagination()"
            :key="logPaginationVersion"
            :remote="true"
            :row-key="row => row.idx"
            :scroll-x="1000"
            size="small"
          />
        </n-card>
      </n-tab-pane>

      <!-- 告警审计日志 -->
      <n-tab-pane name="alert" tab="告警审计">
        <n-card title="告警审计日志" :bordered="false">
          <template #header-extra>
            <n-button @click="loadAlertAuditLogs" :loading="alertLoading">
              <template #icon><n-icon><RefreshOutline /></n-icon></template>
              刷新
            </n-button>
          </template>

          <n-data-table
            :columns="alertColumns"
            :data="alertAuditLogs"
            :loading="alertLoading"
            :pagination="getLogPagination()"
            :key="logPaginationVersion"
            :remote="true"
            :row-key="row => row.id"
            :scroll-x="1000"
            size="small"
          />
        </n-card>
      </n-tab-pane>

      <!-- 采集日志 -->
      <n-tab-pane name="collection" tab="采集日志">
        <n-card title="采集日志" :bordered="false">
          <template #header-extra>
            <n-space>
              <n-select v-model:value="collectionFilters.status" :options="collectionStatusOptions" placeholder="采集状态" clearable style="width: 120px" />
              <n-input v-model:value="collectionFilters.device" placeholder="设备名称" clearable style="width: 150px" />
              <n-button @click="loadCollectionLogs" :loading="collectionLoading">
                <template #icon><n-icon><RefreshOutline /></n-icon></template>
                刷新
              </n-button>
            </n-space>
          </template>

          <n-data-table
            :columns="collectionColumns"
            :data="collectionLogs"
            :loading="collectionLoading"
            :pagination="getLogPagination()"
            :key="logPaginationVersion"
            :remote="true"
            :row-key="row => row.idx"
            :scroll-x="1200"
            size="small"
          />
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, h } from 'vue'
import {
  NCard, NDataTable, NButton, NInput, NSelect, NDatePicker, NTabs, NTabPane,
  NSpace, NTag, NIcon, NEmpty, NTooltip, NBadge
} from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import { useMessage } from 'naive-ui'
import { formatDate } from '@/utils/date'

const message = useMessage()
const activeTab = ref('operation')

// ==================== 分页 refs ====================
const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(0)

// ==================== 操作日志 ====================
const loading = ref(false)
const operationLogs = ref([])
const filters = reactive({ keyword: '', action: null, dateRange: null })

const handleLogPageChange = (p) => {
  logPage.value = p
  logPagination.page = p
  logPaginationVersion.value++
  loadByTab()
}
const handleLogPageSizeChange = (s) => {
  logPageSize.value = s
  logPage.value = 1
  logPagination.pageSize = s
  logPagination.page = 1
  logPaginationVersion.value++
  loadByTab()
}
// 共享纯 JS 对象 — getLogPagination() 每次返回同一引用
const logPagination = {
  page: 1,
  pageSize: 20,
  pageCount: 1,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: handleLogPageChange,
  onUpdatePageSize: handleLogPageSizeChange,
}
const logPaginationVersion = ref(0)
const getLogPagination = () => {
  logPaginationVersion.value
  logPagination.pageCount = Math.max(1, Math.ceil((logTotal.value || 0) / (logPageSize.value || 1)))
  logPagination.itemCount = logTotal.value
  return logPagination
}

// tab 切换时调用对应加载函数
function loadByTab() {
  if (activeTab.value === 'operation') loadOperationLogs()
  else if (activeTab.value === 'system') loadSystemLogs()
  else if (activeTab.value === 'alert') loadAlertAuditLogs()
  else if (activeTab.value === 'collection') loadCollectionLogs()
}

onMounted(() => {
  loadOperationLogs()
})

watch(activeTab, () => {
  logPage.value = 1
  loadByTab()
})

const actionOptions = [
  { label: '登录', value: 'login' }, { label: '登出', value: 'logout' },
  { label: '创建设备', value: 'create_device' }, { label: '更新设备', value: 'update_device' },
  { label: '删除设备', value: 'delete_device' }, { label: '触发采集', value: 'collect' },
  { label: '创建工单', value: 'create_workorder' }, { label: '更新工单', value: 'update_workorder' },
  { label: '更新告警', value: 'update_alert' }, { label: '确认告警', value: 'acknowledge_alert' },
]

const levelTag = (level) => {
  const map = { DEBUG: 'default', INFO: 'info', WARNING: 'warning', ERROR: 'error', CRITICAL: 'error' }
  return map[level?.toUpperCase()] || 'default'
}

const operationColumns = [
  { title: '时间', key: 'timestamp', width: 170, render: (r) => r.timestamp ? formatDate(r.timestamp) : '-' },
  { title: '用户', key: 'username', width: 100 },
  { title: '操作', key: 'action', width: 130, render: (r) => h(NTag, { size: 'small', type: actionOptions.find(o => o.value === r.action) ? 'success' : 'default' }, () => r.action || '-') },
  { title: '资源', key: 'resource', width: 120, ellipsis: { tooltip: true } },
  { title: '路径', key: 'path', width: 200, ellipsis: { tooltip: true } },
  { title: '方法', key: 'method', width: 70 },
  { title: 'IP', key: 'ip_address', width: 130 },
  { title: '状态', key: 'response_status', width: 80, render: (r) => {
    const t = r.response_status >= 400 ? 'error' : r.response_status >= 200 ? 'success' : 'default'
    return h(NTag, { size: 'small', type: t }, () => r.response_status || '-')
  }},
  { title: '耗时', key: 'duration_ms', width: 80, render: (r) => r.duration_ms != null ? `${r.duration_ms}ms` : '-' },
]

async function loadOperationLogs() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({ page: logPage.value, page_size: logPageSize.value })
    if (filters.action) params.set('action', filters.action)
    if (filters.keyword) params.set('operator', filters.keyword)

    const res = await fetch(`/api/v1/admin/logs?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    operationLogs.value = data.items || []
    logTotal.value = data.total || 0
    logPaginationVersion.value++  // 触发 Naive UI 重新读取 pageCount/itemCount
  } catch (e) {
    message.error(`加载操作日志失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

// ==================== 系统日志 ====================
const systemLoading = ref(false)
const systemLogs = ref([])
const systemFilters = reactive({ level: null, keyword: '' })
const logLevelOptions = [
  { label: 'DEBUG', value: 'DEBUG' }, { label: 'INFO', value: 'INFO' },
  { label: 'WARNING', value: 'WARNING' }, { label: 'ERROR', value: 'ERROR' }, { label: 'CRITICAL', value: 'CRITICAL' },
]

const systemColumns = [
  { title: '#', key: 'idx', width: 60 },
  { title: '时间', key: 'time', width: 170 },
  { title: '级别', key: 'level', width: 90, render: (r) => h(NTag, { size: 'small', type: levelTag(r.level) }, () => r.level || '-') },
  { title: '来源', key: 'source', width: 150, ellipsis: { tooltip: true } },
  { title: '日志内容', key: 'message', ellipsis: { tooltip: true } },
]

async function loadSystemLogs() {
  systemLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: logPage.value,
      page_size: logPageSize.value,
    })
    if (systemFilters.level) params.set('level', systemFilters.level)
    if (systemFilters.keyword) params.set('keyword', systemFilters.keyword)
    const res = await fetch(`/api/v1/admin/system-logs?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    systemLogs.value = data.items || []
    logTotal.value = data.total || 0
    logPaginationVersion.value++  // 触发 Naive UI 重新读取 pageCount/itemCount
  } catch (e) {
    message.error(`加载系统日志失败: ${e.message}`)
  } finally {
    systemLoading.value = false
  }
}

function formatUptime(seconds) {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 24) return `${Math.floor(h/24)}天${h%24}小时`
  return `${h}小时${m}分钟`
}

// ==================== 告警审计日志 ====================
const alertLoading = ref(false)
const alertAuditLogs = ref([])

const alertColumns = [
  { title: '时间', key: 'created_at', width: 170, render: (r) => r.created_at ? formatDate(r.created_at) : '-' },
  { title: '告警ID', key: 'alert_id', width: 80 },
  { title: '操作类型', key: 'action', width: 100, render: (r) => {
    const map = { create: '创建', update: '更新', delete: '删除', acknowledge: '确认', resolve: '解决' }
    return map[r.action] || r.action || '-'
  }},
  { title: '操作人', key: 'operator', width: 100 },
  { title: '变更字段', key: 'field_name', width: 120 },
  { title: '原值', key: 'old_value', width: 120, ellipsis: { tooltip: true } },
  { title: '新值', key: 'new_value', width: 120, ellipsis: { tooltip: true } },
  { title: '备注/原因', key: 'reason', ellipsis: { tooltip: true } },
]

async function loadAlertAuditLogs() {
  alertLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: logPage.value,
      page_size: logPageSize.value,
    })
    const res = await fetch(`/api/v1/monitoring/audit-logs?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    alertAuditLogs.value = data.items || []
    logTotal.value = data.total || 0
    logPaginationVersion.value++  // 触发 Naive UI 重新读取 pageCount/itemCount
  } catch (e) {
    message.warning(`告警审计日志接口不可用，显示模拟数据`)
    const now = new Date()
    const levels = ['warning', 'critical', 'info', 'warning', 'critical']
    const messages = [
      'CPU使用率超过阈值 95%，触发告警',
      '内存使用率达到 87%，接近阈值',
      '磁盘空间不足，剩余 8GB',
      '网络延迟增加至 320ms',
      '服务响应超时，已自动恢复'
    ]
    alertAuditLogs.value = Array.from({ length: 5 }, (_, i) => ({
      idx: i + 1,
      timestamp: new Date(now - i * 1800000).toISOString(),
      level: levels[i],
      message: messages[i],
      operator: ['admin', 'system', 'admin', 'system', 'admin'][i],
      action_type: ['告警产生', '告警确认', '告警恢复', '告警升级', '告警处理'][i],
      note: ['自动触发', '人工确认', '系统自动恢复', '需人工介入', '已处理'][i]
    }))
    logTotal.value = alertAuditLogs.value.length
    logPaginationVersion.value++  // 触发 Naive UI 重新读取 pageCount/itemCount
  } finally {
    alertLoading.value = false
  }
}

// ==================== 采集日志 ====================
const collectionLoading = ref(false)
const collectionLogs = ref([])
const collectionFilters = reactive({ status: null, device: '' })
const collectionStatusOptions = [
  { label: '成功', value: 'success' }, { label: '失败', value: 'failed' }, { label: '离线', value: 'offline' },
]

const collectionColumns = [
  { title: '#', key: 'idx', width: 60 },
  { title: '时间', key: 'time', width: 170 },
  { title: '设备', key: 'device', width: 160, ellipsis: { tooltip: true } },
  { title: '协议', key: 'protocol', width: 100 },
  { title: '状态', key: 'status', width: 90, render: (r) => h(NTag, { size: 'small', type: { success: 'success', failed: 'error', offline: 'warning' }[r.status] || 'default' }, () => r.status || '-') },
  { title: '耗时', key: 'duration', width: 80 },
  { title: '消息', key: 'message', ellipsis: { tooltip: true } },
]

async function loadCollectionLogs() {
  collectionLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: logPage.value,
      page_size: logPageSize.value,
    })
    if (collectionFilters.device) params.set('device', collectionFilters.device)
    if (collectionFilters.status) params.set('status', collectionFilters.status)
    const res = await fetch(`/api/v1/admin/collection-logs?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    collectionLogs.value = data.items || []
    logTotal.value = data.total || 0
    logPaginationVersion.value++  // 触发 Naive UI 重新读取 pageCount/itemCount
  } catch (e) {
    message.error(`加载采集日志失败: ${e.message}`)
  } finally {
    collectionLoading.value = false
  }
}

// 切 tab 时加载对应数据
watch(activeTab, () => {
  logPage.value = 1
  loadByTab()
})
</script>

<style scoped>
.logs-container { padding: 16px; }
</style>
