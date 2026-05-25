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
      <el-form :model="form" label-position="left" label-width="80" require-asterisk-position="right">
        <el-form-item label="菜单名称" required>
          <el-input v-model="form.label" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单编码" required>
          <el-input v-model="form.key" placeholder="请输入菜单编码，如: system:user" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="菜单路径">
          <el-input v-model="form.path" placeholder="请输入菜单路径，如: /system/user" />
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
          <el-input-number v-model="form.sort" :min="0" :max="9999" style="width: 100%" />
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
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/system/menus', { headers: { Authorization: `Bearer ${token}` } })
    if (res.status === 404) throw new Error('API_NOT_FOUND')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    const list = Array.isArray(data) ? data : (data.data || [])
    const map = {}
    list.forEach(item => { map[item.key] = { ...item, children: [] } })
    list.forEach(item => {
      if (item.parent_key && map[item.parent_key]) map[item.parent_key].children.push(map[item.key])
      else if (!item.parent_key) menuTree.value.push(map[item.key])
    })
  } catch {
    menuTree.value = [
      { key: 'dashboard', label: '仪表盘', iconName: 'DataBoard', path: '/dashboard', sort: 0 },
      { key: 'monitoring', label: '监控中心', iconName: 'Monitor', sort: 1, children: [
        { key: '/monitoring/devices', label: '设备监控', path: '/monitoring/devices', sort: 0 },
        { key: '/monitoring/alerts', label: '告警管理', path: '/monitoring/alerts', sort: 1 },
        { key: '/monitoring/performance', label: '性能监控', path: '/monitoring/performance', sort: 2 },
        { key: '/management/vendor-credentials', label: '厂商账密', path: '/management/vendor-credentials', sort: 3 },
      ]},
      { key: 'workorder', label: '工单管理', iconName: 'Tickets', sort: 2, children: [
        { key: '/workorder/list', label: '工单列表', path: '/workorder/list', sort: 0 },
        { key: '/workorder/create', label: '创建工单', path: '/workorder/create', sort: 1 },
        { key: '/workorder/my', label: '我的工单', path: '/workorder/my', sort: 2 },
      ]},
      { key: 'ai', label: 'AI助手', iconName: 'MagicStick', sort: 4, children: [
        { key: '/ai/chat', label: 'AI聊天', path: '/ai/chat', sort: 0 },
        { key: '/ai/copilot', label: '知识库问答', path: '/ai/copilot', sort: 1 },
        { key: '/ai/analyze', label: '智能分析', path: '/ai/analyze', sort: 2 },
      ]},
      { key: 'automation', label: '自动化', iconName: 'Lightning', sort: 5, children: [
        { key: '/automation/script', label: '脚本管理', path: '/automation/script', sort: 0 },
        { key: '/automation/task', label: '任务调度', path: '/automation/task', sort: 1 },
        { key: '/automation/evaluate', label: '指标评估', path: '/automation/evaluate', sort: 2 },
        { key: '/automation/execute', label: '执行记录', path: '/automation/execute', sort: 3 },
      ]},
      { key: 'backup', label: '备份管理', iconName: 'Document', sort: 6, children: [
        { key: '/backup/list', label: '备份记录', path: '/backup/list', sort: 0 },
        { key: '/backup/restore', label: '恢复管理', path: '/backup/restore', sort: 1 },
      ]},
      { key: 'notification', label: '消息中心', iconName: 'Bell', sort: 7, children: [
        { key: '/notification/message', label: '我的消息', path: '/notification/message', sort: 0 },
        { key: '/notification/history', label: '消息历史', path: '/notification/history', sort: 1 },
        { key: '/notification/config', label: '通知配置', path: '/notification/config', sort: 2 },
      ]},
      { key: 'system', label: '系统管理', iconName: 'Setting', sort: 99, children: [
        { key: '/system/user', label: '用户管理', path: '/system/user', sort: 0 },
        { key: '/system/role', label: '角色管理', path: '/system/role', sort: 1 },
        { key: '/system/menu', label: '菜单管理', path: '/system/menu', sort: 2 },
        { key: '/system/dict', label: '字典管理', path: '/system/dict', sort: 3 },
        { key: '/system/config', label: '参数配置', path: '/system/config', sort: 4 },
        { key: '/system/logs', label: '日志查看', path: '/system/logs', sort: 5 },
        { key: '/system/adapters', label: '适配器管理', path: '/system/adapters', sort: 6 },
      ]},
      { key: 'report', label: '报表管理', iconName: 'TrendCharts', sort: 100, children: [
        { key: '/report/list', label: '报表管理', path: '/report/list', sort: 0 },
        { key: '/report/create', label: '生成报表', path: '/report/create', sort: 1 },
        { key: '/report/template', label: '模板管理', path: '/report/template', sort: 2 },
      ]},
    ]
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
    const token = localStorage.getItem('token') || ''
    const method = isEdit.value ? 'PUT' : 'POST'
    const url = isEdit.value ? `/api/v1/system/menus/${form.key}` : '/api/v1/system/menus'
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify(payload) })
    if (res.status === 404) throw new Error('API_NOT_FOUND')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    drawerVisible.value = false
    loadMenus()
  } catch (e) {
    if (e.message === 'API_NOT_FOUND') {
      if (isEdit.value) {
        const update = (nodes) => { for (const n of nodes) { if (n.key === payload.key) { Object.assign(n, payload); return true } if (n.children && update(n.children)) return true } return false }
        update(menuTree.value)
      } else {
        const newNode = { ...payload, children: [] }
        if (payload.parent_key) {
          const add = (nodes) => { for (const n of nodes) { if (n.key === payload.parent_key) { n.children = n.children || []; n.children.push(newNode); return true } if (n.children && add(n.children)) return true } return false }
          add(menuTree.value)
        } else { menuTree.value.push(newNode) }
      }
      ElMessage.success(isEdit.value ? '更新成功（本地存储）' : '创建成功（本地存储）')
      drawerVisible.value = false
    } else { ElMessage.error(`操作失败: ${e.message}`) }
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
