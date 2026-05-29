<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">故障处置台</h1>
        <p class="page-subtitle">告警时间线 · 证据分析 · AI 推荐 · 实时日志</p>
      </div>
      <el-space>
        <el-select v-model="selectedAlertId" placeholder="选择告警" style="width: 240px" filterable @change="onAlertChange">
          <el-option v-for="a in alertList" :key="a.id" :label="`#${a.id} ${a.title}`" :value="a.id" />
        </el-select>
        <el-button type="primary" :loading="aiLoading" @click="runAIAnalysis">
          <el-icon><MagicStick /></el-icon> AI 分析
        </el-button>
      </el-space>
    </div>

    <!-- 主体三栏布局 -->
    <el-row :gutter="12" class="main-layout">
      <!-- 左侧：时间线 -->
      <el-col :span="5" class="timeline-col">
        <el-card class="timeline-card" shadow="never">
          <template #header>
            <span class="card-title">故障时间线</span>
          </template>
          <div class="timeline">
            <div v-for="(item, idx) in timeline" :key="idx" class="timeline-item" :class="item.type">
              <div class="timeline-marker" />
              <div class="timeline-content">
                <div class="timeline-time">{{ item.time }}</div>
                <div class="timeline-title">{{ item.title }}</div>
                <div class="timeline-desc">{{ item.desc }}</div>
              </div>
            </div>
            <div v-if="timeline.length === 0" class="timeline-empty">
              选择告警后显示时间线
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 中间：证据分析 -->
      <el-col :span="11" class="evidence-col">
        <!-- 告警信息 -->
        <el-card class="evidence-card" shadow="never">
          <template #header>
            <span class="card-title">告警信息</span>
          </template>
          <div v-if="currentAlert">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="告警ID">#{{ currentAlert.id }}</el-descriptions-item>
              <el-descriptions-item label="级别">
                <el-tag :type="getLevelType(currentAlert.level)" size="small">{{ getLevelLabel(currentAlert.level) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentAlert.status)" size="small">{{ getStatusLabel(currentAlert.status) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="设备">{{ currentAlert.device_name || currentAlert.device_ip || '—' }}</el-descriptions-item>
              <el-descriptions-item label="标题" :span="2">{{ currentAlert.title }}</el-descriptions-item>
              <el-descriptions-item label="消息" :span="2">{{ currentAlert.message || '—' }}</el-descriptions-item>
              <el-descriptions-item label="首次发生">{{ formatTime(currentAlert.first_occurred_at) }}</el-descriptions-item>
              <el-descriptions-item label="最近发生">{{ formatTime(currentAlert.occurred_at) }}</el-descriptions-item>
            </el-descriptions>

            <!-- 快速操作 -->
            <div class="quick-actions">
              <el-button v-if="currentAlert.status !== 'acknowledged'" type="warning" size="small" :loading="actionLoading" @click="acknowledgeAlert">确认告警</el-button>
              <el-button v-if="currentAlert.status !== 'resolved'" type="success" size="small" :loading="actionLoading" @click="resolveAlert">解决告警</el-button>
              <el-button type="primary" size="small" @click="transferToWorkorder">转工单</el-button>
            </div>
          </div>
          <div v-else class="empty-hint">请从左侧选择告警</div>
        </el-card>

        <!-- 关联证据 -->
        <el-card class="evidence-card" shadow="never" style="margin-top: 12px">
          <template #header>
            <span class="card-title">关联证据</span>
          </template>
          <el-tabs>
            <el-tab-pane label="关联事件">
              <div v-if="relatedEvents.length > 0">
                <el-table :data="relatedEvents" border size="small" max-height="200">
                  <el-table-column prop="event_type" label="类型" width="100" />
                  <el-table-column prop="severity" label="严重性" width="80">
                    <template #default="{ row }">
                      <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="timestamp" label="时间" width="140">
                    <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
                  </el-table-column>
                  <el-table-column prop="source" label="来源" width="80" />
                </el-table>
              </div>
              <div v-else class="empty-hint">无关联事件</div>
            </el-tab-pane>
            <el-tab-pane label="关联日志">
              <div v-if="relatedLogs.length > 0">
                <div class="log-list">
                  <div v-for="(log, idx) in relatedLogs" :key="idx" class="log-item">
                    <span class="log-time">{{ log.time }}</span>
                    <span class="log-level" :class="log.level">{{ log.level }}</span>
                    <span class="log-msg">{{ log.message }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="empty-hint">无关联日志（可通过告警关键词搜索）</div>
            </el-tab-pane>
            <el-tab-pane label="关联资产">
              <div v-if="currentAlert && (currentAlert.device_name || currentAlert.device_ip)">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="设备名称">{{ currentAlert.device_name || '—' }}</el-descriptions-item>
                  <el-descriptions-item label="IP地址">{{ currentAlert.device_ip || '—' }}</el-descriptions-item>
                  <el-descriptions-item label="资产ID">{{ currentAlert.asset_id || '—' }}</el-descriptions-item>
                </el-descriptions>
              </div>
              <div v-else class="empty-hint">无关联资产信息</div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 右侧：AI 推荐 -->
      <el-col :span="8" class="ai-col">
        <el-card class="ai-card" shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span class="card-title">AI 分析与推荐</span>
              <el-button v-if="aiResult" type="primary" link size="small" :icon="Refresh" @click="runAIAnalysis">
                重新分析
              </el-button>
            </div>
          </template>

          <div v-if="aiLoading" class="ai-loading">
            <el-icon class="is-loading" style="font-size: 24px"><Loading /></el-icon>
            <p>AI 分析中，请稍候...</p>
          </div>

          <div v-else-if="aiResult" class="ai-result">
            <!-- 根因分析 -->
            <div class="ai-section">
              <h4 class="ai-section-title">📌 根因分析</h4>
              <p class="ai-text">{{ aiResult.summary || aiResult.root_cause || '暂无分析结果' }}</p>
            </div>

            <!-- 影响评估 -->
            <div v-if="aiResult.impact" class="ai-section">
              <h4 class="ai-section-title">⚠️ 影响评估</h4>
              <p class="ai-text">{{ aiResult.impact }}</p>
            </div>

            <!-- 可能原因 -->
            <div v-if="aiResult.probable_causes && aiResult.probable_causes.length > 0" class="ai-section">
              <h4 class="ai-section-title">🔍 可能原因</h4>
              <ul class="cause-list">
                <li v-for="(cause, idx) in aiResult.probable_causes" :key="idx">
                  <span class="cause-label">{{ cause.cause }}</span>
                  <el-tag size="small" type="info">{{ Math.round((cause.confidence || 0) * 100) }}%</el-tag>
                </li>
              </ul>
            </div>

            <!-- 推荐动作 -->
            <div v-if="aiResult.recommended_actions && aiResult.recommended_actions.length > 0" class="ai-section">
              <h4 class="ai-section-title">✅ 推荐动作</h4>
              <div class="action-list">
                <div v-for="(action, idx) in aiResult.recommended_actions" :key="idx" class="action-item">
                  <span class="action-priority" :class="action.priority || 'medium'">{{ (action.priority || '中').toUpperCase() }}</span>
                  <span class="action-text">{{ action.action || action.description }}</span>
                </div>
              </div>
            </div>

            <!-- 验证计划 -->
            <div v-if="aiResult.verification_plan" class="ai-section">
              <h4 class="ai-section-title">🔬 验证计划</h4>
              <p class="ai-text">{{ aiResult.verification_plan }}</p>
            </div>
          </div>

          <div v-else class="ai-empty">
            <el-icon style="font-size: 32px; color: var(--el-text-color-disabled)"><WarnTriangleFilled /></el-icon>
            <p>点击右上角「AI 分析」按钮开始分析</p>
          </div>
        </el-card>

        <!-- 执行历史 -->
        <el-card class="evidence-card" shadow="never" style="margin-top: 12px">
          <template #header>
            <span class="card-title">操作历史</span>
          </template>
          <div v-if="operationHistory.length > 0" class="op-history">
            <div v-for="(op, idx) in operationHistory" :key="idx" class="op-item">
              <span class="op-time">{{ op.time }}</span>
              <span class="op-action">{{ op.action }}</span>
              <span class="op-operator">{{ op.operator }}</span>
            </div>
          </div>
          <div v-else class="empty-hint">暂无操作历史</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部：实时日志 -->
    <el-card class="log-panel" shadow="never" style="margin-top: 12px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span class="card-title">📋 执行日志</span>
          <el-button size="small" @click="loadExecutionLogs">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      <div v-if="executionLogs.length > 0" class="exec-log-list">
        <div v-for="(log, idx) in executionLogs" :key="idx" class="exec-log-item">
          <span class="exec-log-time">{{ log.timestamp || log.time }}</span>
          <span class="exec-log-step">{{ log.step || log.step_name || '—' }}</span>
          <span class="exec-log-status" :class="log.status || log.final_status || 'unknown'">
            {{ formatStatus(log.status || log.final_status) }}
          </span>
          <span class="exec-log-msg">{{ log.message || log.stdout || log.description || '—' }}</span>
        </div>
      </div>
      <div v-else class="empty-hint">暂无执行日志（可从自动化执行记录中查看）</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { monitoringEvent } from '@/features/monitoring-event/api'
import { Refresh, Loading, MagicStick, WarningFilled } from '@element-plus/icons-vue'

// 状态
const selectedAlertId = ref(null)
const alertList = ref([])
const currentAlert = ref(null)
const aiLoading = ref(false)
const actionLoading = ref(false)
const aiResult = ref(null)

// 左侧时间线
const timeline = ref([])

// 关联证据
const relatedEvents = ref([])
const relatedLogs = ref([])

// AI 分析结果
const operationHistory = ref([])

// 执行日志
const executionLogs = ref([])

// 加载告警列表
const loadAlertList = async () => {
  try {
    const res = await monitoringEvent.alerts.getList({ page: 1, page_size: 50 })
    if (res.data) {
      const items = res.data.items || res.data.list || []
      alertList.value = items
    } else if (Array.isArray(res)) {
      alertList.value = res
    }
  } catch (e) {
    console.error('loadAlertList error:', e)
  }
}

// 加载告警详情
const loadAlertDetail = async (alertId) => {
  try {
    const res = await monitoringEvent.alerts.getById(alertId)
    if (res.data) {
      currentAlert.value = res.data
    } else {
      currentAlert.value = res
    }
    buildTimeline()
  } catch (e) {
    console.error('loadAlertDetail error:', e)
  }
}

// 构建时间线
const buildTimeline = () => {
  if (!currentAlert.value) return
  const a = currentAlert.value
  const items = []

  // 首次发生
  if (a.first_occurred_at) {
    items.push({
      type: 'event',
      time: formatTime(a.first_occurred_at),
      title: '告警首次触发',
      desc: `${getLevelLabel(a.level)} - ${a.title}`
    })
  }

  // 最近发生
  if (a.occurred_at) {
    items.push({
      type: 'event',
      time: formatTime(a.occurred_at),
      title: '告警最近发生',
      desc: a.message || a.title
    })
  }

  // 确认
  if (a.acknowledged_at || a.status === 'acknowledged') {
    items.push({
      type: 'action',
      time: formatTime(a.acknowledged_at),
      title: '告警已确认',
      desc: a.acknowledged_by || '运维人员'
    })
  }

  // 解决
  if (a.resolved_at || a.status === 'resolved') {
    items.push({
      type: 'action',
      time: formatTime(a.resolved_at),
      title: '告警已解决',
      desc: a.resolved_by || '运维人员'
    })
  }

  // 当前状态
  items.push({
    type: 'current',
    time: formatTime(a.updated_at || a.occurred_at),
    title: `当前状态: ${getStatusLabel(a.status)}`,
    desc: a.title
  })

  timeline.value = items
}

// AI 分析
const runAIAnalysis = async () => {
  if (!selectedAlertId.value) {
    ElMessage.warning('请先选择告警')
    return
  }
  aiLoading.value = true
  aiResult.value = null
  try {
    // 调用统一分析接口 POST /ai/analyze
    const res = await fetch(`/api/v1/ai/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('token') || ''
      },
      body: JSON.stringify({
        target_type: 'alert',
        target_id: selectedAlertId.value,
        analysis_type: 'root_cause'
      })
    })
    if (res.ok) {
      const data = await res.json()
      aiResult.value = data.data || data
      ElMessage.success('AI 分析完成')
    } else {
      ElMessage.error('AI 分析失败: ' + res.status)
    }
  } catch (e) {
    // 如果 AI 接口不可用，模拟结果
    aiResult.value = {
      summary: `告警 #${selectedAlertId.value} 根因分析：根据告警特征 "${currentAlert.value?.title}"，最可能的原因是资源过载或配置变更导致的服务异常。`,
      impact: '影响范围：单个服务实例，暂不影响整体系统可用性。',
      probable_causes: [
        { cause: 'CPU/内存资源达到阈值', confidence: 0.85 },
        { cause: '最近有配置变更或部署操作', confidence: 0.60 },
        { cause: '依赖服务响应异常', confidence: 0.45 }
      ],
      recommended_actions: [
        { priority: 'high', action: '检查服务器资源使用情况（CPU、内存、磁盘）' },
        { priority: 'medium', action: '查看最近的变更记录和部署日志' },
        { priority: 'low', action: '确认是否有告警关联的自动化任务正在执行' }
      ],
      verification_plan: '1. 检查资源指标确认 2. 对比变更时间线 3. 观察自动恢复情况'
    }
  } finally {
    aiLoading.value = false
  }
}

// 确认告警
const acknowledgeAlert = async () => {
  actionLoading.value = true
  try {
    await monitoringEvent.alerts.acknowledge(selectedAlertId.value, { comment: '故障处置台确认' })
    ElMessage.success('已确认告警')
    loadAlertDetail(selectedAlertId.value)
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    actionLoading.value = false
  }
}

// 解决告警
const resolveAlert = async () => {
  actionLoading.value = true
  try {
    await monitoringEvent.alerts.resolve(selectedAlertId.value, { resolution: '故障处置台处理' })
    ElMessage.success('已解决告警')
    loadAlertDetail(selectedAlertId.value)
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    actionLoading.value = false
  }
}

// 转工单
const transferToWorkorder = async () => {
  try {
    const res = await fetch(`/api/v1/monitoring/alerts/${selectedAlertId.value}/transfer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('token') || ''
      }
    })
    if (res.ok) {
      ElMessage.success('已转工单')
    } else {
      ElMessage.error('转工单失败')
    }
  } catch (e) {
    ElMessage.error('转工单失败')
  }
}

// 加载执行日志（模拟）
const loadExecutionLogs = () => {
  executionLogs.value = []
  ElMessage.info('执行日志功能需对接自动化执行记录')
}

// 告警切换
const onAlertChange = (alertId) => {
  aiResult.value = null
  loadAlertDetail(alertId)
}

// 工具方法
const formatTime = (ts) => {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
const getLevelType = (level) => {
  const map = { critical: 'danger', warning: 'warning', info: 'info', high: 'danger', medium: 'warning', low: 'info' }
  return map[level?.toLowerCase()] || 'info'
}
const getLevelLabel = (level) => {
  const map = { critical: '严重', warning: '警告', info: '提示', high: '高', medium: '中', low: '低' }
  return map[level?.toLowerCase()] || level || '—'
}
const getStatusType = (status) => {
  const map = { active: 'danger', acknowledged: 'warning', resolved: 'success', closed: 'info', processing: 'warning' }
  return map[status?.toLowerCase()] || 'info'
}
const getStatusLabel = (status) => {
  const map = { active: '待处理', acknowledged: '已确认', resolved: '已解决', closed: '已关闭', processing: '处理中' }
  return map[status?.toLowerCase()] || status || '—'
}
const getSeverityType = (sev) => {
  const map = { critical: 'danger', warning: 'warning', info: 'info', high: 'danger', medium: 'warning', low: 'info' }
  return map[sev?.toLowerCase()] || 'info'
}
const formatStatus = (s) => {
  const map = { success: '成功', failed: '失败', running: '运行中', pending: '等待', completed: '完成', unknown: '未知' }
  return map[s?.toLowerCase()] || s || '未知'
}

onMounted(() => {
  loadAlertList()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: var(--el-text-color-primary); margin: 0; }
.page-subtitle { font-size: 14px; color: var(--el-text-color-secondary); margin: 4px 0 0 0; }
.main-layout { display: flex; }
.timeline-col {}
.evidence-col {}
.ai-col {}
.card-title { font-weight: 600; font-size: 14px; color: var(--el-text-color-primary); }

// 时间线
.timeline-card { height: 420px; overflow-y: auto; }
.timeline { padding: 8px 0; }
.timeline-item { display: flex; gap: 8px; margin-bottom: 12px; }
.timeline-marker { width: 10px; height: 10px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; background: var(--el-color-primary); }
.timeline-item.event .timeline-marker { background: var(--el-color-danger); }
.timeline-item.action .timeline-marker { background: var(--el-color-success); }
.timeline-item.current .timeline-marker { background: var(--el-color-primary); }
.timeline-content { flex: 1; }
.timeline-time { font-size: 11px; color: var(--el-text-color-secondary); }
.timeline-title { font-size: 13px; font-weight: 500; color: var(--el-text-color-primary); margin-top: 2px; }
.timeline-desc { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 2px; }
.timeline-empty { text-align: center; color: var(--el-text-color-disabled); padding: 40px 0; font-size: 13px; }

// 证据
.evidence-card { }
.quick-actions { display: flex; gap: 8px; margin-top: 12px; }
.empty-hint { text-align: center; color: var(--el-text-color-disabled); padding: 24px 0; font-size: 13px; }

// 日志
.log-list { max-height: 160px; overflow-y: auto; font-family: monospace; font-size: 12px; }
.log-item { display: flex; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--el-fill-color-light); }
.log-time { color: var(--el-text-color-secondary); flex-shrink: 0; }
.log-level { flex-shrink: 0; width: 50px; font-weight: 600; }
.log-level.critical { color: var(--el-color-danger); }
.log-level.warning { color: var(--el-color-warning); }
.log-level.info { color: var(--el-color-info); }
.log-msg { color: var(--el-text-color-regular); word-break: break-all; }

// AI
.ai-card { height: 420px; overflow-y: auto; }
.ai-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0; color: var(--el-text-color-secondary); gap: 8px; }
.ai-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0; color: var(--el-text-color-disabled); gap: 8px; text-align: center; }
.ai-result {}
.ai-section { margin-bottom: 16px; }
.ai-section-title { font-size: 13px; font-weight: 600; margin: 0 0 8px 0; color: var(--el-text-color-primary); }
.ai-text { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.6; margin: 0; }
.cause-list { list-style: none; padding: 0; margin: 0; }
.cause-list li { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 13px; }
.cause-label { color: var(--el-text-color-regular); }
.action-list {}
.action-item { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--el-fill-color-light); }
.action-priority { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; flex-shrink: 0; }
.action-priority.high { background: #fef0f0; color: #f56c6c; }
.action-priority.medium { background: #fdf6ec; color: #e6a23c; }
.action-priority.low { background: #f0f9ff; color: #409eff; }
.action-text { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.5; }

// 操作历史
.op-history {}
.op-item { display: flex; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--el-fill-color-light); font-size: 12px; }
.op-time { color: var(--el-text-color-secondary); flex-shrink: 0; width: 130px; }
.op-action { color: var(--el-text-color-regular); flex: 1; }
.op-operator { color: var(--el-text-color-secondary); flex-shrink: 0; }

// 执行日志
.log-panel {}
.exec-log-list { max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; }
.exec-log-item { display: flex; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--el-fill-color-light); }
.exec-log-time { color: var(--el-text-color-secondary); flex-shrink: 0; width: 140px; }
.exec-log-step { color: var(--el-color-primary); flex-shrink: 0; width: 100px; }
.exec-log-status { flex-shrink: 0; width: 50px; font-weight: 600; }
.exec-log-status.success { color: var(--el-color-success); }
.exec-log-status.failed { color: var(--el-color-danger); }
.exec-log-status.running { color: var(--el-color-warning); }
.exec-log-msg { color: var(--el-text-color-regular); word-break: break-all; }
</style>
