<template>
  <div class="page-container">
    <el-card>
      <el-tabs type="border-card">
        <el-tab-pane label="指标评估">
          <el-form :model="form" label-placement="left" label-width="100" style="max-width: 600px; margin-top: 16px;">
            <el-form-item label="设备" required>
              <el-select v-model="form.device_id" placeholder="请选择设备" style="width: 100%" @change="loadMetrics">
                <el-option
                  v-for="d in deviceOptions"
                  :key="d.value"
                  :label="d.label"
                  :value="d.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="指标" required>
              <el-select v-model="form.metric_name" placeholder="请先选择设备" style="width: 100%" :disabled="!form.device_id">
                <el-option
                  v-for="m in metricOptions"
                  :key="m.value"
                  :label="m.label"
                  :value="m.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="阈值(可选)">
              <el-input v-model="form.threshold" placeholder="请输入阈值(可选)" />
            </el-form-item>
            <el-form-item>
              <el-space>
                <el-button type="primary" @click="handleEvaluate" :loading="evaluating">评估</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-space>
            </el-form-item>
          </el-form>

          <!-- 评估结果 -->
          <el-card v-if="evalResult" style="margin-top: 16px;">
            <template #header>评估结果</template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="设备ID">{{ evalResult.device_id || '-' }}</el-descriptions-item>
              <el-descriptions-item label="指标名称">{{ evalResult.metric_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="当前值">{{ evalResult.current_value ?? '-' }}</el-descriptions-item>
              <el-descriptions-item label="阈值">{{ evalResult.threshold ?? '-' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(evalResult.status)">{{ getStatusText(evalResult.status) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="执行ID">{{ evalResult.execution_id || '-' }}</el-descriptions-item>
            </el-descriptions>
            <el-divider />
            <el-input v-model="evalResultDetail" type="textarea" :rows="8" readonly placeholder="暂无详细结果" />
          </el-card>
        </el-tab-pane>

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
import request from '@/api/request'
import { devices } from '@/api/monitoring'
import { automation } from '@/api'

const loading = ref(false)
const evaluating = ref(false)
const historyLoading = ref(false)
const snapshotLoading = ref(false)
const deviceOptions = ref([])
const metricOptions = ref([])
const evalResult = ref(null)
const evalResultDetail = ref('')
const historyList = ref([])
const snapshotDialogVisible = ref(false)
const snapshotDetail = ref('')
const currentExecutionId = ref(null)

const form = reactive({ device_id: null, metric_name: null, threshold: '' })
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

async function loadDevices() {
  try {
    const res = await devices.getList({ page: 1, page_size: 100 })
    deviceOptions.value = (res.items || []).map(d => ({ label: `${d.name} (${d.ip_address})`, value: d.id }))
  } catch (e) {
    ElMessage.error(`加载设备失败: ${e.message}`)
    deviceOptions.value = []
  }
}

async function loadMetrics(deviceId) {
  if (!deviceId) {
    metricOptions.value = []
    return
  }
  try {
    const res = await devices.getById(deviceId)
    const metrics = res.metrics || []
    metricOptions.value = metrics.map(m => ({ label: m.name || m.metric_name, value: m.name || m.metric_name }))
  } catch (_) {
    // 使用默认指标
    metricOptions.value = [
      { label: 'CPU使用率', value: 'cpu_usage' },
      { label: '内存使用率', value: 'memory_usage' },
      { label: '磁盘使用率', value: 'disk_usage' },
      { label: '网络流量', value: 'network_traffic' }
    ]
  }
}

async function handleEvaluate() {
  if (!form.device_id) { ElMessage.warning('请选择设备'); return }
  if (!form.metric_name) { ElMessage.warning('请选择指标'); return }
  evaluating.value = true
  evalResult.value = null
  evalResultDetail.value = ''
  try {
    const payload = { device_id: form.device_id, metric_name: form.metric_name }
    if (form.threshold) payload.threshold = parseFloat(form.threshold)
    const data = await automation.evaluate(payload)
    evalResult.value = data
    evalResultDetail.value = JSON.stringify(data, null, 2)
    ElMessage.success('评估完成')
  } catch (e) {
    evalResultDetail.value = `评估失败: ${e.message}`
    ElMessage.error(`评估失败: ${e.message}`)
  } finally {
    evaluating.value = false
  }
}

async function handleViewSnapshot(row) {
  currentExecutionId.value = row.execution_id
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

function resetForm() {
  form.device_id = null
  form.metric_name = null
  form.threshold = ''
  evalResult.value = null
  evalResultDetail.value = ''
  metricOptions.value = []
}

onMounted(() => {
  loadDevices()
  loadHistory()
})
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
