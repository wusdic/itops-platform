<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识分类管理</h1>
        <p class="page-subtitle">管理知识库文档分类</p>
      </div>
      <div class="page-actions">
        <n-button type="primary" @click="handleAddRoot">
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          新建根分类
        </n-button>
      </div>
    </div>

    <n-card class="tree-card">
      <n-spin :show="loading">
        <n-tree
          block-line
          expand-on-click
          :data="treeData"
          :expanded-keys="expandedKeys"
          :selected-keys="selectedKeys"
          :render-suffix="renderSuffix"
          :render-label="renderLabel"
          @update:expanded-keys="handleExpand"
          @update:selected-keys="handleSelect"
        />
      </n-spin>
    </n-card>

    <!-- 添加/编辑分类弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      preset="card"
      :title="isEditing ? '编辑分类' : '新建分类'"
      style="width: 500px"
    >
      <n-form :model="formData" label-placement="top" :rules="formRules" ref="formRef">
        <n-form-item label="分类名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入分类名称" />
        </n-form-item>
        <n-form-item label="分类编码" path="code">
          <n-input v-model:value="formData.code" placeholder="请输入分类编码（英文/数字）" :disabled="isEditing" />
        </n-form-item>
        <n-form-item label="上级分类">
          <n-tree-select
            v-model:value="formData.parent_id"
            :options="categoryOptions"
            placeholder="选择上级分类（不选则为根分类）"
            clearable
            :render-label="renderTreeSelectLabel"
          />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="formData.sort_order" :min="0" :max="9999" style="width: 100%" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="formData.description" type="textarea" placeholder="请输入备注信息" :rows="3" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" @click="submitForm" :loading="formLoading">确定</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal
      v-model:show="deleteModalVisible"
      preset="card"
      title="确认删除"
      style="width: 400px"
    >
      <n-alert type="warning" v-if="deleteHasChildren" style="margin-bottom: 16px">
        该分类下存在子分类，删除后子分类也将一并删除。
      </n-alert>
      <p>确定要删除分类「{{ currentCategory?.name }}」吗？此操作不可恢复。</p>
      <template #footer>
        <n-space justify="end">
          <n-button @click="deleteModalVisible = false">取消</n-button>
          <n-button type="error" @click="confirmDelete" :loading="deleteLoading">删除</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, h } from 'vue'
import { NIcon, useMessage, useDialog } from 'naive-ui'
import { Add, CreateOutline, TrashOutline, PencilOutline } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const formLoading = ref(false)
const deleteLoading = ref(false)

// 分类数据（模拟）
const categoryList = ref([
  { id: 1, name: '系统运维', code: 'ops', parent_id: null, sort_order: 1, description: '系统运维相关文档', children: [
    { id: 11, name: '服务器管理', code: 'server', parent_id: 1, sort_order: 11, description: '服务器日常管理' },
    { id: 12, name: '网络配置', code: 'network', parent_id: 1, sort_order: 12, description: '网络设备配置' }
  ]},
  { id: 2, name: '故障处理', code: 'fault', parent_id: null, sort_order: 2, description: '故障处理流程和记录', children: [
    { id: 21, name: '紧急故障', code: 'critical', parent_id: 2, sort_order: 21, description: 'P0/P1级故障' },
    { id: 22, name: '一般故障', code: 'normal', parent_id: 2, sort_order: 22, description: 'P2/P3级故障' }
  ]},
  { id: 3, name: '安全规范', code: 'security', parent_id: null, sort_order: 3, description: '安全相关规范文档' },
  { id: 4, name: '操作手册', code: 'manual', parent_id: null, sort_order: 4, description: '各类操作手册' }
])

// 树形相关
const expandedKeys = ref([1, 2])
const selectedKeys = ref([])
const currentCategory = ref(null)

// 弹窗状态
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

// 删除弹窗
const deleteModalVisible = ref(false)
const deleteHasChildren = computed(() => {
  if (!currentCategory.value) return false
  const findCategory = (list) => {
    for (const item of list) {
      if (item.id === currentCategory.value.id) return true
      if (item.children && findCategory(item.children)) return true
    }
    return false
  }
  return currentCategory.value.children && currentCategory.value.children.length > 0
})

// 将平铺数据转为树形
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

// 分类选择器选项（扁平化树）
const categoryOptions = computed(() => {
  const flatten = (list, depth = 0) => {
    return list.reduce((acc, item) => {
      acc.push({ label: item.name, value: item.id, depth, disabled: item.id === currentCategory.value?.id })
      if (item.children && item.children.length > 0) {
        acc.push(...flatten(item.children, depth + 1))
      }
      return acc
    }, [])
  }
  return flatten(categoryList.value)
})

