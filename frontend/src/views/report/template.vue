<template>
  <div class="template-container">
    <!-- Header -->
    <div class="header-section">
      <div class="header-title">
        <h2>报表模板</h2>
        <p class="header-desc">管理和配置报表模板以实现自动化生成</p>
      </div>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建模板
      </el-button>
    </div>

    <!-- Templates Grid -->
    <el-row :gutter="20" v-if="templateList.length > 0">
      <el-col :span="8" v-for="template in templateList" :key="template.id">
        <el-card class="template-card" shadow="hover">
          <div class="template-header">
            <div class="template-icon">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="template-info">
              <h3 class="template-name">{{ template.name }}</h3>
              <el-tag :type="getTypeColor(template.type)" size="small">
                {{ formatType(template.type) }}
              </el-tag>
            </div>
          </div>
          
          <div class="template-description">
            {{ template.description || '暂无描述' }}
          </div>
          
          <div class="template-meta">
            <div class="meta-item">
              <span class="meta-label">字段数:</span>
              <span class="meta-value">{{ template.fields?.length || 0 }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">状态:</span>
              <el-tag :type="template.active ? 'success' : 'info'" size="small">
                {{ template.active ? '启用' : '禁用' }}
              </el-tag>
            </div>
          </div>

          <div class="template-actions">
            <el-button size="small" @click="handleEdit(template)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(template)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Empty State -->
    <el-empty v-else description="暂无模板" class="empty-state">
      <template #extra>
        <el-button size="small" @click="handleCreate">创建第一个模板</el-button>
      </template>
    </el-empty>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="modal.show"
      :title="modal.isEdit ? '编辑模板' : '创建模板'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="top"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input
            v-model.trim="formData.name"
            placeholder="请输入模板名称"
          />
        </el-form-item>

        <el-form-item label="报表类型" prop="type">
          <el-select
            v-model="formData.type"
            :options="typeOptions"
            placeholder="请选择报表类型"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model.trim="formData.description"
            type="textarea"
            placeholder="请输入模板描述"
            :rows="3"
          />
        </el-form-item>

        <el-form-item label="模板内容" prop="content">
          <el-input
            v-model.trim="formData.content"
            type="textarea"
            placeholder="请输入HTML模板内容，占位符如 {{device_name}}, {{metric_value}}"
            :rows="8"
          />
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="formData.active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space justify="end">
          <el-button @click="modal.show = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="modal.loading">
            {{ modal.isEdit ? '更新' : '创建' }}
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog
      v-model="deleteModal.show"
      title="确认删除"
      width="400px"
    >
      <p>{{ deleteModal.message }}</p>
      <template #footer>
        <el-button @click="deleteModal.show = false">取消</el-button>
        <el-button type="danger" @click="handleConfirmDelete">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, Edit, Delete } from '@element-plus/icons-vue'

const message = ElMessage
const loading = ref(false)
const templateList = ref([])
const formRef = ref(null)

// Modal state
const modal = reactive({
  show: false,
  isEdit: false,
  loading: false,
  currentId: null
})

// Delete modal state
const deleteModal = reactive({
  show: false,
  message: '',
  templateId: null
})

// Form data
const formData = reactive({
  name: '',
  type: null,
  description: '',
  content: '',
  active: true
})

// Form rules
const formRules = {
  name: { required: true, message: '请输入模板名称', trigger: 'blur' },
  type: { required: true, message: '请选择报表类型', trigger: 'change' },
  content: { required: true, message: '请输入模板内容', trigger: 'blur' }
}

// Type options
const typeOptions = [
  { label: '日报', value: 'daily' },
  { label: '周报', value: 'weekly' },
  { label: '月报', value: 'monthly' },
  { label: '季报', value: 'quarterly' },
  { label: '年报', value: 'annual' },
  { label: '自定义报表', value: 'custom' }
]

// Helper functions
function getTypeColor(type) {
  const colors = {
    daily: 'primary',
    weekly: 'success',
    monthly: 'warning',
    quarterly: 'danger',
    annual: 'primary',
    custom: 'info'
  }
  return colors[type] || 'info'
}

function formatType(type) {
  const labels = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报',
    quarterly: '季报',
    annual: '年报',
    custom: '自定义'
  }
  return labels[type] || type
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}

function resetForm() {
  formData.name = ''
  formData.type = null
  formData.description = ''
  formData.content = ''
  formData.active = true
}

// API Functions
async function fetchTemplates() {
  loading.value = true
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
    loading.value = false
  }
}

async function createTemplate() {
  try {
    const response = await fetch('/api/v1/reports/template', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(formData)
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    message.success('模板创建成功')
    modal.show = false
    resetForm()
    fetchTemplates()
    return data
  } catch (error) {
    message.error('创建模板失败')
    throw error
  }
}

async function updateTemplate() {
  try {
    const response = await fetch(`/api/v1/reports/template/${modal.currentId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(formData)
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    message.success('模板更新成功')
    modal.show = false
    resetForm()
    fetchTemplates()
    return data
  } catch (error) {
    message.error('更新模板失败')
    throw error
  }
}

async function deleteTemplate(id) {
  try {
    const response = await fetch(`/api/v1/reports/template/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    message.success('模板删除成功')
    fetchTemplates()
  } catch (error) {
    message.error('删除模板失败')
  }
}

// Action Handlers
function handleCreate() {
  resetForm()
  modal.isEdit = false
  modal.currentId = null
  modal.show = true
}

function handleEdit(template) {
  modal.isEdit = true
  modal.currentId = template.id
  formData.name = template.name
  formData.type = template.type
  formData.description = template.description || ''
  formData.content = template.content || ''
  formData.active = template.active ?? true
  modal.show = true
}

function handleDelete(template) {
  deleteModal.templateId = template.id
  deleteModal.message = `确定要删除模板"${template.name}"吗？此操作无法撤销。`
  deleteModal.show = true
}

async function handleConfirmDelete() {
  await ElMessageBox.confirm('确定删除该模板吗？此操作不可恢复。', '删除确认', { type: 'warning' })
  if (deleteModal.templateId) {
    deleteTemplate(deleteModal.templateId)
  }
  deleteModal.show = false
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    modal.loading = true
    if (modal.isEdit) {
      await updateTemplate()
    } else {
      await createTemplate()
    }
  } catch (error) {
    // Validation error - handled by form
  } finally {
    modal.loading = false
  }
}

// Lifecycle
onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.template-container {
  padding: 16px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-title h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-desc {
  margin: 0;
  font-size: 14px;
  color: #8c8c8c;
}

.template-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.template-description {
  flex: 1;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-meta {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-label {
  font-size: 13px;
  color: #8c8c8c;
}

.meta-value {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
}

.template-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  margin-top: 80px;
}
</style>