<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">消息中心 / 消息历史</h1>
        <p class="page-subtitle">查看历史通知消息</p>
      </div>
      <div class="page-actions">
        <el-button @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="markAllRead">
          <el-icon><Check /></el-icon>
          全部已读
        </el-button>
      </div>
    </div>

    <el-card class="mb-4" shadow="never">
      <el-space align="center">
        <el-select v-model="filterType" placeholder="按类型筛选" clearable :options="typeOptions" style="width: 150px" @change="loadData" />
        <el-select v-model="filterChannel" placeholder="按渠道筛选" clearable :options="channelOptions" style="width: 150px" @change="loadData" />
        <el-select v-model="filterRead" placeholder="按阅读状态筛选" clearable :options="readOptions" style="width: 150px" @change="loadData" />
        <el-button @click="clearFilters">清除筛选</el-button>
      </el-space>
    </el-card>

    <el-card shadow="never">
      <el-table
        :data="list"
        v-loading="loading"
        :pagination="paginationConfig"
        row-key="id"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      >
        <el-table-column label="序号" type="index" width="60" />
        <el-table-column label="类型" prop="type" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="渠道" prop="channel" width="100" />
        <el-table-column label="标题" prop="title" width="200" show-overflow-tooltip />
        <el-table-column label="内容" prop="content" show-overflow-tooltip />
        <el-table-column label="状态" prop="read" width="100">
          <template #default="{ row }">
            <el-tag :type="row.read ? 'success' : 'warning'" size="small">{{ row.read ? '已读' : '未读' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" prop="created_at" width="180" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button size="small" link @click="showDetail(row)">查看</el-button>
            <el-button size="small" link @click="toggleRead(row)">{{ row.read ? '标记未读' : '标记已读' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && messageList.length === 0" description="暂无数据" />
    </el-card>

    <el-dialog v-model="detailModalVisible" title="消息详情" width="500px" destroy-on-close>
      <el-descriptions v-if="currentMessage" direction="vertical" :column="1" border>
        <el-descriptions-item label="类型">
          <el-tag :type="getTypeColor(currentMessage.type)">{{ currentMessage.type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="渠道">{{ currentMessage.channel }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ currentMessage.title }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentMessage.content }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentMessage.read ? 'success' : 'warning'">{{ currentMessage.read ? '已读' : '未读' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatDate(currentMessage.created_at, 'YYYY-MM-DD HH:mm') }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space justify="end">
          <el-button v-if="!currentMessage?.read" type="primary" @click="markAsRead">标记已读</el-button>
          <el-button @click="detailModalVisible = false">关闭</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Check } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'

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

const paginationConfig = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100],
  layout: 'sizes, prev, pager, next',
  onCurrentChange: (page) => { paginationConfig.currentPage = page; loadData(); },
  onSizeChange: (size) => { paginationConfig.pageSize = size; paginationConfig.currentPage = 1; loadData(); }
})

onMounted(() => { loadData() })

const loadData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: paginationConfig.currentPage, page_size: paginationConfig.pageSize })
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
    paginationConfig.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载失败: ${e.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => { paginationConfig.currentPage = page; loadData() }
const handlePageSizeChange = (pageSize) => { paginationConfig.pageSize = pageSize; paginationConfig.currentPage = 1; loadData() }
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
    ElMessage.error(`标记失败: ${e.message}`)
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
    ElMessage.error(`操作失败: ${e.message}`)
  }
}

const markAllRead = async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/notifications/history/read-all', {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success('已全部标记为已读')
    loadData()
  } catch (e) {
    ElMessage.error(`操作失败: ${e.message}`)
  }
}

const clearFilters = () => { filterType.value = null; filterChannel.value = null; filterRead.value = null; loadData() }
const getTypeColor = (type) => ({ alert: 'danger', maintenance: 'warning', info: 'info' }[type] || 'info')
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 4px 0 0 0; }
.page-actions { display: flex; gap: 8px; }
.mb-4 { margin-bottom: 16px; }
</style>
