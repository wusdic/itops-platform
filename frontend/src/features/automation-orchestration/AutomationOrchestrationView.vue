<template>
  <div class="auto-orch">
    <!-- 顶部：标题+统计卡片 -->
    <div class="header-bar">
      <div>
        <h2 class="page-title">自动化编排台</h2>
        <p class="page-subtitle">脚本库 · 任务管理 · 执行控制 · 审批中心</p>
      </div>
      <div class="header-stats">
        <el-statistic title="脚本总数" :value="stats.scripts" />
        <el-statistic title="任务总数" :value="stats.tasks" />
        <el-statistic title="执行总数" :value="stats.executions" />
        <el-statistic title="今日执行" :value="stats.todayExecutions" />
      </div>
    </div>

    <!-- 主Tab区 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- Tab1: 脚本库 -->
      <el-tab-pane label="脚本库" name="scripts">
        <div class="tab-toolbar">
          <el-input v-model="scriptKeyword" placeholder="搜索脚本名称/标签" style="width:260px" clearable @change="loadScripts">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="scriptTypeFilter" placeholder="脚本类型" clearable style="width:140px" @change="loadScripts">
            <el-option label="Shell" value="shell" />
            <el-option label="Python" value="python" />
            <el-option label="Ansible" value="ansible" />
          </el-select>
          <el-select v-model="riskFilter" placeholder="风险等级" clearable style="width:140px" @change="loadScripts">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
          <el-button type="primary" :icon="Plus" @click="showScriptDialog = true">新建脚本</el-button>
        </div>
        <el-table :data="scriptList" stripe v-loading="scriptLoading" @row-click="selectScript">
          <el-table-column prop="name" label="脚本名称" min-width="140">
            <template #default="{row}">
              <el-link type="primary" :underline="false">{{ row.name }}</el-link>
              <el-tag v-if="row.risk_level === 'high'" type="danger" size="small" style="margin-left:6px">高风险</el-tag>
              <el-tag v-else-if="row.risk_level === 'medium'" type="warning" size="small" style="margin-left:6px">中风险</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="script_type" label="类型" width="100" />
          <el-table-column prop="risk_level" label="风险" width="80">
            <template #default="{row}">
              <el-tag :type="riskTagType(row.risk_level)" size="small">{{ row.risk_level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="80" />
          <el-table-column prop="created_at" label="创建时间" width="160" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{row}">
              <el-button size="small" type="primary" @click.stop="runScript(row)">执行</el-button>
              <el-button size="small" @click.stop="viewScriptDetail(row)">详情</el-button>
              <el-button size="small" type="danger" plain @click.stop="deleteScript(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="scriptPage"
          v-model:page-size="scriptPageSize"
          :total="scriptTotal"
          :page-sizes="[10,20,50]"
          layout="total,sizes,prev,pager,next"
          style="margin-top:12px"
          @size-change="loadScripts"
          @current-change="loadScripts"
        />
      </el-tab-pane>

      <!-- Tab2: 任务管理 -->
      <el-tab-pane label="任务管理" name="tasks">
        <div class="tab-toolbar">
          <el-input v-model="taskKeyword" placeholder="搜索任务名称" style="width:260px" clearable @change="loadTasks">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="triggerFilter" placeholder="触发类型" clearable style="width:140px" @change="loadTasks">
            <el-option label="Cron" value="cron" />
            <el-option label="Manual" value="manual" />
            <el-option label="Event" value="event" />
          </el-select>
          <el-button type="primary" :icon="Plus" @click="showTaskDialog = true">新建任务</el-button>
        </div>
        <el-table :data="taskList" stripe v-loading="taskLoading">
          <el-table-column prop="name" label="任务名称" min-width="160">
            <template #default="{row}">
              <el-link type="primary" :underline="false">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="script_name" label="关联脚本" min-width="120" />
          <el-table-column prop="trigger_type" label="触发类型" width="100">
            <template #default="{row}">
              <el-tag size="small">{{ row.trigger_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="trigger_config" label="触发配置" min-width="160">
            <template #default="{row}">
              <span v-if="row.trigger_type === 'cron' && row.trigger_config">{{ row.trigger_config.cron || row.trigger_config.schedule }}</span>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="状态" width="80">
            <template #default="{row}">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{row}">
              <el-button size="small" type="success" @click="runTask(row)">立即执行</el-button>
              <el-button size="small" @click="viewTaskDetail(row)">详情</el-button>
              <el-button size="small" type="danger" plain @click="deleteTask(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="taskPage"
          v-model:page-size="taskPageSize"
          :total="taskTotal"
          :page-sizes="[10,20,50]"
          layout="total,sizes,prev,pager,next"
          style="margin-top:12px"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </el-tab-pane>

      <!-- Tab3: 执行历史 -->
      <el-tab-pane label="执行历史" name="executions">
        <div class="tab-toolbar">
          <el-input v-model="execKeyword" placeholder="搜索任务/脚本名称" style="width:260px" clearable @change="loadExecutions">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="execStatusFilter" placeholder="执行状态" clearable style="width:140px" @change="loadExecutions">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="运行中" value="running" />
            <el-option label="待审批" value="pending_approval" />
          </el-select>
          <el-button :icon="Refresh" @click="loadExecutions">刷新</el-button>
        </div>
        <el-table :data="execList" stripe v-loading="execLoading">
          <el-table-column prop="script_name" label="脚本" min-width="120" />
          <el-table-column prop="task_name" label="任务" min-width="120">
            <template #default="{row}">
              {{ row.task_name || '—' }}
            </template>
          </el-table-column>
          <el-table-column prop="trigger_type" label="触发" width="90" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{row}">
              <el-tag :type="execStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" width="160" />
          <el-table-column prop="finished_at" label="结束时间" width="160">
            <template #default="{row}">
              {{ row.finished_at || '—' }}
            </template>
          </el-table-column>
          <el-table-column prop="triggered_by" label="触发人" width="100" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{row}">
              <el-button size="small" @click="viewExecDetail(row)">详情</el-button>
              <el-button v-if="row.status === 'pending_approval'" size="small" type="warning" @click="approveExec(row)">审批</el-button>
              <el-button size="small" @click="viewExecLogs(row)">日志</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="execPage"
          v-model:page-size="execPageSize"
          :total="execTotal"
          :page-sizes="[10,20,50]"
          layout="total,sizes,prev,pager,next"
          style="margin-top:12px"
          @size-change="loadExecutions"
          @current-change="loadExecutions"
        />
      </el-tab-pane>

      <!-- Tab4: 执行详情（侧滑/对话框） -->
    </el-tabs>

    <!-- 脚本详情抽屉 -->
    <el-drawer v-model="scriptDrawer" :title="selectedScript?.name || '脚本详情'" size="600px">
      <template v-if="selectedScript">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="脚本ID">{{ selectedScript.id }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selectedScript.script_type }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="riskTagType(selectedScript.risk_level)">{{ selectedScript.risk_level }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源">{{ selectedScript.source }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ selectedScript.created_at }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedScript.description || '—' }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px">
          <div style="font-weight:600;margin-bottom:8px">脚本内容</div>
          <el-input v-if="selectedScript.content" type="textarea" :model-value="selectedScript.content" :rows="12" readonly />
          <span v-else>—</span>
        </div>
        <div style="margin-top:16px" v-if="selectedScript.params_schema?.length">
          <div style="font-weight:600;margin-bottom:8px">参数定义</div>
          <el-tag v-for="p in selectedScript.params_schema" :key="p.name" style="margin-right:6px;margin-bottom:6px">{{ p.name }}: {{ p.type || 'string' }}</el-tag>
        </div>
      </template>
    </el-drawer>

    <!-- 执行详情抽屉 -->
    <el-drawer v-model="execDrawer" title="执行详情" size="600px">
      <template v-if="selectedExec">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行ID" :span="2">{{ selectedExec.id }}</el-descriptions-item>
          <el-descriptions-item label="脚本">{{ selectedExec.script_name }}</el-descriptions-item>
          <el-descriptions-item label="任务">{{ selectedExec.task_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="触发类型">{{ selectedExec.trigger_type }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="execStatusTagType(selectedExec.status)">{{ selectedExec.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ selectedExec.started_at }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ selectedExec.finished_at || '—' }}</el-descriptions-item>
          <el-descriptions-item label="触发人">{{ selectedExec.triggered_by || '—' }}</el-descriptions-item>
          <el-descriptions-item label="执行时长" :span="2">
            {{ selectedExec.duration ? selectedExec.duration + 's' : '—' }}
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px">
          <div style="font-weight:600;margin-bottom:8px">执行结果摘要</div>
          <code v-if="selectedExec.result_summary">{{ selectedExec.result_summary }}</code>
          <span v-else>—</span>
        </div>
        <div v-if="selectedExec.error_message" style="margin-top:12px">
          <div style="font-weight:600;margin-bottom:8px;color:#f56c6c">错误信息</div>
          <el-alert type="error" :closable="false">{{ selectedExec.error_message }}</el-alert>
        </div>
      </template>
    </el-drawer>

    <!-- 执行日志抽屉 -->
    <el-drawer v-model="logsDrawer" title="执行日志" size="700px">
      <div v-loading="logsLoading">
        <el-button :icon="Refresh" size="small" @click="loadExecLogs" style="margin-bottom:12px">刷新</el-button>
        <el-input v-model="logFilter" placeholder="过滤日志内容" style="margin-bottom:12px" clearable />
        <div class="log-viewer">
          <pre v-for="(line,idx) in filteredLogs" :key="idx" class="log-line">{{ line }}</pre>
          <span v-if="execLogs.length === 0" style="color:#999">暂无日志</span>
        </div>
      </div>
    </el-drawer>

    <!-- 脚本执行对话框 -->
    <el-dialog v-model="runScriptDialog" title="执行脚本" width="520px">
      <el-form label-width="100px">
        <el-form-item label="脚本">{{ selectedScript?.name }}</el-form-item>
        <el-form-item label="风险等级">
          <el-tag :type="riskTagType(selectedScript?.risk_level)">{{ selectedScript?.risk_level }}</el-tag>
        </el-form-item>
        <el-form-item label="执行说明">
          <el-alert v-if="selectedScript?.risk_level === 'high'" type="warning" :closable="false">
            高风险脚本，审批通过后方可执行
          </el-alert>
          <el-alert v-else type="info" :closable="false">
            执行后可在执行历史中查看结果和日志
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="runScriptDialog = false">取消</el-button>
        <el-button type="primary" :loading="runLoading" @click="confirmRunScript">确认执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Refresh } from '@element-plus/icons-vue'

const request = window.axios || window.axios

// Tab状态
const activeTab = ref('scripts')

// 统计数据
const stats = ref({ scripts: 0, tasks: 0, executions: 0, todayExecutions: 0 })

// 脚本相关
const scriptList = ref([])
const scriptLoading = ref(false)
const scriptKeyword = ref('')
const scriptTypeFilter = ref('')
const riskFilter = ref('')
const scriptPage = ref(1)
const scriptPageSize = ref(10)
const scriptTotal = ref(0)

// 任务相关
const taskList = ref([])
const taskLoading = ref(false)
const taskKeyword = ref('')
const triggerFilter = ref('')
const taskPage = ref(1)
const taskPageSize = ref(10)
const taskTotal = ref(0)

// 执行相关
const execList = ref([])
const execLoading = ref(false)
const execKeyword = ref('')
const execStatusFilter = ref('')
const execPage = ref(1)
const execPageSize = ref(10)
const execTotal = ref(0)

// 弹窗/Drawer状态
const scriptDrawer = ref(false)
const selectedScript = ref(null)
const execDrawer = ref(false)
const selectedExec = ref(null)
const logsDrawer = ref(false)
const execLogs = ref([])
const logsLoading = ref(false)
const logFilter = ref('')
const showScriptDialog = ref(false)
const showTaskDialog = ref(false)
const runScriptDialog = ref(false)
const runLoading = ref(false)

const filteredLogs = computed(() => {
  if (!logFilter.value) return execLogs.value
  return execLogs.value.filter(l => l.toLowerCase().includes(logFilter.value.toLowerCase()))
})

// 加载统计数据
async function loadStats() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    const [scriptsRes, tasksRes, execsRes] = await Promise.all([
      fetch('/api/v1/automation/scripts?page=1&page_size=1', { headers }),
      fetch('/api/v1/automation/tasks?page=1&page_size=1', { headers }),
      fetch('/api/v1/automation/executions?page=1&page_size=1', { headers })
    ])
    const scriptsData = scriptsRes.ok ? (await scriptsRes.json()).data : {}
    const tasksData = tasksRes.ok ? (await tasksRes.json()).data : {}
    const execsData = execsRes.ok ? (await execsRes.json()).data : {}

    stats.value.scripts = scriptsData.total || 0
    stats.value.tasks = tasksData.total || 0
    stats.value.executions = execsData.total || 0

    // 今日执行
    const today = new Date().toISOString().split('T')[0]
    const todayRes = await fetch(`/api/v1/automation/executions?page=1&page_size=1&started_at=${today}`, { headers })
    if (todayRes.ok) {
      const d = (await todayRes.json()).data || {}
      stats.value.todayExecutions = d.total || 0
    }
  } catch (e) {
    console.error('loadStats failed', e)
  }
}

// 加载脚本列表
async function loadScripts() {
  scriptLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: scriptPage.value,
      page_size: scriptPageSize.value
    })
    if (scriptKeyword.value) params.append('keyword', scriptKeyword.value)
    if (scriptTypeFilter.value) params.append('script_type', scriptTypeFilter.value)
    if (riskFilter.value) params.append('risk_level', riskFilter.value)

    const res = await fetch(`/api/v1/automation/scripts?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('load scripts failed')
    const data = (await res.json()).data || {}
    scriptList.value = data.items || []
    scriptTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载脚本列表失败')
  } finally {
    scriptLoading.value = false
  }
}

// 加载任务列表
async function loadTasks() {
  taskLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: taskPage.value,
      page_size: taskPageSize.value
    })
    if (taskKeyword.value) params.append('keyword', taskKeyword.value)
    if (triggerFilter.value) params.append('trigger_type', triggerFilter.value)

    const res = await fetch(`/api/v1/automation/tasks?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('load tasks failed')
    const data = (await res.json()).data || {}
    taskList.value = data.items || []
    taskTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载任务列表失败')
  } finally {
    taskLoading.value = false
  }
}

// 加载执行历史
async function loadExecutions() {
  execLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams({
      page: execPage.value,
      page_size: execPageSize.value
    })
    if (execKeyword.value) params.append('keyword', execKeyword.value)
    if (execStatusFilter.value) params.append('status', execStatusFilter.value)

    const res = await fetch(`/api/v1/automation/executions?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('load executions failed')
    const data = (await res.json()).data || {}
    execList.value = data.items || []
    execTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载执行历史失败')
  } finally {
    execLoading.value = false
  }
}

// 执行脚本
function runScript(row) {
  selectedScript.value = row
  runScriptDialog.value = true
}

async function confirmRunScript() {
  runLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/scripts/${selectedScript.value.id}/execute`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '执行失败')
    }
    ElMessage.success('脚本已提交执行，请到执行历史中查看')
    runScriptDialog.value = false
    loadExecutions()
  } catch (e) {
    ElMessage.error('执行失败: ' + e.message)
  } finally {
    runLoading.value = false
  }
}

