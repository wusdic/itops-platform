<template>
  <div class="create-report-container">
    <el-card class="main-card">
      <div class="card-header">
        <div class="header-info">
          <h2>生成新报表</h2>
          <p>通过您喜欢的设置和过滤器创建自定义报表</p>
        </div>
      </div>

      <el-tabs type="line">
        <!-- Basic Settings Tab -->
        <el-tab-pane label="基础设置" name="basic">
          <div class="tab-content">
            <el-row :gutter="24">
              <!-- Left Column - Report Configuration -->
              <el-col :span="12">
                <el-card title="报表配置" class="config-card">
                  <!-- Report Type Selector -->
                  <el-form-item label="报表类型" required>
                    <el-row :gutter="12">
                      <el-col :span="8" v-for="type in reportTypes" :key="type.value">
                        <div
                          class="type-option"
                          :class="{ active: formData.type === type.value }"
                          @click="formData.type = type.value"
                        >
                          <el-icon :size="24" class="type-icon">
                            <component :is="type.icon" />
                          </el-icon>
                          <span class="type-label">{{ type.label }}</span>
                          <span class="type-desc">{{ type.description }}</span>
                        </div>
                      </el-col>
                    </el-row>
                  </el-form-item>

                  <!-- Template Selector -->
                  <el-form-item label="报表模板" required>
                    <el-select
                      v-model="formData.template_id"
                      :options="templateOptions"
                      placeholder="选择模板"
                      filterable
                      :loading="templatesLoading"
                      style="width: 100%"
                    />
                  </el-form-item>

                  <!-- Output Format Selector -->
                  <el-form-item label="输出格式" required>
                    <el-row :gutter="12">
                      <el-col :span="8" v-for="format in outputFormats" :key="format.value">
                        <div
                          class="format-option"
                          :class="{ active: formData.format === format.value }"
                          @click="formData.format = format.value"
                        >
                          <el-icon :size="32" class="format-icon">
                            <component :is="format.icon" />
                          </el-icon>
                          <span class="format-label">{{ format.label }}</span>
                        </div>
                      </el-col>
                    </el-row>
                  </el-form-item>
                </el-card>
              </el-col>

              <!-- Right Column - Date & Filters -->
              <el-col :span="12">
                <el-card title="日期范围和过滤器" class="config-card">
                  <!-- Date Range Picker -->
                  <el-form-item label="日期范围" required>
                    <el-date-picker
                      v-model="formData.date_range"
                      type="daterange"
                      range
                      clearable
                      style="width: 100%"
                    />
                  </el-form-item>

                  <!-- Quick Date Presets -->
                  <el-form-item label="快速选择">
                    <el-space :size="8">
                      <el-button
                        v-for="preset in datePresets"
                        :key="preset.label"
                        size="small"
                        @click="applyDatePreset(preset)"
                      >
                        {{ preset.label }}
                      </el-button>
                    </el-space>
                  </el-form-item>

                  <!-- Device Group Filter -->
                  <el-form-item label="设备分组">
                    <el-select
                      v-model="formData.device_group"
                      :options="deviceGroupOptions"
                      placeholder="所有设备分组"
                      clearable
                      multiple
                      style="width: 100%"
                    />
                  </el-form-item>

                  <!-- Alert Level Filter -->
                  <el-form-item label="告警级别">
                    <el-select
                      v-model="formData.alert_level"
                      :options="alertLevelOptions"
                      placeholder="所有告警级别"
                      clearable
                      multiple
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-card>
              </el-col>
            </el-row>

            <!-- Report Name -->
            <el-card title="报表详情" class="details-card">
              <el-form-item label="报表名称" required>
                <el-input
                  v-model="formData.name"
                  placeholder="输入报表名称"
                />
              </el-form-item>
              <el-form-item label="描述">
                <el-input
                  v-model="formData.description"
                  type="textarea"
                  placeholder="报表描述（可选）"
                  :rows="2"
                />
              </el-form-item>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- Preview Tab -->
        <el-tab-pane label="预览" name="preview">
          <div class="tab-content">
            <el-card class="preview-card">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>报表预览</span>
                  <el-space>
                    <el-button @click="refreshPreview" :loading="previewLoading">
                      <el-icon><Refresh /></el-icon>
                      刷新
                    </el-button>
                  </el-space>
                </div>
              </template>
              
              <div v-loading="previewLoading" class="preview-container">
                <div v-if="previewContent" class="preview-content" v-html="previewContent"></div>
                <el-empty v-else description="配置设置后点击生成预览查看预览" />
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Action Buttons -->
      <div class="action-bar">
        <el-space justify="space-between" align="center" style="width: 100%">
          <el-button @click="handleReset">重置表单</el-button>
          <el-space>
            <el-button @click="handleSaveTemplate" :loading="saving">
              <el-icon><Document /></el-icon>
              保存为模板
            </el-button>
            <el-button type="primary" @click="handleGenerate" :loading="generating">
              <el-icon><VideoPlay /></el-icon>
              生成报表
            </el-button>
          </el-space>
        </el-space>
      </div>
    </el-card>

    <!-- Save Template Modal -->
    <el-dialog
      v-model="saveTemplateModal.show"
      title="保存为模板"
      width="450px"
    >
      <el-form :model="saveTemplateForm" label-placement="top">
        <el-form-item label="模板名称" required>
          <el-input v-model="saveTemplateForm.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="saveTemplateForm.description"
            type="textarea"
            placeholder="模板描述（可选）"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="saveTemplateModal.show = false">取消</el-button>
          <el-button type="primary" @click="confirmSaveTemplate" :loading="savingTemplate">
            保存
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- Generation Progress Modal -->
    <el-dialog
      v-model="progressModal.show"
      title="正在生成报表"
      width="450px"
      :close-on-click-modal="false"
    >
      <div class="progress-content">
        <el-progress
          :percentage="progressModal.percentage"
          :status="progressModal.status"
          :stroke-width="20"
        />
        <p class="progress-text">{{ progressModal.message }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  VideoPlay,
  Refresh,
} from '@element-plus/icons-vue'

