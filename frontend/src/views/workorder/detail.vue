<template>
  <div class="detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-title">
          <h2>工单详情</h2>
          <span class="order-no">{{ workorderData.order_no }}</span>
        </div>
      </div>
      <div class="header-actions">
        <!-- 分配按钮 -->
        <el-button v-if="canAssign" type="primary" @click="showAssignDialog">
          <el-icon><User /></el-icon>
          分配
        </el-button>
        <!-- 审批按钮 -->
        <el-button v-if="canApprove" type="success" @click="showApproveDialog">
          <el-icon><Check /></el-icon>
          审批
        </el-button>
        <el-button v-if="canReject" type="danger" @click="showRejectDialog">
          <el-icon><Close /></el-icon>
          拒绝
        </el-button>
        <!-- 解决按钮 -->
        <el-button v-if="canResolve" type="warning" @click="showResolveDialog">
          <el-icon><CircleCheck /></el-icon>
          解决
        </el-button>
        <!-- 关闭按钮 -->
        <el-button v-if="canClose" @click="handleClose">
          <el-icon><Lock /></el-icon>
          关闭
        </el-button>
      </div>
    </div>

    <div v-loading="loading">
      <!-- 基本信息卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="statusType(workorderData.status)" size="small">
              {{ statusText(workorderData.status) }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border direction="vertical" size="default">
          <el-descriptions-item label="工单标题" :span="2">
            {{ workorderData.title || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tooltip :content="priorityDescriptions[workorderData.priority]" placement="top">
              <el-tag :type="priorityType(workorderData.priority)" size="small">
                {{ priorityText(workorderData.priority) }}
              </el-tag>
            </el-tooltip>
          </el-descriptions-item>
          <el-descriptions-item label="工单类型">
            {{ workorderData.type || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ workorderData.creator || workorderData.created_by || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="处理人">
            <span v-if="workorderData.assignee" class="assignee-name">
              {{ workorderData.assignee }}
            </span>
            <span v-else class="no-assignee">待分配</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联设备">
            {{ workorderData.device || workorderData.device_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ workorderData.created_at ? formatTime(workorderData.created_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ workorderData.updated_at ? formatTime(workorderData.updated_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="解决时间" v-if="workorderData.resolved_at">
            {{ formatTime(workorderData.resolved_at) }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="description-section" v-if="workorderData.description">
          <div class="section-label">工单描述</div>
          <div class="description-content">{{ workorderData.description }}</div>
        </div>
        <div class="handling-notes" v-if="workorderData.handling_notes">
          <div class="section-label">处理备注</div>
          <div class="notes-content">{{ workorderData.handling_notes }}</div>
        </div>
      </el-card>

      <!-- SLA 状态 -->
      <el-card class="sla-card" shadow="never" v-if="slaData">
        <template #header>
          <div class="card-header">
            <span>SLA 状态</span>
            <el-tag :type="slaStatusType" size="small">{{ slaStatusText }}</el-tag>
          </div>
        </template>
        <div class="sla-content">
          <div class="sla-timer">
            <div class="timer-value" :class="{ 'timer-warning': slaData.warning, 'timer-critical': slaData.critical }">
              {{ slaTimeDisplay }}
            </div>
            <div class="timer-label">{{ slaLabel }}</div>
          </div>
          <div class="sla-info">
            <div class="sla-item">
              <span class="sla-item-label">响应时限</span>
              <span class="sla-item-value">{{ slaData.response_deadline ? formatTime(slaData.response_deadline) : '-' }}</span>
            </div>
            <div class="sla-item">
              <span class="sla-item-label">解决时限</span>
              <span class="sla-item-value">{{ slaData.resolve_deadline ? formatTime(slaData.resolve_deadline) : '-' }}</span>
            </div>
            <div class="sla-item">
              <span class="sla-item-label">已用时间</span>
              <span class="sla-item-value">{{ slaData.elapsed_formatted || '-' }}</span>
            </div>
            <div class="sla-item">
              <span class="sla-item-label">剩余时间</span>
              <span class="sla-item-value">{{ slaData.remaining_formatted || '-' }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 审批流程图 -->
      <el-card class="flow-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>审批流程</span>
            <el-button text size="small" @click="loadApprovalFlow" :loading="flowLoading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-if="flowLoading" class="flow-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载审批流程...
        </div>

        <div v-else-if="approvalFlow && approvalFlow.nodes && approvalFlow.nodes.length > 0" class="flow-visualization">
          <div class="flow-timeline-horizontal">
            <div
              v-for="(node, idx) in approvalFlow.nodes"
              :key="node.node_id"
              class="flow-node-h"
              :class="[
                `flow-node-h--${node.type}`,
                node.is_current ? 'flow-node-h--current' : '',
                idx === 0 ? 'flow-node-h--first' : '',
                idx === approvalFlow.nodes.length - 1 ? 'flow-node-h--last' : ''
              ]"
            >
              <div class="flow-node-h-connector" v-if="idx < approvalFlow.nodes.length - 1" />
              <div class="flow-node-h-icon">
                {{ node.action_icon || getNodeIcon(node.type) }}
              </div>
              <div class="flow-node-h-content">
                <div class="flow-node-h-title">{{ node.title }}</div>
                <div class="flow-node-h-meta">
                  <span v-if="node.operator">👤 {{ node.operator }}</span>
                </div>
                <div class="flow-node-h-time" v-if="node.created_at">
                  🕐 {{ formatFlowTime(node.created_at) }}
                </div>
                <div class="flow-node-h-status" v-if="node.is_current || node.status_label">
                  <el-tag v-if="node.is_current" type="warning" size="small">当前</el-tag>
                  <el-tag v-if="node.status_label" :type="flowNodeStatusType(node.status)" size="small">
                    {{ node.status_label }}
                  </el-tag>
                </div>
                <div class="flow-node-h-comment" v-if="node.comment">
                  💬 {{ node.comment }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="flow-empty">
          <el-empty description="暂无审批流程记录" :image-size="60" />
        </div>

        <!-- 添加流程节点 -->
        <div class="flow-actions" v-if="canAddFlow">
          <el-input v-model.trim="flowComment" placeholder="添加处理备注" style="width: 300px" />
          <el-button type="primary" size="small" @click="addFlowNode">添加流程记录</el-button>
        </div>
      </el-card>

      <!-- 工单操作历史 -->
      <el-card class="history-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>操作历史</span>
          </div>
        </template>
        <el-table :data="workorderFlows" size="small" :pagination="false">
          <el-table-column label="时间" prop="created_at" width="170">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作人" prop="operator" width="120" />
          <el-table-column label="动作" prop="action" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="flowActionTag(row.action)">
                {{ flowActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="备注" prop="comment" show-overflow-tooltip />
        </el-table>
      </el-card>
    </div>

    <!-- 分配弹窗 -->
    <el-dialog v-model="assignDialogVisible" title="分配工单" width="480px" destroy-on-close>
      <el-form label-position="left" label-width="80px">
        <el-form-item label="工单号">
          <span class="form-value">{{ workorderData.order_no }}</span>
        </el-form-item>
        <el-form-item label="处理人" required>
          <el-input v-model.trim="assignForm.assignee" placeholder="请输入处理人姓名" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="assignForm.comment" type="textarea" :rows="3" placeholder="请输入分配备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="assignDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAssign" :loading="actionLoading">确认分配</el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 审批弹窗 -->
    <el-dialog v-model="approveDialogVisible" title="审批工单" width="480px" destroy-on-close>
      <el-form label-position="left" label-width="80px">
        <el-form-item label="审批结果">
          <el-radio-group v-model="approveForm.approved">
            <el-radio :label="true">批准</el-radio>
            <el-radio :label="false">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input v-model.trim="approveForm.comment" type="textarea" :rows="4" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="approveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApprove" :loading="actionLoading">提交审批</el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 解决弹窗 -->
    <el-dialog v-model="resolveDialogVisible" title="解决工单" width="480px" destroy-on-close>
      <el-form label-position="left" label-width="80px">
        <el-form-item label="解决方案">
          <el-input v-model.trim="resolveForm.solution" type="textarea" :rows="4" placeholder="请描述解决方案" />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model.trim="resolveForm.handling_notes" type="textarea" :rows="3" placeholder="请输入处理备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="resolveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitResolve" :loading="actionLoading">确认解决</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, User, Check, Close, CircleCheck, Lock, Refresh, Loading
} from '@element-plus/icons-vue'
import { workorder } from '@/api'

const route = useRoute()
const loading = ref(false)
const flowLoading = ref(false)
const actionLoading = ref(false)

const workorderData = ref({})
const slaData = ref(null)
const approvalFlow = ref(null)
const workorderFlows = ref([])
const flowComment = ref('')

let slaTimer = null

// ── 状态映射 ──────────────────────────────────────────────
const statusLabels = {
  pending: '待处理', processing: '处理中', pending_approval: '待审批',
  approved: '已批准', rejected: '已拒绝', resolved: '已解决', closed: '已关闭', cancelled: '已取消'
}

const priorityDescriptions = {
  P1: 'P1-紧急：系统宕机或核心功能不可用，需立即处理',
  P2: 'P2-高：业务功能严重受损，需尽快处理',
  P3: 'P3-中：功能部分受损，但有替代方案',
  P4: 'P4-低：轻微问题或优化建议'
}

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

const statusType = (s) => ({
  pending: 'warning', processing: 'info', pending_approval: 'warning',
  approved: 'success', rejected: 'danger', resolved: 'success', closed: 'info', cancelled: 'info'
})[s] || 'info'

const statusText = (s) => statusLabels[s] || s
const priorityType = (p) => ({ P1: 'danger', P2: 'warning', P3: 'info', P4: 'info' })[p] || 'info'
const priorityText = (p) => ({ P1: 'P1-紧急', P2: 'P2-高', P3: 'P3-中', P4: 'P4-低' })[p] || p

// ── 操作权限 ──────────────────────────────────────────────
const currentStatus = computed(() => workorderData.value?.status)

const canAssign = computed(() => currentStatus.value === 'pending')
const canApprove = computed(() => currentStatus.value === 'pending_approval')
const canReject = computed(() => currentStatus.value === 'pending_approval')
const canResolve = computed(() => currentStatus.value === 'approved')
const canClose = computed(() => ['resolved', 'approved'].includes(currentStatus.value))
const canAddFlow = computed(() => !['closed', 'cancelled', 'resolved'].includes(currentStatus.value))

// ── SLA 计算 ──────────────────────────────────────────────
const slaStatusType = computed(() => {
  if (!slaData.value) return 'info'
  if (slaData.value.breached) return 'danger'
  if (slaData.value.warning) return 'warning'
  return 'success'
})

const slaStatusText = computed(() => {
  if (!slaData.value) return '-'
  if (slaData.value.breached) return '已超时'
  if (slaData.value.warning) return '即将超时'
  return '正常'
})

const slaLabel = computed(() => {
  if (!slaData.value) return ''
  return slaData.value.phase === 'response' ? '响应剩余时间' : '解决剩余时间'
})

const slaTimeDisplay = computed(() => {
  if (!slaData.value) return '--:--:--'
  return slaData.value.remaining_formatted || slaData.value.elapsed_formatted || '--:--:--'
})

// ── 流程节点 ──────────────────────────────────────────────
const flowNodeStatusType = (status) => ({
  pending: 'info', processing: 'info', pending_approval: 'warning',
  approved: 'success', rejected: 'danger', resolved: 'success', closed: 'info', cancelled: 'info'
})[status] || 'info'

const flowActionText = (action) => ({
  create: '创建', assign: '分配', submit: '提交', approve: '批准',
  reject: '拒绝', resolve: '解决', close: '关闭', cancel: '取消', end: '结束'
})[action] || action

const flowActionTag = (action) => ({
  create: 'primary', assign: 'info', submit: 'warning', approve: 'success',
  reject: 'danger', resolve: 'success', close: 'info', cancel: 'warning', end: 'success'
})[action] || 'info'

const getNodeIcon = (type) => ({
  start: '▶', approval: '☑', process: '⚙', end: '■',
  end_resolved: '✓', end_cancelled: '✗', end_rejected: '✗',
  approval_done: '☑', approval_rejected: '✗'
})[type] || '●'

// ── 格式化 ────────────────────────────────────────────────
function formatTime(ts) {
  if (!ts) return '-'
  try {
    const d = new Date(ts)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
  } catch { return ts }
}

function formatFlowTime(ts) {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch { return ts }
}

// ── 加载数据 ──────────────────────────────────────────────
const workorderId = computed(() => route.params.id || route.query.id)

async function loadWorkorderDetail() {
  loading.value = true
  try {
    const data = await workorder.getById(workorderId.value)
    workorderData.value = data

    // 加载 SLA
    loadSla()

    // 加载操作历史
    loadWorkorderFlows()
  } catch (e) {
    ElMessage.error(`加载工单详情失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

async function loadSla() {
  try {
    slaData.value = await workorder.getSla(workorderId.value)
    startSlaTimer()
  } catch (e) {
    slaData.value = null
  }
}

async function loadApprovalFlow() {
  flowLoading.value = true
  try {
    approvalFlow.value = await workorder.getApprovalFlow(workorderId.value)
  } catch (e) {
    approvalFlow.value = null
  } finally {
    flowLoading.value = false
  }
}

async function loadWorkorderFlows() {
  try {
    const flows = await workorder.getFlows(workorderId.value)
    workorderFlows.value = flows.items || flows || []
  } catch (e) {
    workorderFlows.value = []
  }
}

function startSlaTimer() {
  stopSlaTimer()
  slaTimer = setInterval(() => {
    if (slaData.value) {
      loadSla()
    }
  }, 30000)
}

function stopSlaTimer() {
  if (slaTimer) { clearInterval(slaTimer); slaTimer = null }
}

// ── 操作 ──────────────────────────────────────────────────
const assignDialogVisible = ref(false)
const assignForm = reactive({ assignee: '', comment: '' })

function showAssignDialog() {
  assignForm.assignee = ''
  assignForm.comment = ''
  assignDialogVisible.value = true
}

async function submitAssign() {
  if (!assignForm.assignee) { ElMessage.warning('请输入处理人'); return }
  actionLoading.value = true
  try {
    await workorder.assign(workorderId.value, assignForm)
    ElMessage.success('工单已分配')
    assignDialogVisible.value = false
    loadWorkorderDetail()
  } catch (e) {
    ElMessage.error(`分配失败: ${e.message}`)
  } finally {
    actionLoading.value = false
  }
}

const approveDialogVisible = ref(false)
const approveForm = reactive({ approved: true, comment: '' })

function showApproveDialog() {
  approveForm.approved = true
  approveForm.comment = ''
  approveDialogVisible.value = true
}

async function submitApprove() {
  actionLoading.value = true
  try {
    await workorder.approve(workorderId.value, approveForm)
    ElMessage.success('审批已提交')
    approveDialogVisible.value = false
    loadWorkorderDetail()
  } catch (e) {
    ElMessage.error(`审批失败: ${e.message}`)
  } finally {
    actionLoading.value = false
  }
}

function showRejectDialog() {
  approveForm.approved = false
  approveForm.comment = ''
  approveDialogVisible.value = true
}

const resolveDialogVisible = ref(false)
const resolveForm = reactive({ solution: '', handling_notes: '' })

function showResolveDialog() {
  resolveForm.solution = ''
  resolveForm.handling_notes = ''
  resolveDialogVisible.value = true
}

async function submitResolve() {
  if (!resolveForm.solution) { ElMessage.warning('请输入解决方案'); return }
  actionLoading.value = true
  try {
    await workorder.resolve(workorderId.value, resolveForm)
    ElMessage.success('工单已解决')
    resolveDialogVisible.value = false
    loadWorkorderDetail()
  } catch (e) {
    ElMessage.error(`解决失败: ${e.message}`)
  } finally {
    actionLoading.value = false
  }
}

async function handleClose() {
  try {
    await workorder.close(workorderId.value, {})
    ElMessage.success('工单已关闭')
    loadWorkorderDetail()
  } catch (e) {
    ElMessage.error(`关闭失败: ${e.message}`)
  }
}

async function addFlowNode() {
  if (!flowComment.value.trim()) { ElMessage.warning('请输入处理备注'); return }
  try {
    await workorder.addFlow(workorderId.value, { comment: flowComment.value })
    ElMessage.success('流程记录已添加')
    flowComment.value = ''
    loadWorkorderFlows()
    loadApprovalFlow()
  } catch (e) {
    ElMessage.error(`添加失败: ${e.message}`)
  }
}

onMounted(() => {
  loadWorkorderDetail()
  loadApprovalFlow()
})

onUnmounted(() => { stopSlaTimer() })
</script>

<style scoped>
.detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.order-no {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
  margin-left: 8px;
}
.header-actions {
  display: flex;
  gap: 8px;
}

.info-card,
.sla-card,
.flow-card,
.history-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.description-section,
.handling-notes {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
}
.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.description-content,
.notes-content {
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.6;
  white-space: pre-wrap;
}

.assignee-name {
  color: var(--el-color-primary);
}
.no-assignee {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

/* SLA */
.sla-content {
  display: flex;
  align-items: center;
  gap: 32px;
}
.sla-timer {
  text-align: center;
}
.timer-value {
  font-size: 32px;
  font-weight: 700;
  font-family: monospace;
  color: var(--el-color-success);
  line-height: 1;
}
.timer-value.timer-warning {
  color: var(--el-color-warning);
}
.timer-value.timer-critical {
  color: var(--el-color-danger);
}
.timer-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
.sla-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.sla-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sla-item-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.sla-item-value {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

/* 流程图 */
.flow-loading {
  text-align: center;
  padding: 24px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
.flow-empty {
  padding: 24px;
}

.flow-visualization {
  overflow-x: auto;
  padding: 16px 0;
}
.flow-timeline-horizontal {
  display: flex;
  align-items: flex-start;
  gap: 0;
  min-width: min-content;
}

.flow-node-h {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 140px;
  position: relative;
  padding: 0 8px;
}
.flow-node-h-connector {
  position: absolute;
  top: 20px;
  left: calc(50% + 20px);
  width: calc(100% - 40px);
  height: 3px;
  background: var(--el-border-color);
  z-index: 0;
}
.flow-node-h-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: var(--el-fill-color-dark);
  color: var(--el-text-color-secondary);
  border: 2px solid var(--el-border-color);
  z-index: 1;
  position: relative;
}
.flow-node-h--first .flow-node-h-icon {
  background: var(--el-color-primary);
  color: #fff;
  border-color: var(--el-color-primary);
}
.flow-node-h--current .flow-node-h-icon {
  background: var(--el-color-warning);
  color: #fff;
  border-color: var(--el-color-warning);
}
.flow-node-h--end .flow-node-h-icon,
.flow-node-h--end_resolved .flow-node-h-icon {
  background: var(--el-color-success);
  color: #fff;
  border-color: var(--el-color-success);
}
.flow-node-h--end_cancelled .flow-node-h-icon,
.flow-node-h--end_rejected .flow-node-h-icon {
  background: var(--el-color-danger);
  color: #fff;
  border-color: var(--el-color-danger);
}
.flow-node-h--approval_done .flow-node-h-icon {
  background: var(--el-color-success);
  color: #fff;
  border-color: var(--el-color-success);
}
.flow-node-h--approval_rejected .flow-node-h-icon {
  background: var(--el-color-danger);
  color: #fff;
  border-color: var(--el-color-danger);
}
.flow-node-h--approval .flow-node-h-icon {
  background: var(--el-color-primary);
  color: #fff;
  border-color: var(--el-color-primary);
}
.flow-node-h-content {
  margin-top: 8px;
  text-align: center;
  min-width: 120px;
}
.flow-node-h-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.flow-node-h-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
.flow-node-h-time {
  font-size: 11px;
  color: var(--el-text-color-tertiary);
  margin-top: 2px;
}
.flow-node-h-status {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-top: 4px;
}
.flow-node-h-comment {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flow-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-value {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* 暗色主题适配 */
:deep(.el-card) {
  background: var(--el-bg-color);
  border-color: var(--el-border-color);
}
:deep(.el-descriptions__label) {
  background: var(--el-fill-color-light) !important;
}
</style>
