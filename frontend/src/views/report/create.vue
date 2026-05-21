<template>
  <div class="create-report-container">
    <n-card class="main-card">
      <div class="card-header">
        <div class="header-info">
          <h2>生成新报表</h2>
          <p>通过您喜欢的设置和过滤器创建自定义报表</p>
        </div>
      </div>

      <n-tabs type="line" animated>
        <!-- Basic Settings Tab -->
        <n-tab-pane name="basic" tab="基础设置">
          <div class="tab-content">
            <n-grid :cols="2" :x-gap="24">
              <!-- Left Column - Report Configuration -->
              <n-gi>
                <n-card title="报表配置" class="config-card">
                  <!-- Report Type Selector -->
                  <n-form-item label="报表类型" required>
                    <n-grid :cols="3" :x-gap="12" :y-gap="12">
                      <n-gi v-for="type in reportTypes" :key="type.value">
                        <div
                          class="type-option"
                          :class="{ active: formData.type === type.value }"
                          @click="formData.type = type.value"
                        >
                          <n-icon :size="24" class="type-icon">
                            <component :is="type.icon" />
                          </n-icon>
                          <span class="type-label">{{ type.label }}</span>
                          <span class="type-desc">{{ type.description }}</span>
                        </div>
                      </n-gi>
                    </n-grid>
                  </n-form-item>

                  <!-- Template Selector -->
                  <n-form-item label="报表模板" required>
                    <n-select
                      v-model:value="formData.template_id"
                      :options="templateOptions"
                      placeholder="选择模板"
                      filterable
                      :loading="templatesLoading"
                    />
                  </n-form-item>

                  <!-- Output Format Selector -->
                  <n-form-item label="输出格式" required>
                    <n-space vertical :size="12">
                      <n-grid :cols="3" :x-gap="12">
                        <n-gi v-for="format in outputFormats" :key="format.value">
                          <div
                            class="format-option"
                            :class="{ active: formData.format === format.value }"
                            @click="formData.format = format.value"
                          >
                            <n-icon :size="32" class="format-icon">
                              <component :is="format.icon" />
                            </n-icon>
                            <span class="format-label">{{ format.label }}</span>
                          </div>
                        </n-gi>
                      </n-grid>
                    </n-space>
                  </n-form-item>
                </n-card>
              </n-gi>

              <!-- Right Column - Date & Filters -->
              <n-gi>
                <n-card title="日期范围和过滤器" class="config-card">
                  <!-- Date Range Picker -->
                  <n-form-item label="日期范围" required>
                    <n-date-picker
                      v-model:value="formData.date_range"
                      type="daterange"
                      range
                      clearable
                      style="width: 100%"
                    />
                  </n-form-item>

                  <!-- Quick Date Presets -->
                  <n-form-item label="快速选择">
                    <n-space :size="8">
                      <n-button
                        v-for="preset in datePresets"
                        :key="preset.label"
                        size="small"
                        @click="applyDatePreset(preset)"
                      >
                        {{ preset.label }}
                      </n-button>
                    </n-space>
                  </n-form-item>

                  <!-- Device Group Filter -->
                  <n-form-item label="设备分组">
                    <n-select
                      v-model:value="formData.device_group"
                      :options="deviceGroupOptions"
                      placeholder="所有设备分组"
                      clearable
                      multiple
                    />
                  </n-form-item>

                  <!-- Alert Level Filter -->
                  <n-form-item label="告警级别">
                    <n-select
                      v-model:value="formData.alert_level"
                      :options="alertLevelOptions"
                      placeholder="所有告警级别"
                      clearable
                      multiple
                    />
                  </n-form-item>
                </n-card>
              </n-gi>
            </n-grid>

            <!-- Report Name -->
            <n-card title="报表详情" class="details-card">
              <n-form-item label="报表名称" required>
                <n-input
                  v-model:value="formData.name"
                  placeholder="输入报表名称"
                />
              </n-form-item>
              <n-form-item label="描述">
                <n-input
                  v-model:value="formData.description"
                  type="textarea"
                  placeholder="报表描述（可选）"
                  :rows="2"
                />
              </n-form-item>
            </n-card>
          </div>
        </n-tab-pane>

        <!-- Preview Tab -->
        <n-tab-pane name="preview" tab="预览">
          <div class="tab-content">
            <n-card title="报表预览" class="preview-card">
              <template #header-extra>
                <n-space>
                  <n-button @click="refreshPreview" :loading="previewLoading">
                    <template #icon>
                      <n-icon><RefreshOutline /></n-icon>
                    </template>
                    刷新
                  </n-button>
                </n-space>
              </template>
              
              <n-spin :show="previewLoading">
                <div class="preview-container">
                  <div v-if="previewContent" class="preview-content" v-html="previewContent"></div>
                  <n-empty v-else description="配置设置后点击生成预览查看预览" />
                </div>
              </n-spin>
            </n-card>
          </div>
        </n-tab-pane>
      </n-tabs>

      <!-- Action Buttons -->
      <div class="action-bar">
        <n-space justify="space-between" align="center">
          <n-button @click="handleReset">重置表单</n-button>
          <n-space>
            <n-button @click="handleSaveTemplate" :loading="saving">
              <template #icon>
                <n-icon><DocumentTextOutline /></n-icon>
              </template>
              保存为模板
            </n-button>
            <n-button @click="handleGenerate" type="primary" :loading="generating">
              <template #icon>
                <n-icon><PlayOutline /></n-icon>
              </template>
              生成报表
            </n-button>
          </n-space>
        </n-space>
      </div>
    </n-card>

    <!-- Save Template Modal -->
    <n-modal
      v-model:show="saveTemplateModal.show"
      preset="card"
      title="保存为模板"
      :style="{ width: '450px' }"
    >
      <n-form :model="saveTemplateForm" label-placement="top">
        <n-form-item label="模板名称" required>
          <n-input v-model:value="saveTemplateForm.name" placeholder="输入模板名称" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input
            v-model:value="saveTemplateForm.description"
            type="textarea"
            placeholder="模板描述（可选）"
            :rows="2"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="saveTemplateModal.show = false">取消</n-button>
          <n-button type="primary" @click="confirmSaveTemplate" :loading="savingTemplate">
            保存
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Generation Progress Modal -->
    <n-modal
      v-model:show="progressModal.show"
      preset="card"
      title="正在生成报表"
      :closable="false"
      :mask-closable="false"
    >
      <div class="progress-content">
        <n-progress
          type="line"
          :percentage="progressModal.percentage"
          :status="progressModal.status"
          :processing="progressModal.processing"
        />
        <p class="progress-text">{{ progressModal.message }}</p>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, h } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import {
  AddOutline,
  DocumentTextOutline,
  DownloadOutline,
  TrashOutline,
  PlayOutline,
  EyeOutline,
  CreateOutline,
  RefreshOutline,
  ChevronForwardOutline
} from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

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
  processing: true,
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
    icon: 'DailyOutline'
  },
  {
    value: 'weekly',
    label: '周报',
    description: '7天汇总',
    icon: 'WeeklyOutline'
  },
  {
    value: 'monthly',
    label: '月报',
    description: '30天汇总',
    icon: 'MonthlyOutline'
  },
  {
    value: 'quarterly',
    label: '季报',
    description: '90天汇总',
    icon: 'QuarterlyOutline'
  },
  {
    value: 'annual',
    label: '年报',
    description: '年度汇总',
    icon: 'AnnualOutline'
  },
  {
    value: 'custom',
    label: '自定义',
    description: '自定义日期范围',
    icon: 'CustomOutline'
  }
]

