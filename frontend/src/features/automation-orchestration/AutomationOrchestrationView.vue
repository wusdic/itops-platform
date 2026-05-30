<template>
  <div class="automation-page">
    <!-- 顶部统计 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon scripts"><el-icon><Document /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.scripts }}</div>
            <div class="stat-label">剧本库</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon tasks"><el-icon><Clock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.tasks }}</div>
            <div class="stat-label">定时任务</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon executions"><el-icon><VideoPlay /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.executions }}</div>
            <div class="stat-label">执行记录</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon approvals"><el-icon><WarningFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.approvals }}</div>
            <div class="stat-label">待审批</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容 -->
    <el-card class="main-card">
      <el-tabs v-model="activeTab" class="main-tabs">
        <!-- 剧本库 -->
        <el-tab-pane label="剧本库" name="scripts">
          <div class="tab-toolbar">
            <el-button type="primary" @click="showScriptDialog = true">
              <el-icon><Plus /></el-icon> 新建剧本
            </el-button>
          </div>
          <el-table :data="scripts" v-loading="loading.scripts" stripe class="main-table">
            <el-table-column prop="name" label="剧本名称" min-width="160">
              <template #default="{ row }">
                <el-link type="primary" @click="viewScript(row)">{{ row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="script_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.script_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="riskTagType(row.risk_level)">{{ row.risk_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="80" />
            <el-table-column prop="created_by" label="创建人" width="100" />
            <el-table-column prop="updated_at" label="更新时间" width="180" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="runScript(row)">执行</el-button>
                <el-button size="small" @click="editScript(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteScript(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            class="table-pagination"
            :total="pagination.scripts.total"
            :page-size="pagination.scripts.page_size"
            :current-page="pagination.scripts.page"
            layout="total, prev, pager, next"
            @current-change="p => loadScripts(p)"
          />
        </el-tab-pane>

        <!-- 任务管理 -->
        <el-tab-pane label="任务管理" name="tasks">
          <div class="tab-toolbar">
            <el-button type="primary" @click="showTaskDialog = true">
              <el-icon><Plus /></el-icon> 新建任务
            </el-button>
          </div>
          <el-table :data="tasks" v-loading="loading.tasks" stripe class="main-table">
            <el-table-column prop="name" label="任务名称" min-width="160">
              <template #default="{ row }">
                <el-link type="primary" @click="viewTask(row)">{{ row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="trigger_type" label="触发方式" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.trigger_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cron_expression" label="Cron" width="120" />
            <el-table-column prop="target_script" label="关联剧本" min-width="140" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="taskStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_run" label="上次执行" width="180" />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="runTask(row)">立即执行</el-button>
                <el-button size="small" type="danger" @click="deleteTask(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 执行历史 -->
        <el-tab-pane label="执行历史" name="executions">
          <div class="tab-toolbar">
            <el-select v-model="execFilter.status" placeholder="状态筛选" clearable style="width:140px;margin-right:8px" @change="loadExecutions()">
              <el-option label="全部" value="" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="运行中" value="running" />
              <el-option label="待审批" value="waiting_approval" />
            </el-select>
            <el-date-picker
              v-model="execFilter.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width:240px;margin-right:8px"
              @change="loadExecutions()"
            />
            <el-button @click="execFilter={};loadExecutions()">重置</el-button>
          </div>
          <el-table :data="executions" v-loading="loading.executions" stripe class="main-table">
            <el-table-column prop="id" label="执行ID" width="220">
              <template #default="{ row }">
                <el-link type="primary" @click="viewExecution(row)">{{ row.id.substring(0,8) }}...</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="剧本名称" min-width="140" />
            <el-table-column prop="trigger_type" label="触发方式" width="100" />
            <el-table-column prop="status" label="状态" width="110">
              <template #default="{ row }">
                <el-tag size="small" :type="execStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="started_at" label="开始时间" width="180" />
            <el-table-column prop="finished_at" label="结束时间" width="180" />
            <el-table-column prop="duration" label="耗时" width="90">
              <template #default="{ row }">
                <span v-if="row.duration">{{ row.duration }}s</span>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewExecution(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            class="table-pagination"
            :total="pagination.executions.total"
            :page-size="pagination.executions.page_size"
            :current-page="pagination.executions.page"
            layout="total, prev, pager, next"
            @current-change="p => loadExecutions(p)"
          />
        </el-tab-pane>

        <!-- 审批中心 -->
        <el-tab-pane label="审批中心" name="approvals">
          <div class="tab-toolbar">
            <el-select v-model="approvalFilter.status" placeholder="状态筛选" clearable style="width:160px;margin-right:8px" @change="loadApprovals()">
              <el-option label="全部" value="" />
              <el-option label="待审批" value="pending" />
              <el-option label="已批准" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </div>
          <el-table :data="approvals" v-loading="loading.approvals" stripe class="main-table">
            <el-table-column prop="id" label="审批ID" width="220">
              <template #default="{ row }">
                <el-link type="primary" @click="viewApproval(row)">{{ row.id.substring(0,8) }}...</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="执行名称" min-width="160" />
            <el-table-column prop="requester" label="申请人" width="120" />
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="riskTagType(row.risk_level)">{{ row.risk_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="110">
              <template #default="{ row }">
                <el-tag size="small" :type="approvalStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="180" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="approve(row)" :disabled="row.status !== 'pending'">批准</el-button>
                <el-button size="small" type="danger" @click="reject(row)" :disabled="row.status !== 'pending'">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            class="table-pagination"
            :total="pagination.approvals.total"
            :page-size="pagination.approvals.page_size"
            :current-page="pagination.approvals.page"
            layout="total, prev, pager, next"
            @current-change="p => loadApprovals(p)"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 脚本详情抽屉 -->
    <el-drawer v-model="scriptDrawer" :title="selectedScript?.name" size="600px">
      <template v-if="selectedScript">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="剧本名称">{{ selectedScript.name }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selectedScript.script_type }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag size="small" :type="riskTagType(selectedScript.risk_level)">{{ selectedScript.risk_level }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源">{{ selectedScript.source }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ selectedScript.created_by }}</el-descriptions-item>
          <el-descriptions-item label="标签">{{ selectedScript.tags?.join(', ') || '—' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedScript.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ selectedScript.updated_at }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h4>脚本内容</h4>
        <pre class="script-content">{{ selectedScript.content }}</pre>
        <div class="drawer-actions">
          <el-button type="primary" @click="runScript(selectedScript)">执行此剧本</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 执行详情抽屉 -->
    <el-drawer v-model="executionDrawer" title="执行详情" size="650px">
      <template v-if="selectedExecution">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="执行ID">{{ selectedExecution.id }}</el-descriptions-item>
          <el-descriptions-item label="剧本名称">{{ selectedExecution.name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="触发方式">{{ selectedExecution.trigger_type || '—' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="execStatusType(selectedExecution.status)">{{ selectedExecution.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ selectedExecution.started_at || '—' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ selectedExecution.finished_at || '—' }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ selectedExecution.duration ? selectedExecution.duration + 's' : '—' }}</el-descriptions-item>
          <el-descriptions-item label="执行人">{{ selectedExecution.executed_by || '—' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h4>执行参数</h4>
        <pre class="script-content">{{ JSON.stringify(selectedExecution.parameters || {}, null, 2) }}</pre>
        <el-divider />
        <h4>执行日志</h4>
        <div class="log-container" ref="logContainer">
          <pre class="log-content">{{ executionLogs || '暂无日志' }}</pre>
        </div>
      </template>
    </el-drawer>

    <!-- 新建/编辑剧本对话框 -->
    <el-dialog v-model="showScriptDialog" :title="editingScript ? '编辑剧本' : '新建剧本'" width="600px">
      <el-form :model="scriptForm" label-width="100px">
        <el-form-item label="剧本名称" required>
          <el-input v-model="scriptForm.name" placeholder="请输入剧本名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="scriptForm.script_type" style="width:100%">
            <el-option label="Shell" value="shell" />
            <el-option label="Python" value="python" />
            <el-option label="PowerShell" value="powershell" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="scriptForm.risk_level" style="width:100%">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="scriptForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="脚本内容" required>
          <el-input v-model="scriptForm.content" type="textarea" :rows="10" placeholder="#!/bin/bash&#10;echo 'Hello'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showScriptDialog = false">取消</el-button>
        <el-button type="primary" @click="submitScript" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建任务对话框 -->
    <el-dialog v-model="showTaskDialog" title="新建任务" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="触发方式">
          <el-select v-model="taskForm.trigger_type" style="width:100%">
            <el-option label="Cron" value="cron" />
            <el-option label="Interval" value="interval" />
            <el-option label="手动" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式" v-if="taskForm.trigger_type === 'cron'">
          <el-input v-model="taskForm.cron_expression" placeholder="0 2 * * *" />
        </el-form-item>
        <el-form-item label="关联剧本" required>
          <el-select v-model="taskForm.target_script_id" placeholder="请选择剧本" style="width:100%">
            <el-option v-for="s in scripts" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 执行剧本对话框 -->
    <el-dialog v-model="showRunDialog" title="执行剧本" width="500px">
      <template v-if="runningScript">
        <p style="margin-bottom:16px">
          即将执行：<strong>{{ runningScript.name }}</strong>
          <el-tag size="small" :type="riskTagType(runningScript.risk_level)" style="margin-left:8px">{{ runningScript.risk_level }}</el-tag>
        </p>
        <el-alert v-if="runningScript.risk_level === 'high'" type="warning" :closable="false">
          高风险操作，确认要执行吗？
        </el-alert>
      </template>
      <template #footer>
        <el-button @click="showRunDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRunScript" :loading="running">确认执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Clock, VideoPlay, WarningFilled, Plus } from '@element-plus/icons-vue'
import automation from '@/api/automation'

const activeTab = ref('scripts')

// Stats
const stats = reactive({ scripts: 0, tasks: 0, executions: 0, approvals: 0 })

// Loading states
const loading = reactive({ scripts: false, tasks: false, executions: false, approvals: false })
const submitting = ref(false)
const running = ref(false)

// Data
const scripts = ref([])
const tasks = ref([])
const executions = ref([])
const approvals = ref([])

// Pagination
const pagination = reactive({
  scripts: { page: 1, page_size: 10, total: 0 },
  executions: { page: 1, page_size: 10, total: 0 },
  approvals: { page: 1, page_size: 10, total: 0 }
})

// Filters
const execFilter = reactive({ status: '', date_range: null })
const approvalFilter = reactive({ status: '' })

// Drawer/Modal states
const scriptDrawer = ref(false)
const executionDrawer = ref(false)
const selectedScript = ref(null)
const selectedExecution = ref(null)
const executionLogs = ref('')

// Form dialogs
const showScriptDialog = ref(false)
const showTaskDialog = ref(false)
const showRunDialog = ref(false)
const editingScript = ref(null)
const runningScript = ref(null)

const scriptForm = reactive({ name: '', script_type: 'shell', risk_level: 'medium', description: '', content: '' })
const taskForm = reactive({ name: '', trigger_type: 'cron', cron_expression: '', target_script_id: '' })

// Log container ref
const logContainer = ref(null)

// API wrapper using automation module
async function apiWrap(promise) {
  try {
    const res = await promise
    if (res === null || res === undefined) return null
    // handle wrapped {code, data} response
    if (res && res.data !== undefined) return res.data
    return res
  } catch (e) {
    if (e.response && e.response.status === 401) ElMessage.error('未授权，请重新登录')
    else if (e.response) ElMessage.error(`请求失败: ${e.response.status}`)
    else ElMessage.error(`请求失败: ${e.message}`)
    return null
  }
}

// Load functions
async function loadStats() {
  const [sc, tk, ex, ap] = await Promise.all([
    apiWrap(automation.scripts.getList({ page: 1, page_size: 1 })),
    apiWrap(automation.tasks.getList({ page: 1, page_size: 1 })),
    apiWrap(automation.executions.getList({ page: 1, page_size: 1 })),
    apiWrap(automation.approvals.getList({ page: 1, page_size: 1 }))
  ])
  if (sc) stats.scripts = sc.total || 0
  if (tk) stats.tasks = tk.total || 0
  if (ex) stats.executions = ex.total || 0
  if (ap) stats.approvals = ap.total || 0
}

async function loadScripts(page = 1) {
  loading.scripts = true
  try {
    const data = await apiWrap(automation.scripts.getList({ page, page_size: pagination.scripts.page_size }))
    scripts.value = data?.items || []
    pagination.scripts.total = data?.total || 0
    pagination.scripts.page = page
  } finally {
    loading.scripts = false
  }
}

async function loadTasks() {
  loading.tasks = true
  try {
    const data = await apiWrap(automation.tasks.getList({ page: 1, page_size: 100 }))
    tasks.value = data?.items || []
    pagination.tasks.total = data?.total || 0
  } finally {
    loading.tasks = false
  }
}

async function loadExecutions(page = 1) {
  loading.executions = true
  try {
    const params = { page, page_size: pagination.executions.page_size }
    if (execFilter.status) params.status = execFilter.status
    const data = await apiWrap(automation.executions.getList(params))
    executions.value = data?.items || []
    pagination.executions.total = data?.total || 0
    pagination.executions.page = page
  } finally {
    loading.executions = false
  }
}

async function loadApprovals(page = 1) {
  loading.approvals = true
  try {
    const params = { page, page_size: pagination.approvals.page_size }
    if (approvalFilter.status) params.status = approvalFilter.status
    const data = await apiWrap(automation.approvals.getList(params))
    approvals.value = data?.items || []
    pagination.approvals.total = data?.total || 0
    pagination.approvals.page = page
  } finally {
    loading.approvals = false
  }
}

// Actions
function viewScript(row) {
  selectedScript.value = row
  scriptDrawer.value = true
}

function editScript(row) {
  editingScript.value = row
  Object.assign(scriptForm, { name: row.name, script_type: row.script_type, risk_level: row.risk_level, description: row.description || '', content: row.content || '' })
  showScriptDialog.value = true
}

async function deleteScript(row) {
  try {
    await ElMessageBox.confirm(`确定删除剧本「${row.name}」吗？`, '删除确认', { type: 'warning' })
    const ok = await apiWrap(automation.scripts.delete(row.id))
    if (ok !== null) {
      ElMessage.success('删除成功')
      loadScripts()
      loadStats()
    }
  } catch (e) {}
}

function runScript(row) {
  runningScript.value = row
  showRunDialog.value = true
}

async function confirmRunScript() {
  if (!runningScript.value) return
  running.value = true
  try {
    const ok = await apiWrap(automation.scripts.execute(runningScript.value.id, {}))
    if (ok !== null) {
      ElMessage.success('执行已启动')
      showRunDialog.value = false
      loadExecutions()
      loadStats()
    }
  } finally {
    running.value = false
  }
}

async function submitScript() {
  if (!scriptForm.name || !scriptForm.content) {
    ElMessage.warning('请填写剧本名称和内容')
    return
  }
  submitting.value = true
  try {
    let ok
    if (editingScript.value) {
      ok = await apiWrap(automation.scripts.update(editingScript.value.id, scriptForm))
    } else {
      ok = await apiWrap(automation.scripts.create(scriptForm))
    }
    if (ok !== null) {
      ElMessage.success(editingScript.value ? '更新成功' : '创建成功')
      showScriptDialog.value = false
      editingScript.value = null
      Object.assign(scriptForm, { name: '', script_type: 'shell', risk_level: 'medium', description: '', content: '' })
      loadScripts()
      loadStats()
    }
  } finally {
    submitting.value = false
  }
}

function viewTask(row) {
  // Simple info display
  ElMessage.info(`任务: ${row.name}`)
}

async function deleteTask(row) {
  try {
    await ElMessageBox.confirm(`确定删除任务「${row.name}」吗？`, '删除确认', { type: 'warning' })
    const ok = await apiWrap(automation.tasks.delete(row.id))
    if (ok !== null) {
      ElMessage.success('删除成功')
      loadTasks()
      loadStats()
    }
  } catch (e) {}
}

async function runTask(row) {
  try {
    const ok = await apiWrap(automation.tasks.run(row.id, {}))
    if (ok !== null) {
      ElMessage.success('任务已触发')
      loadExecutions()
    }
  } catch (e) {}
}

async function viewExecution(row) {
  selectedExecution.value = row
  executionLogs.value = '加载中...'
  executionDrawer.value = true
  // Use correct API path: /automation/executions/{id}/logs
  const data = await apiWrap(automation.executions.getLogs(row.id))
  executionLogs.value = data?.logs || data?.stdout || data?.output || '暂无日志'
}

async function viewApproval(row) {
  ElMessage.info(`审批: ${row.name}`)
}

async function approve(row) {
  try {
    await ElMessageBox.confirm(`批准执行「${row.name}」？`, '审批确认', { type: 'success' })
    const ok = await apiWrap(automation.approvals.approve(row.id))
    if (ok !== null) {
      ElMessage.success('已批准')
      loadApprovals()
      loadStats()
    }
  } catch (e) {}
}

async function reject(row) {
  try {
    await ElMessageBox.confirm(`拒绝执行「${row.name}」？`, '审批确认', { type: 'warning' })
    const ok = await apiWrap(automation.approvals.reject(row.id))
    if (ok !== null) {
      ElMessage.success('已拒绝')
      loadApprovals()
      loadStats()
    }
  } catch (e) {}
}

async function submitTask() {
  if (!taskForm.name || !taskForm.target_script_id) {
    ElMessage.warning('请填写任务名称和选择剧本')
    return
  }
  submitting.value = true
  try {
    const ok = await apiWrap(automation.tasks.create(taskForm))
    if (ok !== null) {
      ElMessage.success('创建成功')
      showTaskDialog.value = false
      Object.assign(taskForm, { name: '', trigger_type: 'cron', cron_expression: '', target_script_id: '' })
      loadTasks()
      loadStats()
    }
  } finally {
    submitting.value = false
  }
}

// Tag type helpers
function riskTagType(level) {
  const map = { low: 'success', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}
function taskStatusType(status) {
  const map = { idle: 'info', running: 'primary', disabled: 'danger' }
  return map[status] || 'info'
}
function execStatusType(status) {
  const map = { success: 'success', failed: 'danger', running: 'primary', waiting_approval: 'warning', queued: 'info' }
  return map[status] || 'info'
}
function approvalStatusType(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

// Tab change
function handleTabChange(tab) {
  if (tab === 'scripts' && scripts.value.length === 0) loadScripts()
  if (tab === 'tasks' && tasks.value.length === 0) loadTasks()
  if (tab === 'executions' && executions.value.length === 0) loadExecutions()
  if (tab === 'approvals' && approvals.value.length === 0) loadApprovals()
}

onMounted(() => {
  loadStats()
  loadScripts()
})
</script>

<style scoped>
.automation-page {
  padding: 20px;
}
.stats-row {
  margin-bottom: 16px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}
.stat-icon.scripts { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon.tasks { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.executions { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-icon.approvals { background: linear-gradient(135deg, #fa709a, #fee140); }
.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; line-height: 1; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.main-card { margin-top: 0; }
.main-tabs { padding: 0 4px; }
.tab-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.main-table { margin-top: 8px; }
.table-pagination { margin-top: 16px; justify-content: flex-end; }
.script-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}
.log-container {
  background: #1e1e1e;
  border-radius: 6px;
  max-height: 400px;
  overflow-y: auto;
}
.log-content {
  color: #d4d4d4;
  padding: 16px;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}
.drawer-actions { margin-top: 16px; text-align: right; }
</style>
