<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>回滚历史</span>
          <el-button quaternary @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-space style="margin-bottom: 12px">
        <el-input v-model.trim="searchKeyword" placeholder="搜索执行ID或规则名称" clearable style="width: 240px" @change="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="回滚状态" clearable style="width: 140px" @change="loadData" />
      </el-space>

      <el-table :data="rollbackList" v-loading="loading" style="width: 100%">
        <el-table-column prop="execution_id" label="执行ID" width="120" />
        <el-table-column prop="rule_name" label="规则名称" show-overflow-tooltip />
        <el-table-column prop="device_id" label="设备ID" width="100" />
        <el-table-column prop="metric_name" label="指标" show-overflow-tooltip />
        <el-table-column prop="trigger_value" label="触发值" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" label="触发时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" quaternary type="info" @click="handleDetail(row)">详情</el-button>
            <el-button size="small" quaternary type="primary" @click="handleViewSnapshot(row)">快照</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 快照详情 -->
    <el-dialog v-model="snapshotDialogVisible" title="执行快照" width="800px">
      <div v-loading="snapshotLoading" style="padding: 8px 0;">
        <el-input type="textarea" v-model="snapshotDetail" :rows="25" readonly placeholder="暂无快照数据" />
      </div>
      <template #footer>
        <el-space justify="end">
          <el-button @click="snapshotDialogVisible = false">关闭</el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 回滚详情抽屉 -->
    <el-drawer v-model="detailDrawer" :size="600" direction="rtl">
      <template #title>
        <span>回滚详情</span>
      </template>
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentRollback" :column="1" border>
          <el-descriptions-item label="执行ID">{{ currentRollback.execution_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="规则名称">{{ currentRollback.rule_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="触发时间">{{ currentRollback.triggered_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentRollback.status)">{{ getStatusText(currentRollback.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="设备ID">{{ currentRollback.device_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="指标名称">{{ currentRollback.metric_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="触发值">{{ currentRollback.trigger_value ?? '-' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div v-if="currentRollback && currentRollback.actions_taken">
          <div style="font-weight: 500; margin-bottom: 8px;">执行的操作:</div>
          <el-input type="textarea" :value="formatActions(currentRollback.actions_taken)" :rows="8" readonly />
        </div>
        <el-empty v-else description="暂无操作详情" />
      </div>
      <template #footer>
        <el-space justify="end">
          <el-button @click="handleViewSnapshot">查看快照</el-button>
          <el-button @click="detailDrawer = false">关闭</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { automation } from '@/api'

const message = ElMessage
const loading = ref(false)
const snapshotLoading = ref(false)
const detailLoading = ref(false)
const rollbackList = ref([])
const searchKeyword = ref('')
const filterStatus = ref(null)
const detailDrawer = ref(false)
const snapshotDialogVisible = ref(false)
const currentRollback = ref(null)
const snapshotDetail = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statusOptions = [
  { label: '全部', value: null },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '进行中', value: 'running' },
  { label: '回滚中', value: 'rolling_back' }
]

function getStatusType(status) {
  const map = { success: 'success', failed: 'danger', running: 'warning', rolling_back: 'primary', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { success: '成功', failed: '失败', running: '进行中', rolling_back: '回滚中', pending: '待处理' }
  return map[status] || status || '-'
}

function formatActions(actions) {
  if (typeof actions === 'string') {
    try {
      return JSON.stringify(JSON.parse(actions), null, 2)
    } catch {
      return actions
    }
  }
  return JSON.stringify(actions, null, 2)
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await automation.rollbackHistory.getList(params)
    if (!res || typeof res !== 'object') throw new Error('响应格式异常')
    rollbackList.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    message.error(`加载回滚历史失败: ${e.message}`)
    rollbackList.value = []
  } finally {
    loading.value = false
  }
}

async function handleDetail(row) {
  currentRollback.value = row
  detailDrawer.value = true
}

async function handleViewSnapshot(row) {
  const executionId = row?.execution_id || currentRollback.value?.execution_id
  if (!executionId) {
    message.warning('无法获取执行ID')
    return
  }
  currentRollback.value = row || currentRollback.value
  snapshotDialogVisible.value = true
  snapshotDetail.value = ''
  snapshotLoading.value = true
  try {
    const data = await automation.executions.getSnapshot(executionId)
    snapshotDetail.value = JSON.stringify(data, null, 2)
  } catch (e) {
    snapshotDetail.value = `加载快照失败: ${e.message}`
    message.error(`加载快照失败: ${e.message}`)
  } finally {
    snapshotLoading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 16px; }
</style>