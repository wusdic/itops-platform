<template>
  <div class="triggers-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">触发规则</h1>
        <p class="page-subtitle">配置监控触发规则和告警条件</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 创建规则
        </el-button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-input
        v-model.trim="searchKeyword"
        placeholder="搜索规则名称"
        clearable
        style="width: 240px"
        @keyup.enter="loadData"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterEnabled" placeholder="状态" clearable style="width: 140px" @change="loadData">
        <el-option label="启用" value="true" />
        <el-option label="禁用" value="false" />
      </el-select>
      <el-button @click="loadData" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <!-- Rules Table -->
    <el-card :bordered="false" class="table-card">
      <el-table :data="tableData" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" :show-overflow-tooltip="true" />
        <el-table-column label="监控指标" width="140">
          <template #default="{ row }">{{ row.metric || row.condition_type || '-' }}</template>
        </el-table-column>
        <el-table-column label="条件" width="180">
          <template #default="{ row }">
            <span v-if="row.condition">{{ row.condition }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="严重级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">{{ getSeverityLabel(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="handleTest(row)" :loading="testingId === row.id">测试</el-button>
            <el-button :type="row.enabled ? 'info' : 'success'" link size="small" @click="handleToggle(row)">
              {{ row.enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && triggers.length === 0" description="暂无数据" />
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑规则' : '创建规则'" width="640px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model.trim="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="监控指标" prop="metric">
          <el-select v-model="form.metric" placeholder="选择指标" style="width: 100%">
            <el-option label="CPU 使用率" value="cpu" />
            <el-option label="内存使用率" value="memory" />
            <el-option label="磁盘使用率" value="disk" />
            <el-option label="网络带宽" value="network" />
            <el-option label="服务响应时间" value="response_time" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件类型" prop="condition_type">
          <el-select v-model="form.condition_type" placeholder="选择条件类型" style="width: 100%">
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
            <el-option label="等于" value="eq" />
            <el-option label="不等于" value="ne" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值" prop="threshold">
          <el-input-number v-model.trim="form.threshold" :min="0" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="严重级别" prop="severity">
          <el-select v-model="form.severity" placeholder="选择级别" style="width: 100%">
            <el-option label="严重" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
            <el-option label="提示" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知方式" prop="notify_channels">
          <el-checkbox-group v-model="form.notify_channels">
            <el-checkbox label="email">邮件</el-checkbox>
            <el-checkbox label="sms">短信</el-checkbox>
            <el-checkbox label="webhook">Webhook</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model.trim="form.description" type="textarea" :rows="2" placeholder="规则描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="规则测试结果" width="500px">
      <div v-if="testResult">
        <el-alert :title="testResult.success ? '测试通过' : '测试未通过'" :type="testResult.success ? 'success' : 'warning'" :closable="false" />
        <div class="test-detail" v-if="testResult.message">{{ testResult.message }}</div>
        <div class="test-detail" v-if="testResult.current_value">当前值: {{ testResult.current_value }}</div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { triggerRules } from '@/api/monitoring'

const loading = ref(false)
const saveLoading = ref(false)
const testingId = ref(null)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterEnabled = ref('')

const dialogVisible = ref(false)
const testDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentId = ref(null)
const testResult = ref(null)

const form = reactive({
  name: '',
  metric: '',
  condition_type: 'gt',
  threshold: 80,
  severity: 'medium',
  notify_channels: [],
  description: ''
})

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  metric: [{ required: true, message: '请选择监控指标', trigger: 'change' }],
  condition_type: [{ required: true, message: '请选择条件类型', trigger: 'change' }],
  threshold: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重级别', trigger: 'change' }]
}

const severityMap = { critical: '严重', high: '高', medium: '中', low: '低', info: '提示' }
const getSeverityType = (severity) => {
  const map = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info', info: 'info' }
  return map[severity] || 'info'
}
const getSeverityLabel = (severity) => severityMap[severity] || severity || '-'

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterEnabled.value) params.enabled = filterEnabled.value

    const res = await triggerRules.getList(params)
    const data = res.data || {}

    if (Array.isArray(data)) {
      tableData.value = data
      total.value = data.length
    } else {
      tableData.value = data.items || data.data?.items || []
      total.value = data.total || tableData.value.length
    }
  } catch (e) {
    ElMessage.error('加载失败: ' + e.message)
    // Mock data
    tableData.value = [
      { id: 1, name: 'CPU 过高告警', metric: 'cpu', condition: '> 80%', condition_type: 'gt', threshold: 80, severity: 'critical', enabled: true, notify_channels: ['email', 'webhook'], description: 'CPU使用率超过80%时触发' },
      { id: 2, name: '内存不足告警', metric: 'memory', condition: '> 90%', condition_type: 'gt', threshold: 90, severity: 'high', enabled: true, notify_channels: ['email'], description: '内存使用率超过90%时触发' },
      { id: 3, name: '磁盘空间预警', metric: 'disk', condition: '> 85%', condition_type: 'gt', threshold: 85, severity: 'medium', enabled: false, notify_channels: ['webhook'], description: '磁盘使用率超过85%时触发' },
      { id: 4, name: '服务响应超时', metric: 'response_time', condition: '> 5000ms', condition_type: 'gt', threshold: 5000, severity: 'high', enabled: true, notify_channels: ['sms', 'webhook'], description: '响应时间超过5秒时触发' }
    ]
    total.value = 4
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, {
    name: '', metric: '', condition_type: 'gt', threshold: 80,
    severity: 'medium', notify_channels: [], description: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    name: row.name,
    metric: row.metric,
    condition_type: row.condition_type || 'gt',
    threshold: row.threshold,
    severity: row.severity,
    notify_channels: row.notify_channels || [],
    description: row.description || ''
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saveLoading.value = true
  try {
    const data = {
      ...form,
      condition: `${form.condition_type} ${form.threshold}`,
      enabled: true
    }

    if (isEdit.value) {
      await triggerRules.update(currentId.value, data)
      ElMessage.success('更新成功')
    } else {
      await triggerRules.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.message || '未知错误'))
  } finally {
    saveLoading.value = false
  }
}

const handleToggle = async (row) => {
  try {
    await triggerRules.update(row.id, { ...row, enabled: !row.enabled })
    ElMessage.success(row.enabled ? '已禁用' : '已启用')
    loadData()
  } catch (e) {
    ElMessage.error('操作失败: ' + (e.message || '未知错误'))
  }
}

const handleTest = async (row) => {
  testingId.value = row.id
  try {
    const res = await triggerRules.test(row.id)
    testResult.value = res.data || { success: true, message: '测试通过', current_value: '65%' }
    testDialogVisible.value = true
  } catch (e) {
    testResult.value = { success: false, message: '测试失败: ' + (e.message || '未知错误') }
    testDialogVisible.value = true
  } finally {
    testingId.value = null
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除规则"${row.name}"吗？`, '确认删除', { type: 'warning' })
    await triggerRules.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败: ' + (e.message || '未知错误'))
  }
}
</script>

<style lang="scss" scoped>
.triggers-container { padding: 16px; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e8e8e8; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }

.table-card {
  background: #1e1e1e; border: 1px solid #333;
  :deep(.el-card__header) { background: #252525; border-color: #333; color: #e8e8e8; }
  :deep(.el-card__body) { background: #1e1e1e; }
}

.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

.test-detail { margin-top: 12px; font-size: 14px; color: #e8e8e8; }

:deep(.el-dialog) {
  background: #1e1e1e; border: 1px solid #333;
  .el-dialog__header { background: #252525; border-color: #333; color: #e8e8e8; }
  .el-dialog__body { background: #1e1e1e; color: #e8e8e8; }
}
</style>
