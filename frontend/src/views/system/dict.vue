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
          v-model.trim="searchKeyword"
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
      <el-empty v-if="!loading && dictList.length === 0" description="暂无数据" />

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
          <el-input v-model.trim="form.name" placeholder="请输入字典名称" />
        </el-form-item>
        <el-form-item label="字典编码" prop="code">
          <el-input v-model.trim="form.code" placeholder="请输入字典编码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
      <el-table :data="dictItems" style="width: 100%" v-loading="itemsLoading">
        <el-table-column prop="label" label="标签" min-width="120" />
        <el-table-column prop="value" label="值" min-width="120" />
        <el-table-column prop="sort_order" label="排序" width="80">
          <template #default="{ row }">{{ row.sort_order || row.sort || 0 }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="(row.status === '1' || row.status === 'active') ? 'success' : 'danger'" size="small">
              {{ (row.status === '1' || row.status === 'active') ? '启用' : '禁用' }}
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
      <el-empty v-if="!loading && dictItems.length === 0" description="暂无字典项" />
      <template #footer>
        <el-button type="primary" size="small" @click="handleAddItem">添加字典项</el-button>
      </template>
    </el-dialog>

    <!-- 字典项编辑弹窗 -->
    <el-dialog v-model="itemDialogVisible" :title="currentEditingItem.id ? '编辑字典项' : '添加字典项'" width="400px">
      <el-form :model="currentEditingItem" label-width="80px" label-position="left">
        <el-form-item label="标签" required>
          <el-input v-model.trim="currentEditingItem.label" placeholder="请输入显示标签" />
        </el-form-item>
        <el-form-item label="值" required>
          <el-input v-model.trim="currentEditingItem.value" placeholder="请输入字典值" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model.trim="currentEditingItem.sort_order" :min="0" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="currentEditingItem.status" style="width: 100%">
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitItemForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const itemsLoading = ref(false)
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

// 字典项管理
const handleItems = async (row) => {
  currentDictId.value = row.id
  itemsDialogVisible.value = true
  itemsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/admin/dict/all-items?type_id=${row.id}&page=1&page_size=100`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()
    dictItems.value = (data.items || []).map(item => ({
      ...item,
      status: item.status === 'active' ? '1' : '0'
    }))
  } catch (error) {
    ElMessage.error('加载字典项失败')
    dictItems.value = []
  } finally {
    itemsLoading.value = false
  }
}

const handleAddItem = () => {
  currentEditingItem.value = { id: null, label: '', value: '', sort_order: 0, status: '1' }
  itemDialogVisible.value = true
}

const handleEditItem = (row) => {
  currentEditingItem.value = { ...row }
  itemDialogVisible.value = true
}

const handleDeleteItem = (row) => {
  ElMessageBox.confirm(`确定删除字典项「${row.label}」吗?`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        const token = localStorage.getItem('token')
        const res = await fetch(`/api/v1/admin/dict/items/${row.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('删除失败')
        ElMessage.success('删除成功')
        handleItems({ id: currentDictId.value })
      } catch (error) {
        ElMessage.error('删除失败')
      }
    }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

const itemDialogVisible = ref(false)
const currentEditingItem = ref({ id: null, label: '', value: '', sort: 0, status: '1' })

const submitItemForm = async () => {
  if (!currentEditingItem.value.label || !currentEditingItem.value.value) {
    ElMessage.warning('请填写标签和值')
    return
  }
  try {
    const token = localStorage.getItem('token')
    const payload = {
      type_id: currentDictId.value,
      label: currentEditingItem.value.label,
      value: currentEditingItem.value.value,
      sort_order: currentEditingItem.value.sort || 0,
      status: currentEditingItem.value.status === '1' ? 'active' : 'inactive'
    }
    const url = currentEditingItem.value.id
      ? `/api/v1/admin/dict/items/${currentEditingItem.value.id}`
      : '/api/v1/admin/dict/all-items'
    const method = currentEditingItem.value.id ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('操作失败')
    ElMessage.success(currentEditingItem.value.id ? '更新成功' : '创建成功')
    itemDialogVisible.value = false
    handleItems({ id: currentDictId.value })
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

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