const message = ElMessage
const dialog = ElMessageBox

// Loading states
const templatesLoading = ref(false)
const previewLoading = ref(false)
const generating = ref(false)
const saving = ref(false)
const savingTemplate = ref(false)

// Form data
const formData = reactive({
  name: '',
  description: '',
  type: 'daily',
  template_id: null,
  format: 'pdf',
  date_range: null,
  device_group: null,
  alert_level: null
})

// Save template modal
const saveTemplateModal = reactive({
  show: false
})

const saveTemplateForm = reactive({
  name: '',
  description: ''
})

// Progress modal
const progressModal = reactive({
  show: false,
  percentage: 0,
  status: 'success',
  message: '正在准备报表生成...'
})

// Preview content
const previewContent = ref('')

// Template list
const templateList = ref([])

// Template options for select
const templateOptions = computed(() => {
  return templateList.value.map(t => ({
    label: t.name,
    value: t.id
  }))
})

// Device group options
const deviceGroupOptions = [
  { label: '生产服务器', value: 'prod_servers' },
  { label: '开发服务器', value: 'dev_servers' },
  { label: '数据库服务器', value: 'db_servers' },
  { label: '网络设备', value: 'network' },
  { label: '存储系统', value: 'storage' }
]

// Alert level options
const alertLevelOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

// Report types configuration
const reportTypes = [
  {
    value: 'daily',
    label: '日报',
    description: '24小时汇总',
    icon: 'Calendar'
  },
  {
    value: 'weekly',
    label: '周报',
    description: '7天汇总',
    icon: 'Calendar'
  },
  {
    value: 'monthly',
    label: '月报',
    description: '30天汇总',
    icon: 'Calendar'
  },
  {
    value: 'quarterly',
    label: '季报',
    description: '90天汇总',
    icon: 'Calendar'
  },
  {
    value: 'annual',
    label: '年报',
    description: '年度汇总',
    icon: 'Calendar'
  },
  {
    value: 'custom',
    label: '自定义',
    description: '自定义日期范围',
    icon: 'Setting'
  }
]

