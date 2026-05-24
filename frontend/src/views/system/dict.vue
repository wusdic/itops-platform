<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>字典管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加字典
          </el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索字典名称/编码"
          style="width: 200px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table :data="dictList" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="字典名称" width="180" />
        <el-table-column prop="code" label="字典编码" width="150" />
        <el-table-column prop="description" label="描述" :show-overflow-tooltip="true" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleItems(row)">字典项</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 创建/编辑字典 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" label-position="left">
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入字典名称" />
        </el-form-item>
        <el-form-item label="字典编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入字典编码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 字典项管理 -->
    <el-dialog v-model="itemsDialogVisible" title="字典项管理" width="700px">
      <el-table :data="dictItems" style="width: 100%">
        <el-table-column prop="label" label="标签" min-width="120" />
        <el-table-column prop="value" label="值" min-width="120" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'" size="small">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditItem(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" size="small" @click="handleAddItem">添加字典项</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const searchKeyword = ref('')
const dictList = ref([])
const dialogVisible = ref(false)
const itemsDialogVisible = ref(false)
const dialogTitle = ref('添加字典')
const formRef = ref(null)
const dictItems = ref([])
const currentDictId = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({ id: null, name: '', code: '', description: '', status: '1' })

const rules = {
  name: [{ required: true, message: '请输入字典名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入字典编码', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/admin/dict?page=${pagination.page}&page_size=${pagination.pageSize}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()
    dictList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载字典列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchData() })

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  dialogTitle.value = '添加字典'
  Object.assign(form, { id: null, name: '', code: '', description: '', status: '1' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑字典'
  Object.assign(form, { id: row.id, name: row.name, code: row.code, description: row.description, status: row.status })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除字典 "${row.name}" 吗?`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        const token = localStorage.getItem('token')
        await fetch(`/api/v1/admin/dict/${row.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        ElMessage.success('删除成功')
        fetchData()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

const handleItems = (row) => {
  currentDictId.value = row.id
  dictItems.value = [
    { id: 1, label: '是', value: '1', sort: 1, status: '1' },
    { id: 2, label: '否', value: '0', sort: 2, status: '1' }
  ]
  itemsDialogVisible.value = true
}

const handleAddItem = () => { ElMessage.info('字典项管理功能需后端提供独立 API 接口支持') }
const handleEditItem = (row) => { ElMessage.info(`编辑字典项「${row.label}」（${row.value}）需后端 API 支持`) }
const handleDeleteItem = (row) => { ElMessage.info(`删除字典项「${row.label}」需后端 API 支持`) }

const submitForm = async () => {
  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    const token = localStorage.getItem('token')
    const url = form.id ? `/api/v1/admin/dict/${form.id}` : '/api/v1/admin/dict'
    const method = form.id ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    })

    if (!res.ok) throw new Error('请求失败')

    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; }
.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
