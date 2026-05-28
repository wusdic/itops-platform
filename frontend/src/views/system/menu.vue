<template>
  <div class="page-container">
    <el-card class="menu-card">
      <template #header>
        <div class="card-header">
          <span>菜单管理</span>
          <el-button type="primary" @click="handleAdd(null)">
            <el-icon><Plus /></el-icon>
            添加菜单
          </el-button>
        </div>
      </template>

      <el-tree
        :data="menuTree"
        :default-expand-all="false"
        :expand-on-click-node="false"
        node-key="key"
        :props="{ label: 'label', children: 'children' }"
        @node-click="handleNodeClick"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <span class="node-label">
              <el-icon v-if="data.icon"><component :is="getIconComponent(data.iconName)" /></el-icon>
              <span>{{ data.label }}</span>
              <el-tag v-if="data.type === 'btn'" type="warning" size="small">按钮</el-tag>
            </span>
            <span class="node-actions">
              <el-button size="small" link type="primary" @click.stop="handleAddChild(data)">添加子项</el-button>
              <el-button size="small" link type="info" @click.stop="handleEdit(data)">编辑</el-button>
              <el-button size="small" link type="danger" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 添加/编辑菜单抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="drawerTitle"
      direction="rtl"
      size="450px"
      :show-close="false"
      class="menu-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <span>{{ drawerTitle }}</span>
          <el-button size="small" link @click="drawerVisible = false">取消</el-button>
        </div>
      </template>
      <el-form :model="form" label-position="top" label-width="80" require-asterisk-position="right">
        <el-form-item label="菜单名称" required>
          <el-input v-model.trim="form.label" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单编码" required>
          <el-input v-model="form.key" placeholder="请输入菜单编码，如: system:user" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="菜单路径">
          <el-input v-model.trim="form.path" placeholder="请输入菜单路径，如: /system/user" />
        </el-form-item>
        <el-form-item label="图标">
          <el-select v-model="form.iconName" placeholder="选择图标" clearable filterable style="width: 100%">
            <el-option
              v-for="icon in iconOptions"
              :key="icon.value"
              :label="icon.label"
              :value="icon.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model.trim="form.sort" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.type">
            <el-radio value="menu">菜单</el-radio>
            <el-radio value="btn">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="上级菜单" v-if="form.parentKey">
          <el-tag>{{ getMenuLabelByKey(form.parentKey) }}</el-tag>
          <el-button size="small" link style="margin-left: 8px" @click="form.parentKey = null">清除</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="text-align: right;">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, shallowRef } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, Monitor, Warning, Folder, Setting, User, Key, Lock,
  Lightning, Document, House, List, Refresh, Cloudy, Box, TrendCharts,
  Connection, Operation, View, Delete, Plus, CirclePlus, CircleClose,
  Tickets, MagicStick, Coin, Ticket, Bell, DataBoard, Upload, Search,
  Check, RefreshRight, Finished, Timer, FolderChecked, Reading,
  DataAnalysis, Cpu, Aim, Histogram, PieChart, Compass
} from '@element-plus/icons-vue'
import { menu as menuApi } from '@/api'

const ICON_MAP = {
  Grid, Monitor, Warning, Folder, Setting, User, Key, Lock,
  Lightning, Document, House, List, Refresh, Cloudy, Box, TrendCharts,
  Connection, Operation, View, Delete, Plus, CirclePlus, CircleClose,
  Tickets, MagicStick, Coin, Ticket, Bell, DataBoard, Upload, Search,
  Check, RefreshRight, Finished, Timer, FolderChecked, Reading,
  DataAnalysis, Cpu, Aim, Histogram, PieChart, Compass
}

function getIconComponent(iconName) {
  if (!iconName) return null
  return ICON_MAP[iconName] || null
}

const iconOptions = Object.keys(ICON_MAP).map(name => ({
  label: name,
  value: name
}))

const menuTree = ref([])
const drawerVisible = ref(false)
const drawerTitle = ref('添加菜单')
const submitting = ref(false)
const isEdit = ref(false)

const form = reactive({
  key: '', label: '', path: '', iconName: null, icon: null, sort: 0, type: 'menu', parentKey: null
})

function getMenuLabelByKey(key) {
  const find = (items) => {
    for (const item of items) {
      if (item.key === key) return item.label
      if (item.children) { const f = find(item.children); if (f) return f }
    }
    return null
  }
  return find(menuTree.value) || key
}

async function loadMenus() {
  try {
    const data = await menuApi.getList()
    const list = Array.isArray(data) ? data : (data.items || [])
    const map = {}
    list.forEach(item => { map[item.key] = { ...item, children: [] } })
    list.forEach(item => {
      if (item.parent_key && map[item.parent_key]) map[item.parent_key].children.push(map[item.key])
      else if (!item.parent_key) menuTree.value.push(map[item.key])
    })
  } catch {
    ElMessage.error('加载菜单失败，请检查网络')
  }
}

function handleNodeClick(data) {}

function handleAdd(parent) {
  isEdit.value = false; drawerTitle.value = '添加菜单'
  Object.assign(form, { key: '', label: '', path: '', iconName: null, icon: null, sort: 0, type: 'menu', parentKey: parent?.key || null })
  drawerVisible.value = true
}

function handleAddChild(parent) { handleAdd(parent) }

function handleEdit(data) {
  isEdit.value = true; drawerTitle.value = '编辑菜单'
  Object.assign(form, { key: data.key, label: data.label, path: data.path || '', iconName: data.iconName || null, icon: data.icon || null, sort: data.sort ?? 0, type: data.type || 'menu', parentKey: data.parent_key || null })
  drawerVisible.value = true
}

function handleDelete(data) {
  ElMessageBox.confirm(
    `确定删除菜单"${data.label}"吗？${data.children?.length ? '（将同时删除所有子菜单）' : ''}`,
    '确认删除',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    const remove = (nodes) => {
      const idx = nodes.findIndex(n => n.key === data.key)
      if (idx !== -1) { nodes.splice(idx, 1); return true }
      for (const node of nodes) { if (node.children && remove(node.children)) return true }
      return false
    }
    remove(menuTree.value)
    ElMessage.success('删除成功')
    drawerVisible.value = false
  }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

async function submitForm() {
  if (!form.label || !form.key) { ElMessage.warning('请填写必填项'); return }
  submitting.value = true
  const payload = {
    key: form.key, label: form.label, path: form.path || '',
    icon: form.iconName ? ICON_MAP[form.iconName] : null,
    iconName: form.iconName, sort: form.sort, type: form.type, parent_key: form.parentKey
  }
  try {
    if (isEdit.value) {
      await menuApi.update(form.key, payload)
    } else {
      await menuApi.create(payload)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    drawerVisible.value = false
    loadMenus()
  } catch (e) {
    ElMessage.error(`操作失败: ${e.message || e}`)
  } finally { submitting.value = false }
}

onMounted(loadMenus)
</script>

<style scoped>
.page-container { padding: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.tree-node { display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 8px; }
.node-label { display: flex; align-items: center; gap: 8px; }
.node-actions { display: flex; gap: 4px; }
.menu-drawer :deep(.el-drawer__header) { margin-bottom: 0; padding: 12px 16px; border-bottom: 1px solid #ebeef5; }
</style>
