<template>
  <div>
    <div class="page-header">
      <div>
        <h2>工单列表</h2>
        <p class="page-subtitle">查看和管理所有工单</p>
      </div>
      <el-button type="primary" @click="$router.push('/workorder/create')">
        <el-icon><Plus /></el-icon>
        创建工单
      </el-button>
    </div>

    <!-- Stats Summary -->
    <div v-if="workorderStats" class="stats-row">
      <div class="stat-badge" @click="filterStatus = 'pending'">
        <span class="stat-num">{{ workorderStats.pending || 0 }}</span>
        <span class="stat-label">待处理</span>
      </div>
      <div class="stat-badge" @click="filterStatus = 'processing'">
        <span class="stat-num">{{ workorderStats.processing || 0 }}</span>
        <span class="stat-label">处理中</span>
      </div>
      <div class="stat-badge" @click="filterStatus = 'resolved'">
        <span class="stat-num">{{ workorderStats.resolved || 0 }}</span>
        <span class="stat-label">已解决</span>
      </div>
      <div class="stat-badge" @click="filterStatus = 'closed'">
        <span class="stat-num">{{ workorderStats.closed || 0 }}</span>
        <span class="stat-label">已关闭</span>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <el-card shadow="never" style="margin-bottom:12px">
      <el-space :wrap="true" :size="12" align="center">
        <el-input v-model.trim="searchKeyword" placeholder="搜索工单标题" clearable style="width:200px" @keyup.enter="loadData" />
        <el-select v-model="filterStatus" placeholder="工单状态" clearable :options="statusOptions" style="width:140px" @change="loadData" />
        <el-select v-model="filterPriority" placeholder="优先级" clearable :options="priorityOptions" style="width:140px" @change="loadData" />
        <el-select v-model="filterDevice" placeholder="关联设备" clearable :options="deviceList" filterable style="width:180px" @change="loadData" />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-space>
    </el-card>

    <!-- 工单列表 -->
    <el-card shadow="never">
      <template #header>
        <span>工单列表 <span class="table-count">共 {{ pagination.total }} 条</span></span>
      </template>
      <el-table
        :data="workorderList"
        v-loading="loading"
        :pagination="pagination"
        row-key="id"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      >
        <el-table-column label="工单号" prop="order_no" width="180" />
        <el-table-column label="工单标题" prop="title" show-overflow-tooltip />
        <el-table-column label="优先级" width="120">
          <template #default="{ row }">
            <el-tooltip :content="priorityDescriptions[row.priority] || row.priority" placement="top" :disabled="!row.priority">
              <el-tag :type="priorityType(row.priority)" size="small">{{ priorityText(row.priority) }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="220">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建人" prop="creator" width="120" />
        <el-table-column label="处理人" prop="assignee" width="120">
          <template #default="{ row }">{{ row.assignee || '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" prop="created_at" width="170">
          <template #default="{ row }">{{ row.created_at ? row.created_at.replace('T', ' ').slice(0, 16) : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="8">
              <el-button size="small" type="primary" link @click="handleView(row)">查看</el-button>
              <el-button size="small" type="info" link @click="handleEdit(row)">编辑</el-button>
              <el-button v-if="row.status !== 'closed'" size="small" type="warning" link @click="handleClose(row)">关闭</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-empty v-if="!loading && workorderList.length === 0" description="暂无数据" />

    <!-- 查看工单详情弹窗 -->
    <el-dialog v-model="viewModalVisible" title="工单详情" width="600px" destroy-on-close>
      <el-descriptions v-if="viewData" :column="1" border direction="vertical" size="large">
        <el-descriptions-item label="工单号">{{ viewData.order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工单标题">{{ viewData.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ viewData.type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tooltip :content="priorityDescriptions[viewData.priority] || viewData.priority" placement="top">
            <el-tag :type="priorityType(viewData.priority)" size="small">{{ priorityText(viewData.priority) }}</el-tag>
          </el-tooltip>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)" size="small">{{ statusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述">{{ viewData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备">{{ viewData.device || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ viewData.created_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ viewData.assignee || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at ? viewData.created_at.slice(0, 16) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ viewData.updated_at ? viewData.updated_at.slice(0, 16) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理备注">{{ viewData.handling_notes || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 审批流程可视化 -->
      <div v-if="approvalFlow" class="approval-flow-section">
        <div class="flow-section-title">审批流程</div>
        <div class="flow-timeline">
          <div
            v-for="(node, idx) in approvalFlow.nodes"
            :key="node.node_id"
            class="flow-node"
            :class="[
              `flow-node--${node.type}`,
              node.is_current ? 'flow-node--current' : '',
              idx === 0 ? 'flow-node--first' : '',
              idx === approvalFlow.nodes.length - 1 ? 'flow-node--last' : '',
            ]"
          >
            <div class="flow-node-connector" v-if="idx < approvalFlow.nodes.length - 1" />
            <div class="flow-node-icon">{{ node.action_icon }}</div>
            <div class="flow-node-content">
              <div class="flow-node-header">
                <span class="flow-node-title">{{ node.title }}</span>
                <el-tag v-if="node.is_current" type="warning" size="small">当前</el-tag>
                <el-tag v-if="node.status_label" :type="flowNodeStatusType(node.status)" size="small">{{ node.status_label }}</el-tag>
              </div>
              <div class="flow-node-meta">
                <span v-if="node.operator">👤 {{ node.operator }}</span>
                <span v-if="node.created_at">🕐 {{ formatFlowTime(node.created_at) }}</span>
                <span v-if="node.action && node.action !== 'end' && node.action !== 'create'">➡️ {{ flowActionText(node.action) }}</span>
              </div>
              <div v-if="node.comment" class="flow-node-comment">💬 {{ node.comment }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="approvalFlowLoading" class="approval-flow-loading">
        <el-icon class="is-loading"><Loading /></el-icon> 加载审批流程...
      </div>
      <div v-else class="approval-flow-empty">
        <el-button text @click="loadApprovalFlow(viewData.id)">查看审批流程 →</el-button>
      </div>

      <template #footer>
        <el-button @click="viewModalVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 编辑工单弹窗 -->
    <el-dialog v-model="editModalVisible" title="编辑工单" width="520px" destroy-on-close>
      <el-alert v-if="statusTransitionHint" type="info" :show-icon="false" style="margin-bottom:16px">
        {{ statusTransitionHint }}
      </el-alert>
      <el-form label-position="top" label-width="80">
        <el-form-item label="工单号">
          <span class="form-value">{{ editForm.order_no }}</span>
        </el-form-item>
        <el-form-item label="当前状态">
          <el-tag :type="statusType(editForm.status)" size="small">{{ statusText(editForm.status) }}</el-tag>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="editForm.status" :options="statusTransitionOptions" placeholder="请选择新状态" style="width:100%" />
        </el-form-item>
        <el-form-item label="处理人">
          <el-input v-model.trim="editForm.assignee" placeholder="请输入处理人" />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model.trim="editForm.handling_notes" type="textarea" :rows="4" placeholder="请输入处理备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="editModalVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editSubmitting">保存</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, QuestionFilled, Loading } from '@element-plus/icons-vue'
import { workorder as workorderApi, devices as devicesApi } from '@/api'
import { CONFIG } from '@/config/constants'

const loading = ref(false)
const editSubmitting = ref(false)
const searchKeyword = ref('')
const filterStatus = ref(null)
const filterPriority = ref(null)
const filterDevice = ref(null)
const deviceList = ref([])
const workorderList = ref([])

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100],
  layout: 'sizes, prev, pager, next',
  onCurrentChange: (page) => { pagination.currentPage = page; loadData(); },
  onSizeChange: (size) => { pagination.pageSize = size; pagination.currentPage = 1; loadData(); }
})

const viewModalVisible = ref(false)
const viewData = ref({})
const approvalFlow = ref(null)
const approvalFlowLoading = ref(false)

const editModalVisible = ref(false)
const editForm = reactive({ id: null, order_no: '', status: '', assignee: '', handling_notes: '' })
const statusTransitionOptions = ref([])

const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '待审批', value: 'pending_approval' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' },
  { label: '已取消', value: 'cancelled' }
]

const priorityOptions = [
  { label: 'P1 - 紧急', value: 'P1' },
  { label: 'P2 - 高', value: 'P2' },
  { label: 'P3 - 中', value: 'P3' },
  { label: 'P4 - 低', value: 'P4' }
]

const priorityDescriptions = {
  P1: 'P1-紧急：系统宕机或核心功能不可用，需立即处理',
  P2: 'P2-高：业务功能严重受损，需尽快处理',
  P3: 'P3-中：功能部分受损，但有替代方案',
  P4: 'P4-低：轻微问题或优化建议'
}

const statusFlow = ['pending', 'processing', 'pending_approval', 'approved', 'rejected', 'resolved', 'closed', 'cancelled']
const statusLabels = { pending: '待处理', processing: '处理中', pending_approval: '待审批', approved: '已批准', rejected: '已拒绝', resolved: '已解决', closed: '已关闭', cancelled: '已取消' }
const statusTransitionMap = {
  pending: ['processing'],
  processing: ['pending_approval'],
  pending_approval: ['approved', 'rejected'],
  approved: ['resolved'],
  rejected: ['closed'],
  resolved: ['closed'],
  closed: [],
  cancelled: []
}

const workorderStats = ref({ pending: 0, processing: 0, resolved: 0, closed: 0 })

async function loadStats() {
  try {
    const res = await workorderApi.getStats()
    workorderStats.value = {
      pending: res.pending || 0,
      processing: res.processing || 0,
      resolved: res.resolved || 0,
      closed: res.closed || 0
    }
  } catch (e) {
    // load order stats failed silently
  }
}

const statusTransitionHint = computed(() => {
  if (!editForm.status) return ''
  const nextStatuses = statusTransitionMap[editForm.status]
  if (!nextStatuses || nextStatuses.length === 0) return '当前状态无法流转'
  const nextSteps = nextStatuses.map(s => statusLabels[s]).join(' / ')
  return `可流转至：${nextSteps}`
})

const priorityType = (p) => ({ P1: 'danger', P2: 'warning', P3: 'info', P4: 'info' })[p] || 'info'
const priorityText = (p) => ({ P1: 'P1-紧急', P2: 'P2-高', P3: 'P3-中', P4: 'P4-低' })[p] || p
const statusType = (s) => ({ pending: 'warning', processing: 'info', pending_approval: 'warning', approved: 'success', rejected: 'danger', resolved: 'success', closed: 'info', cancelled: 'info' })[s] || 'info'
const statusText = (s) => ({ pending: '待处理', processing: '处理中', pending_approval: '待审批', approved: '已批准', rejected: '已拒绝', resolved: '已解决', closed: '已关闭', cancelled: '已取消' })[s] || s

const getStatusTransitionOptions = (currentStatus) => {
  const flow = ['pending', 'processing', 'pending_approval', 'approved', 'rejected', 'resolved', 'closed', 'cancelled']
  const currentIndex = flow.indexOf(currentStatus)
  if (currentIndex === -1 || currentIndex === flow.length - 1) return []
  return flow.slice(currentIndex + 1).map(s => ({ label: statusText(s), value: s }))
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.currentPage, page_size: pagination.pageSize }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPriority.value) params.priority = filterPriority.value
    if (filterDevice.value) params.device_id = filterDevice.value

    const res = await workorderApi.getList(params)
    workorderList.value = res.items || res.data?.items || []
    pagination.total = res.total || res.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载工单列表失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

async function loadDevices() {
  try {
    const res = await devicesApi.getList({ page: 1, page_size: 500 })
    deviceList.value = (res.items || res.data?.items || []).map(d => ({ label: d.name || d.device_name || `设备-${d.id}`, value: d.id }))
  } catch (e) {
    // load device list failed silently
  }
}

function handlePageChange(p) { pagination.currentPage = p; loadData() }
function handlePageSizeChange(ps) { pagination.pageSize = ps; pagination.currentPage = 1; loadData() }

function resetFilters() {
  searchKeyword.value = ''
  filterStatus.value = null
  filterPriority.value = null
  filterDevice.value = null
  pagination.currentPage = 1
  loadData()
}

async function handleView(row) {
  approvalFlow.value = null
  try {
    const data = await workorderApi.getById(row.id)
    viewData.value = data
    viewModalVisible.value = true
    // 自动加载审批流程
    loadApprovalFlow(row.id)
  } catch (e) {
    ElMessage.error(`获取工单详情失败: ${e.message}`)
  }
}

async function loadApprovalFlow(workorderId) {
  approvalFlowLoading.value = true
  try {
    const data = await workorderApi.getApprovalFlow(workorderId)
    approvalFlow.value = data
  } catch (e) {
    approvalFlow.value = null
  } finally {
    approvalFlowLoading.value = false
  }
}

function flowNodeStatusType(status) {
  const map = {
    pending: 'info', processing: 'info', pending_approval: 'warning',
    approved: 'success', rejected: 'danger', resolved: 'success',
    closed: 'info', cancelled: 'info'
  }
  return map[status] || 'info'
}

function flowActionText(action) {
  const map = {
    create: '创建', assign: '分配', submit: '提交', approve: '批准',
    reject: '拒绝', resolve: '解决', close: '关闭', cancel: '取消', end: '结束'
  }
  return map[action] || action
}

function formatFlowTime(ts) {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  } catch { return ts }
}