// 立即执行任务
async function runTask(row) {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/tasks/${row.id}/run`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('执行失败')
    ElMessage.success('任务已触发执行')
    loadExecutions()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

// 查看详情
function viewScriptDetail(row) {
  selectedScript.value = row
  scriptDrawer.value = true
}

function viewTaskDetail(row) {
  ElMessage.info('任务详情: ' + row.name)
}

function viewExecDetail(row) {
  selectedExec.value = row
  execDrawer.value = true
}

// 加载执行日志
async function viewExecLogs(row) {
  logsDrawer.value = true
  execLogs.value = []
  logsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/executions/${row.id}/logs`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    const logs = data.data?.logs || data.logs || (typeof data === 'string' ? data : '')
    execLogs.value = Array.isArray(logs) ? logs : String(logs).split('\n').filter(Boolean)
  } catch (e) {
    execLogs.value = ['日志加载失败']
  } finally {
    logsLoading.value = false
  }
}

async function loadExecLogs() {
  if (selectedExec.value) await viewExecLogs(selectedExec.value)
}

// 审批
async function approveExec(row) {
  try {
    await ElMessageBox.confirm('确认通过此执行的审批？', '审批确认', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/executions/${row.id}/approval`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: true })
    })
    if (!res.ok) throw new Error('审批失败')
    ElMessage.success('审批已通过')
    loadExecutions()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '审批操作失败')
  }
}

// 删除脚本
async function deleteScript(row) {
  try {
    await ElMessageBox.confirm(`确认删除脚本「${row.name}」？`, '删除确认', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/scripts/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('删除失败')
    ElMessage.success('删除成功')
    loadScripts()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

// 删除任务
async function deleteTask(row) {
  try {
    await ElMessageBox.confirm(`确认删除任务「${row.name}」？`, '删除确认', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/automation/tasks/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('删除失败')
    ElMessage.success('删除成功')
    loadTasks()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

// 选中脚本
function selectScript(row) {
  viewScriptDetail(row)
}

// 辅助函数
function riskTagType(level) {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

function execStatusTagType(status) {
  const map = { success: 'success', failed: 'danger', running: 'primary', pending_approval: 'warning', pending: 'info' }
  return map[status] || 'info'
}

onMounted(() => {
  loadStats()
  loadScripts()
  loadTasks()
  loadExecutions()
})
</script>

<style scoped>
.auto-orch {
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
.header-stats {
  display: flex;
  gap: 32px;
}
.main-tabs {
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.tab-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  align-items: center;
}
.log-viewer {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  max-height: 500px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
.log-line {
  margin: 2px 0;
  line-height: 1.5;
}
</style>
