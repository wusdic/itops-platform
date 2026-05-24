<template>
  <div class="report-list-container">
    <!-- Statistics Summary Cards -->
    <el-row :gutter="16" class="stats-grid">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total || 0 }}</div>
              <div class="stat-label">报表总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed || 0 }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon failed">
              <el-icon :size="32"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.failed || 0 }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon generating">
              <el-icon :size="32"><RefreshRight /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.generating || 0 }}</div>
              <div class="stat-label">生成中</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <el-card class="filter-card">
      <el-space :size="16" align="center" style="width: 100%; justify-content: space-between;">
        <el-space :size="12" align="center">
          <el-select
            v-model="filters.type"
            :options="typeOptions"
            placeholder="报表类型"
            clearable
            style="width: 150px"
          />
          <el-select
            v-model="filters.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
            style="width: 140px"
          />
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range
            clearable
            placeholder="日期范围"
            style="width: 280px"
          />
        </el-space>
        <el-space :size="12" align="center">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-space>
      </el-space>
    </el-card>

    <!-- Reports Data Table -->
    <el-card class="table-card">
      <el-table :data="reportList" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="报表名称" width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            {{ getTypeLabel(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="template_name" label="模板" width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusConfig(row.status).type" :disable-transitions="true">{{ getStatusConfig(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="format" label="格式" width="90">
          <template #default="{ row }">
            {{ row.format?.toUpperCase() || 'PDF' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateLocal(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" quaternary @click="handlePreview(row)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button size="small" quaternary :disabled="row.status !== 'completed'" @click="handleDownload(row.id)">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button size="small" quaternary type="danger" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchReportList"
        @current-change="fetchReportList"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- Preview Modal -->
    <el-dialog
      v-model="previewModal.show"
      title="报表预览"
      width="80%"
      style="max-width: 1000px"
    >
      <div class="preview-content">
        <div v-loading="previewModal.loading">
          <div v-html="previewModal.content" class="preview-html"></div>
        </div>
      </div>
      <template #footer>
        <el-space justify="end">
          <el-button @click="previewModal.show = false">关闭</el-button>
          <el-button type="primary" @click="handleDownload(previewModal.reportId)">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Modal -->
    <el-dialog
      v-model="deleteModal.show"
      title="确认删除"
      width="400px"
    >
      <p>{{ deleteModal.message }}</p>
      <template #footer>
        <el-button @click="deleteModal.show = false">取消</el-button>
        <el-button type="danger" @click="handleConfirmDelete">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, CircleCheck, CircleClose, RefreshRight, Refresh, Search, View, Download, Delete
} from '@element-plus/icons-vue'

const message = ElMessage
const loading = ref(false)
const reportList = ref([])
const stats = ref({})

// Filters
const filters = reactive({
  type: null,
  status: null,
  dateRange: null
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// Options
const typeOptions = [
  { label: '日报', value: 'daily' },
  { label: '周报', value: 'weekly' },
  { label: '月报', value: 'monthly' },
  { label: '季报', value: 'quarterly' },
  { label: '年报', value: 'annual' },
  { label: '自定义', value: 'custom' }
]

const statusOptions = [
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' },
  { label: '生成中', value: 'generating' },
  { label: '待处理', value: 'pending' }
]

// Preview Modal
const previewModal = reactive({
  show: false,
  loading: false,
  content: '',
  reportId: null
})

// Delete Modal
const deleteModal = reactive({
  show: false,
  message: '',
  reportId: null
})

// Helper Functions
function getTypeLabel(type) {
  const labels = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报',
    quarterly: '季报',
    annual: '年报',
    custom: '自定义'
  }
  return labels[type] || type
}

function getStatusConfig(status) {
  const config = {
    completed: { type: 'success', label: '已完成' },
    failed: { type: 'danger', label: '失败' },
    generating: { type: 'primary', label: '生成中' },
    pending: { type: 'warning', label: '待处理' }
  }
  return config[status] || { type: 'info', label: status }
}

function formatDateLocal(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}

// API Functions
async function fetchStats() {
  try {
    const response = await fetch('/api/v1/reports/stats', {
      method: 'GET',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    stats.value = data
  } catch (error) {
    message.error('加载统计数据失败')
    stats.value = { total: 0, completed: 0, failed: 0, generating: 0 }
  }
}

async function fetchReportList() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    
    if (filters.type) params.append('type', filters.type)
    if (filters.status) params.append('status', filters.status)
    if (filters.dateRange && filters.dateRange[0]) {
      params.append('start_date', new Date(filters.dateRange[0]).toISOString())
      params.append('end_date', new Date(filters.dateRange[1]).toISOString())
    }

    const response = await fetch(`/api/v1/reports/?${params}`, {
      method: 'GET',
      headers: getHeaders()
    })
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    reportList.value = data.items || data
    pagination.total = data.total || reportList.value.length
  } catch (error) {
    message.error('加载报表列表失败')
    reportList.value = []
  } finally {
    loading.value = false
  }
}

async function fetchReportPreview(id) {
  previewModal.loading = true
  try {
    const response = await fetch(`/api/v1/reports/${id}/preview`, {
      method: 'GET',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    previewModal.content = data.content || data.html || '<p>暂无预览</p>'
  } catch (error) {
    message.error('加载报表预览失败')
    previewModal.content = '<p>预览不可用</p>'
  } finally {
    previewModal.loading = false
  }
}

async function downloadReport(id) {
  try {
    const response = await fetch(`/api/v1/reports/${id}/download`, {
      method: 'GET',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${id}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    message.success('报表下载成功')
  } catch (error) {
    message.error('下载报表失败')
  }
}

async function deleteReport(id) {
  try {
    const response = await fetch(`/api/v1/reports/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    message.success('报表删除成功')
    fetchReportList()
    fetchStats()
  } catch (error) {
    message.error('删除报表失败')
  }
}

// Action Handlers
function handleSearch() {
  pagination.page = 1
  fetchReportList()
}

function handleReset() {
  filters.type = null
  filters.status = null
  filters.dateRange = null
  pagination.page = 1
  fetchReportList()
}

function handleRefresh() {
  fetchReportList()
  fetchStats()
}

function handlePreview(row) {
  previewModal.reportId = row.id
  previewModal.show = true
  previewModal.content = ''
  fetchReportPreview(row.id)
}

function handleDownload(id) {
  downloadReport(id)
}

function handleDelete(row) {
  deleteModal.reportId = row.id
  deleteModal.message = `Are you sure you want to delete report "${row.name}"? This action cannot be undone.`
  deleteModal.show = true
}

function handleConfirmDelete() {
  if (deleteModal.reportId) {
    deleteReport(deleteModal.reportId)
  }
  deleteModal.show = false
}

// Lifecycle
onMounted(() => {
  fetchReportList()
  fetchStats()
})
</script>

<style scoped>
.report-list-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-grid {
  margin-bottom: 8px;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
}

.stat-icon.failed {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.stat-icon.generating {
  background: linear-gradient(135deg, #1890ff 0%, #69c0ff 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 8px;
}

.table-card {
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.preview-content {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.preview-html {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>