<template>
  <div class="page-container">
    <el-card title="备份管理" :bordered="false">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>备份管理</span>
          <el-button type="primary" @click="handleCreate" :loading="creating">
            <el-icon><Upload /></el-icon>
            创建备份
          </el-button>
        </div>
      </template>

      <el-tabs v-model="filterType" @tab-change="loadData">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="全量备份" name="full" />
        <el-tab-pane label="增量备份" name="incremental" />
      </el-tabs>

      <el-input v-model="searchKeyword" placeholder="搜索备份名称" clearable style="width: 200px; margin-bottom: 12px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>

      <el-table
        :data="filteredBackupList"
        :loading="loading"
        row-key="id"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="备份名称" :show-overflow-tooltip="true" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'full' ? 'success' : 'info'" size="small">
              {{ row.type === 'full' ? '全量' : '增量' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="creator_name" label="创建人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="备份时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="8">
              <el-button size="small" quaternary type="info" :disabled="row.status !== 'completed'" @click="handleDownload(row)">下载</el-button>
              <el-button size="small" quaternary type="danger" :disabled="row.status !== 'completed'" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 执行结果抽屉 -->
    <el-drawer v-model="resultDrawer" :size="600" direction="rtl">
      <template #title>
        <span>执行结果</span>
      </template>
      <el-icon v-if="executing" class="is-loading" style="font-size: 24px;"><Loading /></el-icon>
      <el-input v-else type="textarea" :model-value="formatResult(executeResult)" :rows="15" readonly placeholder="暂无执行结果" style="font-family: monospace;" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, Loading } from '@element-plus/icons-vue'

const loading = ref(false)
const creating = ref(false)
const executing = ref(false)
const backupList = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const resultDrawer = ref(false)
const executeResult = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const filteredBackupList = computed(() => {
  if (!searchKeyword.value) return backupList.value
  const kw = searchKeyword.value.toLowerCase()
  return backupList.value.filter(item =>
    (item.name && item.name.toLowerCase().includes(kw)) ||
    (item.creator_name && item.creator_name.toLowerCase().includes(kw)) ||
    (item.type && item.type.toLowerCase().includes(kw)) ||
    (item.status && item.status.toLowerCase().includes(kw))
  )
})

const formatResult = (data) => {
  if (!data) return ''
  if (typeof data === 'string') return data
  try {
    const obj = typeof data === 'object' ? data : JSON.parse(data)
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(data)
  }
}

const statusTagType = (status) => {
  const map = { completed: 'success', failed: 'danger', running: 'warning' }
  return map[status] || 'info'
}

const statusText = (status) => {
  const map = { completed: '完成', failed: '失败', running: '进行中' }
  return map[status] || status
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: pagination.page, page_size: pagination.pageSize })
    if (filterType.value) params.append('type', filterType.value)
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    const res = await fetch(`/api/v1/admin/backups?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) {
      if (res.status === 500) {
        ElMessage.warning('备份功能暂无可用数据')
        backupList.value = []
        return
      }
      throw new Error(`HTTP ${res.status}`)
    }
    const data = await res.json()
    if (!data || typeof data !== 'object') throw new Error('响应格式异常')
    backupList.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载备份失败: ${e.message}`)
    backupList.value = []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  creating.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/admin/backups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ type: 'full', name: `backup_${Date.now()}` })
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const result = await res.json()
    ElMessage.success('备份创建成功')
    loadData()
  } catch (e) {
    ElMessage.error(`创建备份失败: ${e.message}`)
  } finally {
    creating.value = false
  }
}

function handleDownload(row) {
  ElMessage.info(`下载功能开发中: ${row.name}`)
}

async function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除备份 "${row.name}" 吗？此操作不可逆。`, '确认删除', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token') || ''
      const res = await fetch(`/api/v1/admin/backups/${row.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.error(`删除失败: ${e.message}`)
    }
  }).catch(e => ElMessage.error(`删除失败: ${e.message}`))
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 16px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
.is-loading { animation: rotating 2s linear infinite; }
@keyframes rotating { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
