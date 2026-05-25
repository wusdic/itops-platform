<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">备份列表</h1>
        <p class="page-subtitle">查看和管理数据备份记录</p>
      </div>
      <el-button type="primary" @click="loadData" :loading="loading">刷新</el-button>
    </div>

    <el-card class="filter-bar">
      <el-space align="center" wrap>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索备份名称"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
        <el-select v-model="filterType" placeholder="备份类型" clearable style="width: 120px" @change="loadData">
          <el-option label="全量" value="full" />
          <el-option label="增量" value="incremental" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="备份状态" clearable style="width: 120px" @change="loadData">
          <el-option label="完成" value="completed" />
          <el-option label="失败" value="failed" />
          <el-option label="进行中" value="running" />
        </el-select>
      </el-space>
    </el-card>

    <el-card class="table-container">
      <el-table :data="filteredList" :loading="loading" row-key="id" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="备份名称" :show-overflow-tooltip="true" minWidth="180" />
        <el-table-column prop="backup_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.backup_type === 'full' ? 'success' : 'info'" size="small">
              {{ typeText(row.backup_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">{{ row.size || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_by" label="操作人" width="120" />
        <el-table-column prop="created_at" label="备份时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="8">
              <el-button size="small" @click="handleView(row)">详情</el-button>
              <el-button
                size="small"
                type="primary"
                :disabled="row.status !== 'completed'"
                @click="handleRestore(row)"
              >恢复</el-button>
            </el-space>
          </template>
        </el-table-column>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailModalVisible" title="备份详情" width="560px">
      <el-descriptions v-if="currentBackup" :column="1" border>
        <el-descriptions-item label="ID">{{ currentBackup.id }}</el-descriptions-item>
        <el-descriptions-item label="备份名称">{{ currentBackup.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ typeText(currentBackup.backup_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(currentBackup.status)" size="small">
            {{ statusText(currentBackup.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="大小">{{ currentBackup.size || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentBackup.created_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备份时间">{{ formatTime(currentBackup.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentBackup.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailModalVisible = false">关闭</el-button>
          <el-button
            type="primary"
            :disabled="!currentBackup || currentBackup.status !== 'completed'"
            @click="handleRestore(currentBackup); detailModalVisible = false"
          >恢复此备份</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { backup } from '@/api'

const loading = ref(false)
const backupList = ref([])
const searchKeyword = ref('')
const filterType = ref(null)
const filterStatus = ref(null)
const detailModalVisible = ref(false)
const currentBackup = ref(null)

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const totalPages = computed(() => Math.ceil(pagination.total / pagination.pageSize) || 1)

const filteredList = computed(() => {
  if (!searchKeyword.value) return backupList.value
  const kw = searchKeyword.value.toLowerCase()
  return backupList.value.filter(
    (b) => b.name?.toLowerCase().includes(kw) || b.created_by?.toLowerCase().includes(kw)
  )
})

const typeText = (t) => ({ full: '全量', incremental: '增量', differential: '差异' }[t] || t)
const statusTagType = (s) => ({ completed: 'success', failed: 'danger', running: 'warning' }[s] || 'info')
const statusText = (s) => ({ completed: '完成', failed: '失败', running: '进行中' }[s] || s)

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { limit: pagination.pageSize }
    if (filterType.value) params.backup_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await backup.getList(params)
    backupList.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    backupList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  // 前端过滤
}

const handleView = (row) => {
  currentBackup.value = row
  detailModalVisible.value = true
}

const handleRestore = async (row) => {
  if (!row) return
  try {
    await ElMessageBox.confirm(
      `确定要恢复备份"${row.name}"吗？恢复操作会覆盖当前数据，此操作不可逆。`,
      '确认恢复',
      { type: 'warning', confirmButtonText: '确认恢复', cancelButtonText: '取消' }
    )
    await backup.restore(row.id, { target: 'all', create_pre_backup: true })
    ElMessage.success('恢复任务已创建')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(`恢复失败: ${e.message}`)
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 4px 0 0 0; }
.filter-bar { margin-bottom: 16px; }
.table-container { margin-bottom: 16px; }
.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