// Output formats configuration
const outputFormats = [
  { value: 'pdf', label: 'PDF', icon: 'Document' },
  { value: 'html', label: 'HTML', icon: 'Document' },
  { value: 'excel', label: 'Excel', icon: 'Document' }
]

// Date presets
const datePresets = [
  { label: '今天', getValue: () => { const now = new Date(); return [now, now] } },
  { label: '昨天', getValue: () => { const y = new Date(); y.setDate(y.getDate() - 1); return [y, y] } },
  { label: '最近7天', getValue: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 6); return [s, e] } },
  { label: '最近30天', getValue: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 29); return [s, e] } },
  { label: '本月', getValue: () => { const now = new Date(); return [new Date(now.getFullYear(), now.getMonth(), 1), now] } },
  { label: '上月', getValue: () => { const now = new Date(); const s = new Date(now.getFullYear(), now.getMonth() - 1, 1); const e = new Date(now.getFullYear(), now.getMonth(), 0); return [s, e] } }
]

// Helper functions
function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}

function applyDatePreset(preset) {
  const range = preset.getValue()
  if (range) {
    formData.date_range = range
  }
}

function validateForm() {
  if (!formData.name?.trim()) {
    message.error('请输入报表名称')
    return false
  }
  if (!formData.type) {
    message.error('请选择报表类型')
    return false
  }
  if (!formData.template_id) {
    message.error('请选择报表模板')
    return false
  }
  if (!formData.format) {
    message.error('请选择输出格式')
    return false
  }
  if (!formData.date_range || !formData.date_range[0] || !formData.date_range[1]) {
    message.error('请选择日期范围')
    return false
  }
  return true
}

