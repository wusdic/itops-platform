<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识分类管理</h1>
        <p class="page-subtitle">管理知识库文档分类</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="handleAddRoot">
          <el-icon><Plus /></el-icon>
          新建根分类
        </el-button>
      </div>
    </div>

    <el-card class="tree-card" v-loading="loading">
      <el-tree
        :data="treeData"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        :expand-on-click-node="false"
        default-expand-all
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span class="node-label">
              <span>{{ node.label }}</span>
              <span class="node-code">({{ data.code }})</span>
            </span>
            <span class="node-actions">
              <el-button link type="primary" size="small" @click.stop="handleAddChild(data)">新增</el-button>
              <el-button link type="primary" size="small" @click.stop="handleEdit(data)">编辑</el-button>
              <el-button link type="danger" size="small" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 添加/编辑分类弹窗 -->
    <el-dialog v-model="modalVisible" :title="isEditing ? '编辑分类' : '新建分类'" width="500px">
      <el-form :model="formData" label-position="top" :rules="formRules" ref="formRef">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model.trim="formData.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入分类编码（英文/数字）" :disabled="isEditing" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="formData.parent_id" placeholder="选择上级分类（不选则为根分类）" clearable style="width: 100%">
            <el-option
              v-for="c in flatCategoryList"
              :key="c.id"
              :label="c.name"
              :value="c.id"
              :disabled="c.id === currentCategory?.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model.trim="formData.sort_order" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="formData.description" type="textarea" placeholder="请输入备注信息" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="modalVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="formLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="deleteModalVisible" title="确认删除" width="400px">
      <el-alert v-if="deleteHasChildren" type="warning" :closable="false" style="margin-bottom: 16px">
        该分类下存在子分类，删除后子分类也将一并删除。
      </el-alert>
      <p>确定要删除分类「{{ currentCategory?.name }}」吗？此操作不可恢复。</p>
      <template #footer>
        <el-button @click="deleteModalVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import knowledge from '@/api/knowledge'

const loading = ref(false)
const formLoading = ref(false)
const deleteLoading = ref(false)

const categoryList = ref([])

const currentCategory = ref(null)
const modalVisible = ref(false)
const isEditing = ref(false)
const formRef = ref(null)
const formData = reactive({
  name: '',
  code: '',
  parent_id: null,
  sort_order: 0,
  description: ''
})

const formRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入分类编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '编码只能包含英文、数字和下划线', trigger: 'blur' }
  ]
}

const deleteModalVisible = ref(false)
const deleteHasChildren = computed(() => {
  return currentCategory.value?.children && currentCategory.value.children.length > 0
})

const flatCategoryList = computed(() => {
  const result = []
  const flatten = (list, depth = 0) => {
    for (const item of list) {
      result.push({ id: item.id, name: item.name, depth, disabled: item.id === currentCategory.value?.id })
      if (item.children && item.children.length > 0) {
        flatten(item.children, depth + 1)
      }
    }
  }
  flatten(categoryList.value)
  return result
})

function listToTree(list, parentId = null) {
  return list
    .filter(item => item.parent_id === parentId)
    .sort((a, b) => a.sort_order - b.sort_order)
    .map(item => ({
      ...item,
      children: item.children || listToTree(list, item.id)
    }))
}

const treeData = computed(() => listToTree(categoryList.value, null))

function handleNodeClick(data) {
  currentCategory.value = data
}

function handleAddRoot() {
  isEditing.value = false
  currentCategory.value = null
  Object.assign(formData, { name: '', code: '', parent_id: null, sort_order: getNextSortOrder(null), description: '' })
  modalVisible.value = true
}

function handleAddChild(node) {
  isEditing.value = false
  currentCategory.value = node
  Object.assign(formData, { name: '', code: '', parent_id: node.id, sort_order: getNextSortOrder(node.id), description: '' })
  modalVisible.value = true
}

function handleEdit(node) {
  isEditing.value = true
  currentCategory.value = node
  Object.assign(formData, { name: node.name, code: node.code, parent_id: node.parent_id, sort_order: node.sort_order, description: node.description || '' })
  modalVisible.value = true
}

function handleDelete(node) {
  currentCategory.value = node
  deleteModalVisible.value = true
}

function getNextSortOrder(parentId) {
  const siblings = categoryList.value.filter(item => item.parent_id === parentId)
  if (siblings.length === 0) return 1
  return Math.max(...siblings.map(s => s.sort_order)) + 1
}

async function loadCategories() {
  loading.value = true
  try {
    const data = await knowledge.category.getList()
    // API returns flat list, need to build tree
    categoryList.value = data.items || data || []
  } catch (e) {
    ElMessage.error('加载分类失败')
    categoryList.value = []
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  try {
    await formRef.value?.validate()
  } catch { return }

  formLoading.value = true
  try {
    if (isEditing.value) {
      await knowledge.category.update(currentCategory.value.id, {
        name: formData.name,
        sort_order: formData.sort_order,
        parent_id: formData.parent_id,
        description: formData.description
      })
      ElMessage.success('分类更新成功')
    } else {
      await knowledge.category.create({
        name: formData.name,
        code: formData.code,
        parent_id: formData.parent_id,
        sort_order: formData.sort_order,
        description: formData.description
      })
      ElMessage.success('分类创建成功')
    }

    modalVisible.value = false
    await loadCategories()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    formLoading.value = false
  }
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    await knowledge.category.delete(currentCategory.value.id)
    ElMessage.success('删除成功')
    deleteModalVisible.value = false
    await loadCategories()
  } catch (error) {
    ElMessage.error(error.message || '删除失败')
  } finally {
    deleteLoading.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.page-container { padding: 24px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title { font-size: 24px; font-weight: 600; margin: 0; }
.page-subtitle { color: #999; margin: 4px 0 0; font-size: 14px; }
.tree-card { background: #fff; }
.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 8px;
}
.node-label { display: flex; align-items: center; gap: 8px; }
.node-code { color: #999; font-size: 12px; }
.node-actions { display: flex; gap: 4px; }
</style>