// Output formats configuration
const outputFormats = [
  { value: 'pdf', label: 'PDF', icon: 'PdfOutline' },
  { value: 'html', label: 'HTML', icon: 'HtmlOutline' },
  { value: 'excel', label: 'Excel', icon: 'ExcelOutline' }
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
    console.error('Failed to fetch templates:', error)
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
    console.error('Failed to fetch preview:', error)
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
  progressModal.processing = true
  progressModal.message = '正在生成报表...'
  
  try {
    // Simulate progress updates
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
    progressModal.processing = false
    progressModal.status = 'success'
    
    message.success('报表生成成功')
    
    setTimeout(() => {
      progressModal.show = false
    }, 1500)
    
    return data
  } catch (error) {
    console.error('Failed to generate report:', error)
    progressModal.percentage = 100
    progressModal.status = 'error'
    progressModal.processing = false
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
      content: `<!-- Template for ${formData.type} report -->\n<!-- Settings: ${JSON.stringify({ format: formData.format, filters: { device_group: formData.device_group, alert_level: formData.alert_level } })} -->`,
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
    console.error('Failed to save template:', error)
    message.error('保存模板失败')
  } finally {
    savingTemplate.value = false
  }
}

// Action Handlers
function handleReset() {
  dialog.warning({
    title: '确认重置',
    content: '确定要重置所有表单数据吗？',
    positiveText: '重置',
    negativeText: '取消',
    onPositiveClick: () => {
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
    }
  })
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
