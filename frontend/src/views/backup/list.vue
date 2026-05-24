<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">备份列表</h1>
        <p class="page-subtitle">查看和管理数据备份记录</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="loadData">刷新</el-button>
      </div>
    </div>

    <el-card class="filter-bar">
      <el-space align="center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索备份名称"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
        <el-select
          v-model="filterType"
          placeholder="备份类型"
          :options="typeOptions"
          clearable
          style="width: 120px"
          @change="handleSearch"
        />
        <el-select
          v-model="filterStatus"
          placeholder="备份状态"
          :options="statusOptions"
          clearable
          style="width: 120px"
          @change="handleSearch"
        />
        <el-date-picker
          v-model="timeRange"
          type="daterange"
          clearable
          style="width: 260px"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleSearch"
        />
      </el-space>
    </el-card>

    <el-card class="table-container">
      <el-table
        :data="backupList"
        :loading="loading"
        :row-key="(row) => row.id"
        style="width: 100%"
      >
        <el-table-column v-for="col in columns" :key="col.key" v-bind="col" />
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-count="totalPages"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          show-quick-jumper
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailModalVisible" title="备份详情" width="600px" max-width="600px">
      <el-descriptions label-placement="top" :column="1" border v-if="currentBackup">
        <el-descriptions-item label="备份名称">{{ currentBackup.name || currentBackup.backup_name }}</el-descriptions-item>
        <el-descriptions-item label="备份类型">{{ currentBackup.type === 'full' ? '全量' : '增量' }}</el-descriptions-item>
        <el-descriptions-item label="备份时间">{{ formatTime(currentBackup.backup_at || currentBackup.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="备份大小">{{ currentBackup.size || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ currentBackup.status === 'success' ? '成功' : '失败' }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentBackup.operator || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentBackup.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailModalVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleRestore">恢复此备份</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/date'

const loading = ref(false)
const searchKeyword = ref('')
const filterType = ref(null)
const filterStatus = ref(null)
const timeRange = ref(null)
const backupList = ref([])
const detailModalVisible = ref(false)
const currentBackup = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})
const totalPages = computed(() => Math.ceil(pagination.total / pagination.pageSize) || 1)

const typeOptions = [
  { label: '全量', value: 'full' },
  { label: '增量', value: 'incremental' }
]

const statusOptions = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '进行中', value: 'running' }
]

const getTypeText = (type) => {
  return type === 'full' ? '全量' : '增量'
}

const getStatusTagType = (status) => {
  const map = { success: 'success', failed: 'danger', running: 'warning' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { success: '成功', failed: '失败', running: '进行中' }
  return map[status] || status
}

const formatTime = (time) => {
  if (!time) return '-'
  return formatDate(new Date(time))
}

const columns = [
  { title: '备份名称', key: 'name', minWidth: 180 },
  {
    title: '备份类型',
    key: 'type',
    width: 100,
    render: ({ row }) => h(ElTag, { type: 'info', size: 'small' }, () => getTypeText(row.type))
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: ({ row }) => h(ElTag, { type: getStatusTagType(row.status), size: 'small' }, () => getStatusText(row.status))
  },
  { title: '备份时间', key: 'backup_at', width: 180, render: ({ row }) => formatTime(row.backup_at || row.created_at) },
  { title: '备份大小', key: 'size', width: 120 },
  { title: '操作人', key: 'operator', width: 120 },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: ({ row }) => h(ElSpace, { size: 'small' }, () => [
      h(ElButton, { size: 'small', onClick: () => handleView(row) }, () => '详情'),
      h(ElButton, { size: 'small', type: 'primary', onClick: () => handleRestore(row) }, () => '恢复')
    ])
  }
]

const fetchApi = async (url, options = {}) => {
  const token = localStorage.getItem('token') || ''
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers
    }
  })
  if (!res.ok) throw new Error(`HTTP error ${res.status}`)
  return res.json()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    if (filterType.value) params.append('type', filterType.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (timeRange.value && timeRange.value[0]) {
      params.append('start_time', new Date(timeRange.value[0]).toISOString())
      params.append('end_time', new Date(timeRange.value[1]).toISOString())
    }

    const res = await fetchApi(`/api/v1/admin/backups?${params}`)
    // Support both {items, total} and {data, total} formats
    if (res.items) {
      backupList.value = res.items
      pagination.total = res.total || 0
    } else if (res.data && Array.isArray(res.data)) {
      backupList.value = res.data
      pagination.total = res.total || 0
    } else if (Array.isArray(res)) {
      backupList.value = res
      pagination.total = res.length
    } else {
      backupList.value = []
      pagination.total = 0
    }
  } catch (error) {
    backupList.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleView = (row) => {
  currentBackup.value = row
  detailModalVisible.value = true
}

const handleRestore = async (row) => {
  if (row) {
    currentBackup.value = row
  }
  if (!currentBackup.value) return

  try {
    await ElMessageBox.confirm(
      `确定要恢复备份 "${currentBackup.value.name || currentBackup.value.backup_name}" 吗？恢复操作会覆盖当前数据，此操作不可逆。`,
      '确认恢复',
      {
        confirmButtonText: '确认恢复',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/admin/backups/${currentBackup.value.id}/restore`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({})
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: `HTTP ${res.status}` }))
      ElMessage.error(`恢复失败: ${err.message || res.status}`)
      return
    }
    ElMessage.success('备份恢复成功')
    detailModalVisible.value = false
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(`恢复失败: ${e.message}`)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}
.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 4px 0 0 0;
}
.filter-bar {
  margin-bottom: 16px;
}
.table-container {
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