// 渲染树节点标签
function renderLabel({ option }) {
  return h('span', { style: 'display: flex; align-items: center; gap: 8px' }, [
    h('span', null, option.name),
    h('span', { style: 'color: #999; font-size: 12px' }, `(${option.code})`)
  ])
}

// 渲染树选择器标签
function renderTreeSelectLabel({ option }) {
  return h('span', { style: 'padding-left: ' + (option.depth * 16) + 'px' }, option.label)
}

// 渲染操作按钮
function renderSuffix({ option }) {
  return h('div', { style: 'display: flex; gap: 4px; margin-left: auto' }, [
    h('n-button', {
      text: true,
      size: 'tiny',
      onClick: (e) => { e.stopPropagation(); handleAddChild(option) }
    }, () => h(NIcon, null, () => h(CreateOutline))),
    h('n-button', {
      text: true,
      size: 'tiny',
      type: 'primary',
      onClick: (e) => { e.stopPropagation(); handleEdit(option) }
    }, () => h(NIcon, null, () => h(PencilOutline))),
    h('n-button', {
      text: true,
      size: 'tiny',
      type: 'error',
      onClick: (e) => { e.stopPropagation(); handleDelete(option) }
    }, () => h(NIcon, null, () => h(TrashOutline)))
  ])
}

// 事件处理
function handleExpand(keys) {
  expandedKeys.value = keys
}

function handleSelect(keys) {
  selectedKeys.value = keys
}

function handleAddRoot() {
  isEditing.value = false
  currentCategory.value = null
  formData.name = ''
  formData.code = ''
  formData.parent_id = null
  formData.sort_order = getNextSortOrder(null)
  formData.description = ''
  modalVisible.value = true
}

function handleAddChild(node) {
  isEditing.value = false
  currentCategory.value = node
  formData.name = ''
  formData.code = ''
  formData.parent_id = node.id
  formData.sort_order = getNextSortOrder(node.id)
  formData.description = ''
  modalVisible.value = true
}

function handleEdit(node) {
  isEditing.value = true
  currentCategory.value = node
  formData.name = node.name
  formData.code = node.code
  formData.parent_id = node.parent_id
  formData.sort_order = node.sort_order
  formData.description = node.description || ''
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

// 扁平查找分类
function findCategory(list, id) {
  for (const item of list) {
    if (item.id === id) return item
    if (item.children) {
      const found = findCategory(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 扁平查找所有分类（包含children）
function flattenCategories(list) {
  const result = []
  for (const item of list) {
    result.push(item)
    if (item.children) {
      result.push(...flattenCategories(item.children))
    }
  }
  return result
}

async function submitForm() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  formLoading.value = true
  try {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 300))

    if (isEditing.value) {
      // 编辑
      const category = findCategory(categoryList.value, currentCategory.value.id)
      if (category) {
        category.name = formData.name
        category.description = formData.description
        category.sort_order = formData.sort_order
        category.parent_id = formData.parent_id
      }
      message.success('分类更新成功')
    } else {
      // 新建
      const newCategory = {
        id: Date.now(),
        name: formData.name,
        code: formData.code,
        parent_id: formData.parent_id,
        sort_order: formData.sort_order,
        description: formData.description,
        children: []
      }

      if (formData.parent_id) {
        const parent = findCategory(categoryList.value, formData.parent_id)
        if (parent) {
          if (!parent.children) parent.children = []
          parent.children.push(newCategory)
        }
      } else {
        categoryList.value.push(newCategory)
      }

      // 如果新建的是根分类且有展开状态，自动展开
      if (!formData.parent_id) {
        expandedKeys.value.push(newCategory.id)
      }

      message.success('分类创建成功')
    }

    modalVisible.value = false
  } catch (error) {
    message.error('操作失败')
  } finally {
    formLoading.value = false
  }
}

async function confirmDelete() {
  deleteLoading.value = true
  try {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 300))

    const deleteRecursive = (list, id) => {
      const index = list.findIndex(item => item.id === id)
      if (index !== -1) {
        list.splice(index, 1)
        return true
      }
      for (const item of list) {
        if (item.children && deleteRecursive(item.children, id)) {
          return true
        }
      }
      return false
    }

    deleteRecursive(categoryList.value, currentCategory.value.id)
    selectedKeys.value = []
    message.success('删除成功')
    deleteModalVisible.value = false
  } catch (error) {
    message.error('删除失败')
  } finally {
    deleteLoading.value = false
  }
}

onMounted(() => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 200)
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.page-subtitle {
  color: #999;
  margin: 4px 0 0;
  font-size: 14px;
}

.tree-card {
  background: #fff;
}
</style>
