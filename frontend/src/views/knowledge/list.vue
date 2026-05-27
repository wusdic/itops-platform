<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识库 / SOP列表</h1>
        <p class="page-subtitle">运维标准操作流程</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreateModal">
          <el-icon><Plus /></el-icon>
          创建文档
        </el-button>
        <el-button type="primary" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="mb-4">
      <el-space align="center">
        <el-input
          v-model.trim="searchKeyword"
          placeholder="搜索标题"
          clearable
          style="width: 200px"
          @keyup.enter="loadData"
        />
        <el-select
          v-model="filterStatus"
          placeholder="按状态筛选"
          clearable
          style="width: 150px"
          @change="loadData"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="待审核" value="pending_review" />
          <el-option label="已通过" value="approved" />
          <el-option label="已发布" value="published" />
        </el-select>
        <el-select
          v-model="filterCategory"
          placeholder="按分类筛选"
          clearable
          style="width: 150px"
          @change="loadData"
        >
          <el-option
            v-for="cat in categoryOptions"
            :key="cat.value"
            :label="cat.label"
            :value="cat.value"
          />
        </el-select>
      </el-space>
    </el-card>

    <!-- SOP列表 -->
    <el-card title="SOP文档列表">
      <el-table
        v-loading="loading"
        :data="list"
        :row-key="row => row.id"
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="标题" min-width="200">
          <template #default="props">
            <a href="javascript:void(0)" @click="showDetail(props.row)" style="color: #409eff">
              {{ props.row.title }}
            </a>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="props">
            <el-tag :type="getStatusType(props.row.status)" size="small">
              {{ props.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column label="标签" min-width="200">
          <template #default="props">
            <el-tag
              v-for="tag in (props.row.tags || [])"
              :key="tag"
              size="small"
              style="margin-right: 4px"
            >{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="280">
          <template #default="props">
            <el-space>
              <el-button size="small" @click="openEditModal(props.row)">编辑</el-button>
              <el-button
                v-if="props.row.status === 'draft'"
                size="small"
                type="warning"
                @click="submitReview(props.row)"
              >提交审核</el-button>
              <el-button
                v-if="props.row.status === 'pending_review'"
                size="small"
                type="success"
                @click="approve(props.row)"
              >审核通过</el-button>
              <el-button size="small" type="danger" @click="handleDelete(props.row)">删除</el-button>
            </el-space>
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
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailModalVisible" title="SOP详情" width="600px">
      <el-descriptions v-if="currentSOP" :column="1" border>
        <el-descriptions-item label="标题">{{ currentSOP.title }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentSOP.category_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentSOP.status)">{{ currentSOP.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentSOP.author }}</el-descriptions-item>
        <el-descriptions-item label="标签">
          <el-tag
            v-for="tag in (currentSOP.tags || [])"
            :key="tag"
            size="small"
            style="margin-right: 4px"
          >{{ tag }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentSOP.created_at, 'YYYY-MM-DD HH:mm') }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(currentSOP.updated_at, 'YYYY-MM-DD HH:mm') }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailModalVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="formModalVisible"
      :title="isEditing ? '编辑文档' : '创建文档'"
      width="600px"
    >
      <el-form :model="formData" label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model.trim="formData.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="formData.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="cat in categoryOptions"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model.trim="formData.content" type="textarea" placeholder="请输入文档内容" :rows="6" />
        </el-form-item>
        <el-form-item label="标签（逗号分隔）">
          <el-input v-model.trim="formData.tags_input" placeholder="例如: 运维, 系统, 监控" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="formModalVisible = false">取消</el-button>
          <el-button type="primary" :loading="formLoading" @click="submitForm">确认</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'

const loading = ref(false)
const list = ref([])
const searchKeyword = ref('')
const filterStatus = ref(null)
const filterCategory = ref(null)
const detailModalVisible = ref(false)
const currentSOP = ref(null)

// Form modal state
const formModalVisible = ref(false)
const isEditing = ref(false)
const formLoading = ref(false)
const editingId = ref(null)
const formData = reactive({
  title: '',
  category_id: null,
  content: '',
  tags_input: '',
  status: 'draft'
})

const categoryOptions = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

onMounted(() => {
  loadCategories()
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (filterCategory.value) params.append('category_id', filterCategory.value)

    const res = await fetch(`/api/v1/knowledge/sop?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    list.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载失败: ${e.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/knowledge/category', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    categoryOptions.value = (data.items || []).map(c => ({ label: c.name, value: c.id }))
  } catch (_) { ElMessage.error("操作失败"); }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  formData.title = ''
  formData.category_id = null
  formData.content = ''
  formData.tags_input = ''
  formData.status = 'draft'
  formModalVisible.value = true
}

const openEditModal = async (row) => {
  isEditing.value = true
  editingId.value = row.id
  formModalVisible.value = true
  formLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/knowledge/sop/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    formData.title = data.title || ''
    formData.category_id = data.category_id || null
    formData.content = data.content || ''
    formData.tags_input = (data.tags || []).join(', ')
    formData.status = data.status || 'draft'
  } catch (e) {
    ElMessage.error(`加载文档详情失败: ${e.message}`)
    formModalVisible.value = false
  } finally {
    formLoading.value = false
  }
}

const submitForm = async () => {
  if (!formData.title) {
    ElMessage.warning('请输入文档标题')
    return
  }
  if (!formData.category_id) {
    ElMessage.warning('请选择文档分类')
    return
  }
  formLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const tags = formData.tags_input ? formData.tags_input.split(',').map(t => t.trim()).filter(t => t) : []
    const payload = {
      title: formData.title,
      category_id: formData.category_id,
      content: formData.content,
      tags,
      status: formData.status
    }
    const url = isEditing.value ? `/api/v1/knowledge/sop/${editingId.value}` : '/api/v1/knowledge/sop'
    const method = isEditing.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success(isEditing.value ? '文档更新成功' : '文档创建成功')
    formModalVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(`${isEditing.value ? '更新' : '创建'}失败: ${e.message}`)
  } finally {
    formLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除文档「${row.title}」吗？此操作不可恢复。`, '确认删除', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token') || ''
      const res = await fetch(`/api/v1/knowledge/sop/${row.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.error(`删除失败: ${e.message}`)
    }
    }).catch(e => ElMessage.error(`操作失败: ${e.message}`))
}

const submitReview = (row) => {
  ElMessageBox.confirm(`确定要提交文档「${row.title}」进行审核吗？`, '确认提交审核', {
    confirmButtonText: '确认提交',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token') || ''
      const res = await fetch(`/api/v1/knowledge/sop/${row.id}/review`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      ElMessage.success('提交审核成功')
      loadData()
    } catch (e) {
      ElMessage.error(`提交审核失败: ${e.message}`)
    }
    }).catch(e => ElMessage.error(`操作失败: ${e.message}`))
}

const approve = (row) => {
  ElMessageBox.confirm(`确定要让文档「${row.title}」审核通过吗？`, '确认审核通过', {
    confirmButtonText: '确认通过',
    cancelButtonText: '取消',
    type: 'success'
  }).then(async () => {
    try {
      const token = localStorage.getItem('token') || ''
      const res = await fetch(`/api/v1/knowledge/sop/${row.id}/approve`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      ElMessage.success('审核通过')
      loadData()
    } catch (e) {
      ElMessage.error(`审核操作失败: ${e.message}`)
    }
    }).catch(e => ElMessage.error(`操作失败: ${e.message}`))
}

const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  loadData()
}

const showDetail = (row) => {
  currentSOP.value = row
  detailModalVisible.value = true
}

const getStatusType = (status) => {
  const typeMap = { draft: 'info', pending_review: 'warning', approved: '', published: 'success' }
  return typeMap[status] || 'info'
}
</script>

<style lang="scss" scoped>
.mb-4 { margin-bottom: 16px; }
</style>
