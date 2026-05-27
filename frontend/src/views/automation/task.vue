<template>
  <div class="page-container">
    <el-card>
      <el-tabs type="border-card">
        <el-tab-pane label="历史记录">
          <el-space style="margin-bottom: 12px">
            <el-button quaternary @click="loadHistory" :loading="historyLoading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-space>
          <el-table
            :data="historyList"
            :loading="historyLoading"
            :row-key="row => row.execution_id"
            stripe
            border
          >
            <el-table-column prop="execution_id" label="执行ID" width="120" />
            <el-table-column prop="device_id" label="设备ID" width="100" />
            <el-table-column prop="metric_name" label="指标名称" show-overflow-tooltip />
            <el-table-column prop="current_value" label="当前值" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="props">
                <el-tag :type="getStatusType(props.row.status)" size="small">
                  {{ getStatusText(props.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="triggered_at" label="触发时间" width="180" />
            <el-table-column label="操作" width="100">
              <template #default="props">
                <el-button size="small" link type="info" @click="handleViewSnapshot(props.row)">快照</el-button>
              </template>
            </el-table-column>
          </el-table>
        <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />

          <el-pagination
            v-model:current-page="historyPagination.page"
            v-model:page-size="historyPagination.pageSize"
            :total="historyPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            style="margin-top: 12px; justify-content: flex-end"
            @current-change="loadHistory"
            @size-change="handlePageSizeChange"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 快照详情 -->
    <el-dialog v-model="snapshotDialogVisible" title="执行快照" width="700px">
      <div v-loading="snapshotLoading">
        <el-input v-model="snapshotDetail" type="textarea" :rows="20" readonly placeholder="暂无快照数据" />
      </div>
      <template #footer>
        <el-button @click="snapshotDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { automation } from '@/api'

const historyLoading = ref(false)
const snapshotLoading = ref(false)
const historyList = ref([])
const snapshotDialogVisible = ref(false)
const snapshotDetail = ref('')

const historyPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

function getStatusType(status) {
  const map = { normal: 'success', warning: 'warning', critical: 'danger', triggered: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { normal: '正常', warning: '警告', critical: '严重', triggered: '触发' }
  return map[status] || status || '-'
}

async function handleViewSnapshot(row) {
  snapshotDialogVisible.value = true
  snapshotDetail.value = ''
  snapshotLoading.value = true
  try {
    const data = await automation.executions.getSnapshot(row.execution_id)
    snapshotDetail.value = JSON.stringify(data, null, 2)
  } catch (e) {
    snapshotDetail.value = `加载快照失败: ${e.message}`
    ElMessage.error(`加载快照失败: ${e.message}`)
  } finally {
    snapshotLoading.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await automation.rollbackHistory.getList({
      page: historyPagination.page,
      page_size: historyPagination.pageSize
    })
    if (!res || typeof res !== 'object') throw new Error('响应格式异常')
    historyList.value = res.items || []
    historyPagination.total = res.total || 0
  } catch (e) {
    ElMessage.error(`加载历史记录失败: ${e.message}`)
    historyList.value = []
  } finally {
    historyLoading.value = false
  }
}

function handlePageSizeChange(size) {
  historyPagination.pageSize = size
  historyPagination.page = 1
  loadHistory()
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
