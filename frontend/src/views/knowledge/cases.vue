<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>故障案例库</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加案例
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-space style="margin-bottom: 16px">
        <el-input v-model.trim="searchKeyword" placeholder="搜索标题/关键词" clearable style="width: 200px" @keyup.enter="loadData" />
        <el-select v-model="filterSeverity" :options="severityOptions" placeholder="严重程度" clearable style="width: 140px" @change="loadData" />
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="处理状态" clearable style="width: 140px" @change="loadData" />
      </el-space>

      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="标题" show-overflow-tooltip>
          <template #default="{ row }">
            <a href="javascript:void(0)" style="color:#18a058; cursor: pointer" @click="showDetail(row)">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column label="严重程度" width="90">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" width="160" show-overflow-tooltip />
        <el-table-column prop="occurred_at" label="发生时间" width="170" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" quaternary type="info" @click="showDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && list.length === 0" description="暂无数据" />

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 添加案例对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加故障案例" width="700px" :close-on-click-modal="false">
      <el-form :model="addForm" :rules="addFormRules" ref="addFormRef" label-position="top">
        <el-form-item label="案例标题" prop="title">
          <el-input v-model.trim="addForm.title" placeholder="请输入案例标题" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="addForm.severity" placeholder="选择严重程度" style="width: 100%">
                <el-option v-for="s in severityOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="处理状态" prop="status">
              <el-select v-model="addForm.status" placeholder="选择处理状态" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发生时间" prop="occurred_at">
              <el-date-picker v-model="addForm.occurred_at" type="datetime" placeholder="选择发生时间" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="解决时间" prop="resolved_at">
              <el-date-picker v-model="addForm.resolved_at" type="datetime" placeholder="选择解决时间" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关键词" prop="keywords">
          <el-input v-model.trim="addForm.keywords" placeholder="请输入关键词，多个用逗号分隔" />
        </el-form-item>
        <el-form-item label="影响范围" prop="impact">
          <el-input v-model.trim="addForm.impact" placeholder="请输入影响范围" />
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input v-model.trim="addForm.description" type="textarea" :rows="4" placeholder="请详细描述问题现象" />
        </el-form-item>
        <el-form-item label="根因分析" prop="root_cause">
          <el-input v-model.trim="addForm.root_cause" type="textarea" :rows="3" placeholder="请分析根本原因" />
        </el-form-item>
        <el-form-item label="解决方案" prop="solution">
          <el-input v-model.trim="addForm.solution" type="textarea" :rows="3" placeholder="请描述解决方案" />
        </el-form-item>
        <el-form-item label="经验教训" prop="lessons_learned">
          <el-input v-model.trim="addForm.lessons_learned" type="textarea" :rows="2" placeholder="请总结经验教训" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd" :loading="addLoading">提交</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailDrawer" :size="640" direction="rtl">
      <template #title>
        <span>{{ currentCase?.title || '案例详情' }}</span>
      </template>
      <el-descriptions v-if="currentCase" :column="1" border>
        <el-descriptions-item label="案例ID">{{ currentCase.id }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :type="getSeverityType(currentCase.severity)" size="small">{{ currentCase.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(currentCase.status)" size="small">{{ currentCase.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="关键词">{{ currentCase.keywords || '-' }}</el-descriptions-item>
        <el-descriptions-item label="影响范围">{{ currentCase.impact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发生时间">{{ currentCase.occurred_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="解决时间">{{ currentCase.resolved_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <el-tabs type="line">
        <el-tab-pane label="问题描述" name="desc">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.description || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="根因分析" name="root">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.root_cause || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="解决方案" name="solution">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.solution || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="经验教训" name="lessons">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.lessons_learned || '暂无' }}</div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailDrawer = false">关闭</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import knowledge from '@/api/knowledge'

const message = ElMessage
const loading = ref(false)
const list = ref([])
const searchKeyword = ref('')
const filterSeverity = ref(null)
const filterStatus = ref(null)
const detailDrawer = ref(false)
const currentCase = ref(null)

// Add dialog
const addDialogVisible = ref(false)
const addLoading = ref(false)
const addFormRef = ref(null)
const addForm = reactive({
  title: '',
  severity: '',
  status: '',
  occurred_at: null,
  resolved_at: null,
  keywords: '',
  impact: '',
  description: '',
  root_cause: '',
  solution: '',
  lessons_learned: ''
})

const addFormRules = {
  title: [{ required: true, message: '请输入案例标题', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
  status: [{ required: true, message: '请选择处理状态', trigger: 'change' }],
  occurred_at: [{ required: true, message: '请选择发生时间', trigger: 'change' }]
}

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const severityOptions = [
  { label: '严重', value: 'critical' },
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' },
]

const statusOptions = [
  { label: '未解决', value: 'open' },
  { label: '处理中', value: 'in_progress' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' },
]

function getSeverityType(s) {
  return { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }[s] || 'info'
}

function getStatusType(s) {
  return { open: 'danger', in_progress: 'warning', resolved: 'success', closed: 'info' }[s] || 'info'
}

function showDetail(row) {
  currentCase.value = row
  detailDrawer.value = true
}

function resetAddForm() {
  Object.assign(addForm, {
    title: '',
    severity: '',
    status: '',
    occurred_at: null,
    resolved_at: null,
    keywords: '',
    impact: '',
    description: '',
    root_cause: '',
    solution: '',
    lessons_learned: ''
  })
  addFormRef.value?.clearValidate()
}

function handleAdd() {
  resetAddForm()
  addDialogVisible.value = true
}

async function submitAdd() {
  try {
    await addFormRef.value?.validate()
  } catch { return }

  addLoading.value = true
  try {
    const data = {
      ...addForm,
      occurred_at: addForm.occurred_at ? new Date(addForm.occurred_at).toISOString() : null,
      resolved_at: addForm.resolved_at ? new Date(addForm.resolved_at).toISOString() : null
    }
    await knowledge.faultCase.create(data)
    message.success('故障案例创建成功')
    addDialogVisible.value = false
    await loadData()
  } catch (error) {
    message.error(error.message || '创建失败')
  } finally {
    addLoading.value = false
  }
}

onMounted(() => { loadData() })

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterSeverity.value) params.severity = filterSeverity.value
    if (filterStatus.value) params.status = filterStatus.value

    const data = await knowledge.faultCase.getList(params)
    list.value = data.items || data || []
    pagination.total = data.total || 0
  } catch (e) {
    message.error(`加载失败: ${e.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  pagination.page = page
  loadData()
}

function handlePageSizeChange(pageSize) {
  pagination.pageSize = pageSize
  pagination.page = 1
  loadData()
}
</script>
