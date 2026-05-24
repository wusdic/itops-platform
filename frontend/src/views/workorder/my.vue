<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>我的工单</span>
          <el-button type="primary" size="small" @click="$router.push('/workorder/create')">
            <el-icon><Plus /></el-icon>
            创建工单
          </el-button>
        </div>
      </template>

      <el-space style="margin-bottom: 12px">
        <el-input v-model="searchKeyword" placeholder="搜索工单标题" clearable style="width: 200px" @input="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="工单状态" clearable style="width: 120px" @change="loadData" />
        <el-select v-model="filterPriority" :options="priorityOptions" placeholder="优先级" clearable style="width: 120px" @change="loadData" />
      </el-space>

      <el-table :data="workorderList" v-loading="loading" :pagination="paginationConfig" row-key="id">
        <el-table-column label="ID" prop="id" width="80" />
        <el-table-column label="工单标题" prop="title" show-overflow-tooltip />
        <el-table-column label="优先级" prop="priority" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理人" prop="assignee_name" width="120" />
        <el-table-column label="创建时间" prop="created_at" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="info" @click="handleView(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 工单详情 -->
    <el-dialog v-model="viewModalVisible" title="工单详情" width="600px" destroy-on-close>
      <el-descriptions v-if="viewData" :column="2" border>
        <el-descriptions-item label="工单ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="工单号">{{ viewData.order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ viewData.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ viewData.type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(viewData.status)" size="small">{{ getStatusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(viewData.priority)" size="small">{{ getPriorityText(viewData.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{ viewData.creator_name || viewData.creator || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ viewData.assignee_name || viewData.assignee || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ viewData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理备注" :span="2">{{ viewData.handling_notes || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ viewData.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewModalVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const loading = ref(false)
const workorderList = ref([])
const searchKeyword = ref('')
const filterStatus = ref(null)
const filterPriority = ref(null)
const viewModalVisible = ref(false)
const viewData = ref(null)

const paginationConfig = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100],
  layout: 'sizes, prev, pager, next',
  onCurrentChange: (page) => { paginationConfig.currentPage = page; loadData(); },
  onSizeChange: (size) => { paginationConfig.pageSize = size; paginationConfig.currentPage = 1; loadData(); }
})

const statusOptions = [
  { label: '全部', value: null },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' }
]

const priorityOptions = [
  { label: '全部', value: null },
  { label: 'P1', value: 'P1' },
  { label: 'P2', value: 'P2' },
  { label: 'P3', value: 'P3' },
  { label: 'P4', value: 'P4' }
]

const getPriorityType = (p) => ({ P1: 'danger', P2: 'warning', P3: 'info', P4: 'info' })[p] || 'info'
const getPriorityText = (p) => ({ P1: 'P1', P2: 'P2', P3: 'P3', P4: 'P4' })[p] || p
const getStatusType = (s) => ({ pending: 'warning', processing: 'info', resolved: 'success', closed: 'info' })[s] || 'info'
const getStatusText = (s) => ({ pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' })[s] || s

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: paginationConfig.currentPage, page_size: paginationConfig.pageSize })
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (filterPriority.value) params.append('priority', filterPriority.value)
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    const res = await fetch(`/api/v1/workorders/?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.status === 401) {
      ElMessage.warning('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
      return
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    workorderList.value = data.items || data.data?.items || []
    paginationConfig.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载工单失败: ${e.message}`)
    workorderList.value = []
  } finally {
    loading.value = false
  }
}

function handleView(row) {
  viewData.value = row
  viewModalVisible.value = true
}

onMounted(() => { loadData() })
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
