<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">消息中心</h1>
        <p class="page-subtitle">查看系统通知和告警消息</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="loadData">刷新</el-button>
      </div>
    </div>

    <el-card class="filter-bar">
      <el-space>
        <el-select v-model="filterRead" placeholder="消息状态" clearable style="width: 140px" @change="handleSearch">
          <el-option label="未读" :value="0" />
          <el-option label="已读" :value="1" />
        </el-select>
        <el-button @click="handleMarkAllRead">全部标为已读</el-button>
      </el-space>
    </el-card>

    <el-card class="message-list-container">
      <div v-if="messages.length > 0">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-item"
          :class="{ unread: !msg.is_read }"
          @click="handleViewMessage(msg)"
        >
          <div class="message-main">
            <div class="message-header">
              <el-badge :is-dot="!msg.is_read">
                <span :class="{ 'unread-title': !msg.is_read }">{{ msg.title }}</span>
              </el-badge>
              <el-tag :type="getTypeTag(msg.type)" size="small">{{ getTypeText(msg.type) }}</el-tag>
            </div>
            <p class="message-content">{{ msg.content }}</p>
            <span class="message-time">{{ formatTime(msg.created_at) }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无消息" />
      <div class="pagination" v-if="messages.length > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadData"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailModalVisible" title="消息详情" width="500px">
      <el-descriptions :column="1" border v-if="currentMessage">
        <el-descriptions-item label="标题">{{ currentMessage.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ getTypeText(currentMessage.type) }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatTime(currentMessage.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentMessage.content }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailModalVisible = false">关闭</el-button>
          <el-button
            v-if="currentMessage && !currentMessage.is_read"
            type="primary"
            @click="handleMarkRead(currentMessage)"
          >
            标为已读
          </el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { notification } from '@/api/notification'

const loading = ref(false)
const filterRead = ref(null)
const messages = ref([])
const detailModalVisible = ref(false)
const currentMessage = ref(null)

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const getTypeTag = (type) => {
  const map = { info: 'info', warning: 'warning', error: 'danger', success: 'success' }
  return map[type] || 'info'
}

const getTypeText = (type) => {
  const map = { info: '通知', warning: '警告', error: '错误', success: '成功' }
  return map[type] || '通知'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterRead.value !== null && filterRead.value !== '') {
      params.is_read = filterRead.value
    }

    const res = await notification.getHistory(params)
    const data = res.data || res
    if (data.items) {
      messages.value = data.items
      pagination.total = data.total || 0
    } else if (data.data && Array.isArray(data.data)) {
      messages.value = data.data
      pagination.total = data.total || 0
    } else if (Array.isArray(data)) {
      messages.value = data
      pagination.total = data.length
    } else {
      messages.value = []
      pagination.total = 0
    }
  } catch (error) {
    messages.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

const handleViewMessage = (msg) => {
  currentMessage.value = msg
  detailModalVisible.value = true
  if (!msg.is_read) {
    handleMarkRead(msg)
  }
}

const handleMarkRead = async (msg) => {
  try {
    await notification.markAllRead()
    msg.is_read = true
    ElMessage.success('已标为已读')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleMarkAllRead = async () => {
  try {
    await notification.markAllRead()
    ElMessage.success('全部已标为已读')
    loadData()
  } catch (e) { ElMessage.error('操作失败') }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 4px 0 0 0; }
.filter-bar { margin-bottom: 16px; }
.message-list-container { margin-bottom: 16px; }
.message-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.message-item:last-child { border-bottom: none; }
.message-item:hover { background: #fafafa; }
.unread { background: #f0f7ff; }
.message-main { display: flex; flex-direction: column; gap: 6px; }
.message-header { display: flex; align-items: center; gap: 8px; }
.unread-title { font-weight: 600; }
.message-content { margin: 4px 0 0; color: #666; font-size: 14px; }
.message-time { font-size: 12px; color: #999; }
.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
