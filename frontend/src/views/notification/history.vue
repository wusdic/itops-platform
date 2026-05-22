<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">消息中心 / 消息历史</h1>
        <p class="page-subtitle">查看历史通知消息</p>
      </div>
      <div class="page-actions">
        <n-button @click="loadData">
          <template #icon><n-icon><Refresh /></n-icon></template>
          刷新
        </n-button>
        <n-button @click="markAllRead">
          <template #icon><n-icon><CheckmarkDoneOutline /></n-icon></template>
          全部已读
        </n-button>
      </div>
    </div>

    <n-card class="mb-4">
      <n-space align="center">
        <n-select v-model:value="filterType" :options="typeOptions" placeholder="按类型筛选" clearable style="width: 150px" @update:value="loadData" />
        <n-select v-model:value="filterChannel" :options="channelOptions" placeholder="按渠道筛选" clearable style="width: 150px" @update:value="loadData" />
        <n-select v-model:value="filterRead" :options="readOptions" placeholder="按阅读状态筛选" clearable style="width: 150px" @update:value="loadData" />
        <n-button @click="clearFilters">清除筛选</n-button>
      </n-space>
    </n-card>

    <n-card>
      <n-data-table
        :columns="columns"
        :data="list"
        :loading="loading"
        :pagination="pagination"
        :row-key="row => row.id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </n-card>

    <n-modal v-model:show="detailModalVisible" preset="card" title="消息详情" style="width: 500px">
      <n-descriptions v-if="currentMessage" label-placement="top" :column="1">
        <n-descriptions-item label="类型">
          <n-tag :type="getTypeColor(currentMessage.type)">{{ currentMessage.type }}</n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="渠道">{{ currentMessage.channel }}</n-descriptions-item>
        <n-descriptions-item label="标题">{{ currentMessage.title }}</n-descriptions-item>
        <n-descriptions-item label="内容">{{ currentMessage.content }}</n-descriptions-item>
        <n-descriptions-item label="状态">
          <n-tag :type="currentMessage.read ? 'success' : 'warning'">{{ currentMessage.read ? '已读' : '未读' }}</n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="时间">{{ currentMessage.created_at }}</n-descriptions-item>
      </n-descriptions>
      <template #footer>
        <n-space justify="end">
          <n-button v-if="!currentMessage?.read" type="primary" @click="markAsRead">标记已读</n-button>
          <n-button @click="detailModalVisible = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { NIcon } from 'naive-ui'
import { Refresh, CheckmarkDoneOutline } from '@vicons/ionicons5'
import { useMessage, NTag, NButton, NButtonGroup, NDescriptions, NDescriptionsItem } from 'naive-ui'

const message = useMessage()
const loading = ref(false)
const list = ref([])
const filterType = ref(null)
const filterChannel = ref(null)
const filterRead = ref(null)
const detailModalVisible = ref(false)
const currentMessage = ref(null)

const typeOptions = [
  { label: '告警', value: 'alert' },
  { label: '维护', value: 'maintenance' },
  { label: '通知', value: 'info' }
]

const channelOptions = [
  { label: '站内信', value: 'in_app' },
  { label: '邮件', value: 'email' },
  { label: '短信', value: 'sms' },
  { label: 'webhook', value: 'webhook' }
]

const readOptions = [
  { label: '已读', value: true },
  { label: '未读', value: false }
]

const pagination = {
  page: 1,
  pageSize: 10,
  total: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => { pagination.page = page; loadData(); },
  onUpdatePageSize: (size) => { pagination.pageSize = size; pagination.page = 1; loadData(); }
}

const columns = [
  { title: '序号', type: 'index', width: 60 },
  { title: '类型', key: 'type', width: 100,
    render: (row) => h(NTag, { type: getTypeColor(row.type), size: 'small' }, () => row.type)
  },
  { title: '渠道', key: 'channel', width: 100 },
  { title: '标题', key: 'title', width: 200, ellipsis: { tooltip: true } },
  { title: '内容', key: 'content', ellipsis: { tooltip: true } },
  { title: '状态', key: 'read', width: 100,
    render: (row) => h(NTag, { type: row.read ? 'success' : 'warning', size: 'small' }, () => row.read ? '已读' : '未读')
  },
  { title: '时间', key: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 120,
    render: (row) => h(NButtonGroup, {}, () => [
      h(NButton, { size: 'small', onClick: () => showDetail(row) }, () => '查看'),
      h(NButton, { size: 'small', onClick: () => toggleRead(row) }, () => row.read ? '标记未读' : '标记已读')
    ])
  }
]

onMounted(() => { loadData() })

const loadData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: pagination.page, page_size: pagination.pageSize })
    if (filterType.value) params.append('type', filterType.value)
    if (filterChannel.value) params.append('channel', filterChannel.value)
    if (filterRead.value !== null) params.append('read', filterRead.value)
    const res = await fetch(`/api/v1/notifications/history?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (!data || typeof data !== 'object') throw new Error('响应格式异常')
    list.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
  } catch (e) {
    message.error(`加载失败: ${e.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => { pagination.page = page; loadData() }
const handlePageSizeChange = (pageSize) => { pagination.pageSize = pageSize; pagination.page = 1; loadData() }
const showDetail = (row) => { currentMessage.value = row; detailModalVisible.value = true }

const markAsRead = async () => {
  if (!currentMessage.value) return
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/notifications/history/${currentMessage.value.id}/read`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    currentMessage.value.read = true
    loadData()
    detailModalVisible.value = false
  } catch (e) {
    message.error(`标记失败: ${e.message}`)
  }
}

const toggleRead = async (row) => {
  try {
    const token = localStorage.getItem('token') || ''
    const method = row.read ? 'DELETE' : 'PUT'
    const res = await fetch(`/api/v1/notifications/history/${row.id}/read`, {
      method,
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    loadData()
  } catch (e) {
    message.error(`操作失败: ${e.message}`)
  }
}

const markAllRead = async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/notifications/history/mark-all-read', {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    message.success('已全部标记为已读')
    loadData()
  } catch (e) {
    message.error(`操作失败: ${e.message}`)
  }
}

const clearFilters = () => { filterType.value = null; filterChannel.value = null; filterRead.value = null; loadData() }
const getTypeColor = (type) => ({ alert: 'error', maintenance: 'warning', info: 'info' }[type] || 'default')
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 4px 0 0 0; }
.page-actions { display: flex; gap: 8px; }
.mb-4 { margin-bottom: 16px; }
</style>
