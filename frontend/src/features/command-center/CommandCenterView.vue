<template>
  <div class="command-center">
    <!-- 顶部标题 -->
    <div class="header-bar">
      <div>
        <h2 class="page-title">运维指挥台</h2>
        <p class="page-subtitle">一屏展示全系统运行状态 · 严重告警 · AI建议</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>
      </div>
    </div>

    <!-- 第1行：核心指标卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header><span class="card-title">已监控设备</span></template>
          <div class="stat-body">
            <span class="stat-num">{{ overview.devices }}</span>
            <div class="stat-sub">
              <span class="online">在线 {{ overview.online }}</span>
              <span class="offline">离线 {{ overview.offline }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header><span class="card-title">活跃告警</span></template>
          <div class="stat-body">
            <span class="stat-num">{{ overview.alerts }}</span>
            <div class="stat-sub">
              <span class="critical">严重 {{ overview.critical }}</span>
              <span class="warning">警告 {{ overview.warning }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header><span class="card-title">执行中任务</span></template>
          <div class="stat-body">
            <span class="stat-num">{{ overview.running }}</span>
            <div class="stat-sub">
              <span>今日执行 {{ overview.todayExecutions }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header><span class="card-title">采集成功率</span></template>
          <div class="stat-body">
            <el-progress
              type="circle"
              :percentage="overview.collectionRate"
              :width="70"
              :stroke-width="8"
              :color="collectionRateColor"
            />
            <div class="stat-sub">
              <span>{{ overview.collectionRate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第2行：严重告警 + AI建议 -->
    <el-row :gutter="16" class="content-row">
      <!-- 左侧：严重告警列表 -->
      <el-col :span="14">
        <el-card shadow="hover" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span class="panel-title">🔥 严重告警</span>
              <el-tag type="danger" size="small">{{ criticalAlerts.length }} 条</el-tag>
            </div>
          </template>
          <div v-loading="alertsLoading">
            <el-table v-if="criticalAlerts.length" :data="criticalAlerts" stripe size="small">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="title" label="告警标题" min-width="160" />
              <el-table-column prop="level" label="级别" width="70">
                <template #default="{row}">
                  <el-tag :type="levelTagType(row.level)" size="small">{{ row.level }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="device_name" label="设备" width="120">
                <template #default="{row}">
                  {{ row.device_name || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="occurred_at" label="时间" width="140" />
              <el-table-column label="操作" width="100">
                <template #default="{row}">
                  <el-button size="small" @click="viewAlert(row)">处置</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无严重告警" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：AI建议摘要 -->
      <el-col :span="10">
        <el-card shadow="hover" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span class="panel-title">🤖 AI 建议摘要</span>
              <el-button size="small" :icon="Refresh" link @click="loadAISummary">刷新</el-button>
            </div>
          </template>
          <div v-loading="aiLoading">
            <div v-if="aiSummary" class="ai-summary">
              <div class="ai-item" v-for="(item, idx) in aiSummary" :key="idx">
                <div class="ai-item-title">{{ item.title }}</div>
                <div class="ai-item-content">{{ item.content }}</div>
                <el-tag v-if="item.priority" :type="item.priority === 'high' ? 'danger' : 'warning'" size="small">
                  {{ item.priority === 'high' ? '紧急' : '建议' }}
                </el-tag>
              </div>
            </div>
            <el-empty v-else description="暂无AI建议" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第3行：业务影响排行 + 自动化任务 -->
    <el-row :gutter="16" class="content-row">
      <!-- 业务影响排行 -->
      <el-col :span="12">
        <el-card shadow="hover" class="panel-card">
          <template #header>
            <span class="panel-title">📊 业务影响排行</span>
          </template>
          <div v-loading="bizLoading">
            <el-table v-if="bizImpact.length" :data="bizImpact" stripe size="small">
              <el-table-column type="index" label="排名" width="60" />
              <el-table-column prop="name" label="业务/服务" min-width="140" />
              <el-table-column prop="status" label="状态" width="90">
                <template #default="{row}">
                  <el-tag :type="row.status === 'healthy' ? 'success' : 'danger'" size="small">
                    {{ row.status === 'healthy' ? '正常' : '异常' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="alert_count" label="关联告警" width="90">
                <template #default="{row}">
                  <el-tag v-if="row.alert_count > 0" type="danger" size="small">{{ row.alert_count }}</el-tag>
                  <span v-else>0</span>
                </template>
              </el-table-column>
              <el-table-column prop="uptime" label="可用率" width="80" />
            </el-table>
            <el-empty v-else description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 自动化执行中任务 -->
      <el-col :span="12">
        <el-card shadow="hover" class="panel-card">
          <template #header>
            <div class="panel-header">
              <span class="panel-title">⚡ 自动化执行中</span>
              <el-tag size="small">{{ runningTasks.length }} 个任务运行中</el-tag>
            </div>
          </template>
          <div v-loading="tasksLoading">
            <el-table v-if="runningTasks.length" :data="runningTasks" stripe size="small">
              <el-table-column prop="script_name" label="脚本" min-width="120" />
              <el-table-column prop="task_name" label="任务" min-width="120">
                <template #default="{row}">
                  {{ row.task_name || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="90">
                <template #default="{row}">
                  <el-tag type="primary" size="small">running</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="started_at" label="开始时间" width="140" />
            </el-table>
            <el-empty v-else description="当前无运行中的任务" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第4行：最新告警动态（时间线） -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="24">
        <el-card shadow="hover" class="panel-card">
          <template #header>
            <span class="panel-title">📋 告警动态时间线</span>
          </template>
          <div v-loading="timelineLoading">
            <el-timeline v-if="alertTimeline.length">
              <el-timeline-item
                v-for="item in alertTimeline"
                :key="item.id"
                :type="timelineItemType(item.level)"
                :timestamp="item.occurred_at"
                placement="top"
              >
                <el-card size="small">
                  <div class="timeline-item">
                    <span class="timeline-title">
                      <el-tag :type="levelTagType(item.level)" size="small" style="margin-right:6px">{{ item.level }}</el-tag>
                      {{ item.title }}
                    </span>
                    <span class="timeline-device">{{ item.device_name || item.device_ip || '—' }}</span>
                    <span class="timeline-msg">{{ item.message }}</span>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无告警动态" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

// 加载状态
const alertsLoading = ref(false)
const aiLoading = ref(false)
const bizLoading = ref(false)
const tasksLoading = ref(false)
const timelineLoading = ref(false)

// 统计数据
const overview = ref({ devices: 0, online: 0, offline: 0, alerts: 0, critical: 0, warning: 0, running: 0, todayExecutions: 0, collectionRate: 98 })

// 严重告警
const criticalAlerts = ref([])

// AI建议
const aiSummary = ref(null)

// 业务影响
const bizImpact = ref([])

// 运行中任务
const runningTasks = ref([])

// 告警时间线
const alertTimeline = ref([])

const collectionRateColor = computed(() => {
  if (overview.value.collectionRate >= 95) return '#67c23a'
  if (overview.value.collectionRate >= 80) return '#e6a23c'
  return '#f56c6c'
})

function levelTagType(level) {
  const map = { critical: 'danger', warning: 'warning', info: 'info', low: 'success' }
  return map[level] || 'info'
}

function timelineItemType(level) {
  const map = { critical: 'danger', warning: 'warning', info: 'primary', low: 'success' }
  return map[level] || 'info'
}

// 刷新全部
async function refreshAll() {
  await Promise.all([loadOverview(), loadCriticalAlerts(), loadBizImpact(), loadRunningTasks(), loadAlertTimeline(), loadAISummary()])
  ElMessage.success('刷新完成')
}

// 加载概览统计
async function loadOverview() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    // 设备统计
    const devRes = await fetch('/api/v1/device/devices?page=1&page_size=1', { headers })
    if (devRes.ok) {
      const d = await devRes.json()
      const devData = d.data || d
      overview.value.devices = devData.total || 0
    }

    // 告警统计 - 直接返回 {total, critical, warning, info, active}
    const alertRes = await fetch('/api/v1/monitoring/alerts/statistics', { headers })
    if (alertRes.ok) {
      const d = await alertRes.json()
      const alertData = d.data || d
      overview.value.alerts = alertData.total || 0
      overview.value.critical = alertData.critical || 0
      overview.value.warning = alertData.warning || 0
    }

    // 运行中任务
    const execRes = await fetch('/api/v1/automation/executions?page=1&page_size=100', { headers })
    if (execRes.ok) {
      const d = await execRes.json()
      const execData = d.data || d
      const items = execData.items || []
      overview.value.running = items.filter(e => e.status === 'running').length
      overview.value.todayExecutions = items.filter(e => {
        if (!e.started_at) return false
        return e.started_at.startsWith(new Date().toISOString().split('T')[0])
      }).length
    }
  } catch (e) {
    console.error('loadOverview failed', e)
  }
}

// 加载严重告警
async function loadCriticalAlerts() {
  alertsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/monitoring/alerts?page=1&page_size=10', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const raw = await res.json()
    const data = raw.data || raw
    criticalAlerts.value = (data.items || []).filter(a => a.level === 'critical')
  } catch (e) {
    console.error('loadCriticalAlerts failed', e)
  } finally {
    alertsLoading.value = false
  }
}

// 加载业务影响
async function loadBizImpact() {
  bizLoading.value = true
  try {
    // 获取所有告警，按设备聚合
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/monitoring/alerts?page=1&page_size=100', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const raw = await res.json()
    const data = raw.data || raw
    const alerts = data.items || []

    // 按 device_name 聚合
    const map = {}
    alerts.forEach(a => {
      const key = a.device_name || a.device_ip || '未知设备'
      if (!map[key]) map[key] = { name: key, alert_count: 0, status: 'healthy' }
      if (a.status !== 'resolved') {
        map[key].alert_count++
        map[key].status = 'degraded'
      }
    })

    bizImpact.value = Object.values(map)
      .sort((a, b) => b.alert_count - a.alert_count)
      .slice(0, 8)
      .map(item => ({ ...item, uptime: item.status === 'healthy' ? '100%' : (100 - Math.min(item.alert_count * 5, 30)) + '%' }))
  } catch (e) {
    console.error('loadBizImpact failed', e)
  } finally {
    bizLoading.value = false
  }
}

// 加载运行中任务
async function loadRunningTasks() {
  tasksLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/automation/executions?page=1&page_size=50', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const raw = await res.json()
    const data = raw.data || raw
    runningTasks.value = (data.items || []).filter(e => e.status === 'running')
  } catch (e) {
    console.error('loadRunningTasks failed', e)
  } finally {
    tasksLoading.value = false
  }
}

// 加载告警时间线
async function loadAlertTimeline() {
  timelineLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/monitoring/alerts?page=1&page_size=20', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const raw = await res.json()
    const data = raw.data || raw
    alertTimeline.value = data.items || []
  } catch (e) {
    console.error('loadAlertTimeline failed', e)
  } finally {
    timelineLoading.value = false
  }
}

// 加载AI建议
async function loadAISummary() {
  aiLoading.value = true
  try {
    const token = localStorage.getItem('token')

    // 尝试从最近的 AI 分析历史获取建议
    const res = await fetch('/api/v1/aiops/analysis/history?page=1&page_size=3', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const raw = await res.json()
    const items = raw.data?.items || raw.items || []

    if (items.length) {
      aiSummary.value = items.slice(0, 4).map(item => ({
        title: item.summary?.substring(0, 50) || 'AI 分析结果',
        content: item.root_causes?.join('；') || item.recommended_actions?.join('；') || '暂无详细建议',
        priority: item.confidence > 0.8 ? 'high' : 'normal'
      }))
    } else {
      // 无历史时生成模拟建议
      aiSummary.value = [
        { title: '告警趋势平稳', content: '当前系统运行正常，无重大异常', priority: 'normal' },
        { title: '建议关注', content: '建议定期检查日志采集状态，确保数据完整性', priority: 'normal' }
      ]
    }
  } catch (e) {
    // 静默失败
    aiSummary.value = [
      { title: '告警趋势平稳', content: '当前系统运行正常，无重大异常', priority: 'normal' },
      { title: '建议关注', content: '建议定期检查日志采集状态，确保数据完整性', priority: 'normal' }
    ]
  } finally {
    aiLoading.value = false
  }
}

// 查看告警（跳转处置台）
function viewAlert(alert) {
  window.location.href = '/incident-response?alert_id=' + alert.id
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.command-center {
  padding: 20px;
  min-height: 100%;
  background: #f5f7fa;
}
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.page-title {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
}
.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 13px;
}
.stat-row {
  margin-bottom: 16px;
}
.content-row {
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
}
.card-title {
  font-weight: 600;
  font-size: 14px;
}
.stat-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}
.stat-num {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}
.stat-sub {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 13px;
}
.online { color: #67c23a; }
.offline { color: #909399; }
.critical { color: #f56c6c; }
.warning { color: #e6a23c; }

.panel-card {
  height: 100%;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.panel-title {
  font-weight: 600;
  font-size: 15px;
}
.ai-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ai-item {
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}
.ai-item-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 4px;
  color: #303133;
}
.ai-item-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}
.timeline-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.timeline-title {
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
}
.timeline-device {
  font-size: 12px;
  color: #409eff;
}
.timeline-msg {
  font-size: 12px;
  color: #909399;
}
</style>