// API Functions
async function fetchTemplates() {
  templatesLoading.value = true
  try {
    const response = await fetch('/api/v1/reports/template', {
      method: 'GET',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    templateList.value = data.items || data || []
  } catch (error) {
    message.error('加载模板失败')
    templateList.value = []
  } finally {
    templatesLoading.value = false
  }
}

async function fetchPreview() {
  if (!formData.template_id) {
    message.warning('请先选择模板')
    return
  }
  
  previewLoading.value = true
  try {
    const payload = {
      template_id: formData.template_id,
      type: formData.type,
      start_date: formData.date_range?.[0] ? new Date(formData.date_range[0]).toISOString() : null,
      end_date: formData.date_range?.[1] ? new Date(formData.date_range[1]).toISOString() : null,
      device_group: formData.device_group,
      alert_level: formData.alert_level
    }
    
    const response = await fetch('/api/v1/reports/preview', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    previewContent.value = data.content || data.html || '<p>预览不可用</p>'
  } catch (error) {
    message.error('加载预览失败')
    previewContent.value = ''
  } finally {
    previewLoading.value = false
  }
}

async function generateReport() {
  generating.value = true
  progressModal.show = true
  progressModal.percentage = 0
  progressModal.status = 'success'
  progressModal.message = '正在生成报表...'
  
  try {
    const progressInterval = setInterval(() => {
      if (progressModal.percentage < 90) {
        progressModal.percentage += Math.random() * 15
      }
    }, 500)
    
    const payload = {
      name: formData.name,
      description: formData.description,
      template_id: formData.template_id,
      type: formData.type,
      format: formData.format,
      start_date: formData.date_range?.[0] ? new Date(formData.date_range[0]).toISOString() : null,
      end_date: formData.date_range?.[1] ? new Date(formData.date_range[1]).toISOString() : null,
      filters: {
        device_group: formData.device_group,
        alert_level: formData.alert_level
      }
    }
    
    const response = await fetch('/api/v1/reports/generate', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    })
    
    clearInterval(progressInterval)
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    const data = await response.json()
    progressModal.percentage = 100
    progressModal.message = '报表生成成功！'
    message.success('报表生成成功')
    
    setTimeout(() => {
      progressModal.show = false
    }, 1500)
    
    return data
  } catch (error) {
    progressModal.percentage = 100
    progressModal.status = 'exception'
    progressModal.message = '生成报表失败'
    message.error('生成报表失败')
    throw error
  } finally {
    generating.value = false
  }
}

async function saveAsTemplate() {
  savingTemplate.value = true
  try {
    const payload = {
      name: saveTemplateForm.name,
      description: saveTemplateForm.description,
      type: formData.type,
      content: `<!-- Template for ${formData.type} report -->
<!-- Settings: ${JSON.stringify({ format: formData.format, filters: { device_group: formData.device_group, alert_level: formData.alert_level } })} -->`,
      active: true
    }
    
    const response = await fetch('/api/v1/reports/template', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    message.success('模板保存成功')
    saveTemplateModal.show = false
    saveTemplateForm.name = ''
    saveTemplateForm.description = ''
    fetchTemplates()
  } catch (error) {
    message.error('保存模板失败')
  } finally {
    savingTemplate.value = false
  }
}

// Action Handlers
function handleReset() {
  dialog.confirm(
    '确定要重置所有表单数据吗？',
    '确认重置',
    {
      confirmButtonText: '重置',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    formData.name = ''
    formData.description = ''
    formData.type = 'daily'
    formData.template_id = null
    formData.format = 'pdf'
    formData.date_range = null
    formData.device_group = null
    formData.alert_level = null
    previewContent.value = ''
    message.success('表单重置成功')
  }).catch(e => message.error('重置失败: ' + (e.message || e)))
}

function handleSaveTemplate() {
  if (!formData.type || !formData.format) {
    message.warning('请先选择报表类型和格式')
    return
  }
  saveTemplateModal.show = true
}

function confirmSaveTemplate() {
  if (!saveTemplateForm.name?.trim()) {
    message.error('请输入模板名称')
    return
  }
  saveAsTemplate()
}

async function handleGenerate() {
  if (!validateForm()) return
  try {
    await generateReport()
  } catch (error) {
    // Error already handled in generateReport
  }
}

function refreshPreview() {
  fetchPreview()
}

// Lifecycle
onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.create-report-container {
  padding: 16px;
  background: #f5f5f5;
  min-height: calc(100vh - 100px);
}

.main-card {
  border-radius: 12px;
}

.card-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header-info h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-info p {
  margin: 0;
  font-size: 14px;
  color: #8c8c8c;
}

.tab-content {
  padding: 20px 0;
}

.config-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.details-card {
  margin-top: 16px;
  border-radius: 8px;
}

.preview-card {
  border-radius: 8px;
}

.preview-container {
  min-height: 400px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.preview-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  max-width: 100%;
  overflow-x: auto;
}

/* Report Type Selector */
.type-option {
  padding: 12px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s ease;
  background: white;
}

.type-option:hover {
  border-color: #667eea;
  background: #f8f8ff;
}

.type-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.type-option.active .type-label,
.type-option.active .type-desc {
  color: white;
}

.type-icon {
  margin-bottom: 6px;
  color: #667eea;
}

.type-option.active .type-icon {
  color: white;
}

.type-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 2px;
}

.type-desc {
  display: block;
  font-size: 11px;
  color: #8c8c8c;
}

/* Output Format Selector */
.format-option {
  padding: 16px 12px;
  border: 2px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s ease;
  background: white;
}

.format-option:hover {
  border-color: #52c41a;
  background: #f8fff8;
}

.format-option.active {
  border-color: #52c41a;
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: white;
}

.format-option.active .format-label {
  color: white;
}

.format-icon {
  margin-bottom: 8px;
  color: #52c41a;
}

.format-option.active .format-icon {
  color: white;
}

.format-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

/* Action Bar */
.action-bar {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* Progress Content */
.progress-content {
  padding: 20px 0;
}

.progress-text {
  text-align: center;
  margin-top: 12px;
  color: #666;
}
</style>