function handleEdit(row) {
  editForm.id = row.id
  editForm.order_no = row.order_no || ''
  editForm.status = row.status
  editForm.assignee = row.assignee || ''
  editForm.handling_notes = row.handling_notes || ''
  statusTransitionOptions.value = getStatusTransitionOptions(row.status)
  editModalVisible.value = true
}

async function submitEdit() {
  if (!editForm.id) return
  if (!editForm.status) { ElMessage.warning('请选择新状态'); return }
  editSubmitting.value = true
  try {
    await workorderApi.update(editForm.id, {
      status: editForm.status,
      assignee: editForm.assignee
    })
    ElMessage.success('工单更新成功')
    editModalVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(`更新工单失败: ${e.message}`)
  } finally {
    editSubmitting.value = false
  }
}

async function handleClose(row) {
  try {
    await workorderApi.update(row.id, { status: 'closed' })
    ElMessage.success('工单已关闭')
    loadData()
  } catch (e) {
    ElMessage.error(`关闭工单失败: ${e.message}`)
  }
}

let pollTimer = null

function startPoll() {
  stopPoll()
  pollTimer = setInterval(() => { loadData() }, CONFIG.POLL_INTERVAL_SHORT)
}

function stopPoll() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onMounted(() => { loadData(); loadStats(); loadDevices(); startPoll() })
onUnmounted(() => { stopPoll() })
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.page-header h2 { margin: 0; font-size: 18px; font-weight: 600; }
.page-subtitle { margin: 4px 0 0 0; font-size: 13px; color: #909399; }

.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.stat-badge:hover {
  background: #e8f4ff;
  border-color: #adc6ff;
}
.stat-num {
  font-size: 18px;
  font-weight: 700;
  color: #165dff;
}
.stat-label {
  font-size: 13px;
  color: #606266;
}

.table-count {
  font-size: 13px;
  color: #909399;
  font-weight: normal;
  margin-left: 8px;
}

.form-value {
  color: #606266;
  font-size: 14px;
}

/* 审批流程可视化 */
.approval-flow-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.flow-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}
.flow-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.flow-node {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  position: relative;
  padding-bottom: 12px;
}
.flow-node--first .flow-node-icon {
  background: #165dff;
  color: #fff;
}
.flow-node--current .flow-node-icon {
  background: #fa8c16;
  color: #fff;
}
.flow-node--end .flow-node-icon,
.flow-node--end_resolved .flow-node-icon,
.flow-node--end_cancelled .flow-node-icon,
.flow-node--end_rejected .flow-node-icon {
  background: #52c41a;
  color: #fff;
}
.flow-node--approval_done .flow-node-icon { background: #52c41a; color: #fff; }
.flow-node--approval_rejected .flow-node-icon { background: #ff4d4f; color: #fff; }
.flow-node--approval .flow-node-icon { background: #1890ff; color: #fff; }
.flow-node--process .flow-node-icon { background: #8c8c8c; color: #fff; }
.flow-node--complete .flow-node-icon { background: #52c41a; color: #fff; }
.flow-node--last {
  padding-bottom: 0;
}
.flow-node-connector {
  position: absolute;
  left: 15px;
  top: 28px;
  width: 2px;
  height: calc(100% - 20px);
  background: #e8e8e8;
}
.flow-node-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  z-index: 1;
}
.flow-node-content {
  flex: 1;
  min-width: 0;
}
.flow-node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.flow-node-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}
.flow-node-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  flex-wrap: wrap;
}
.flow-node-comment {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
  background: #f7f8fa;
  padding: 4px 8px;
  border-radius: 4px;
}
.approval-flow-loading {
  text-align: center;
  padding: 12px;
  color: #909399;
  font-size: 13px;
}
.approval-flow-empty {
  text-align: center;
  padding: 8px;
}
</style>
