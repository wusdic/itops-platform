<template>
  <div class="page-container">
    <n-card title="菜单管理" :bordered="false">
      <template #header-extra>
        <n-button type="primary" @click="handleAdd(null)">
          <template #icon><n-icon><AddOutline /></n-icon></template>
          添加菜单
        </n-button>
      </template>

      <n-tree
        block-line
        :data="menuTree"
        :default-expanded-keys="defaultExpandedKeys"
        :selected-keys="selectedKeys"
        key-field="key"
        label-field="label"
        children-field="children"
        @update:selected-keys="handleSelect"
      >
        <template #label="{ label, data }">
          <n-space>
            <n-icon v-if="data.icon"><component :is="data.icon" /></n-icon>
            <span>{{ label }}</span>
            <n-tag v-if="data.type === 'btn'" size="tiny" type="warning">按钮</n-tag>
          </n-space>
        </template>
        <template #suffix="{ data }">
          <n-space size="small">
            <n-button size="tiny" quaternary type="primary" @click.stop="handleAddChild(data)">添加子项</n-button>
            <n-button size="tiny" quaternary type="info" @click.stop="handleEdit(data)">编辑</n-button>
            <n-button size="tiny" quaternary type="error" @click.stop="handleDelete(data)">删除</n-button>
          </n-space>
        </template>
      </n-tree>
    </n-card>

    <!-- 添加/编辑菜单抽屉 -->
    <n-drawer v-model:show="drawerVisible" :width="450" placement="right">
      <n-drawer-content :title="drawerTitle" closable>
        <template #header>
          <n-space justify="space-between" align="center" style="width:100%">
            <span>{{ drawerTitle }}</span>
            <n-button size="small" quaternary @click="drawerVisible = false">取消</n-button>
          </n-space>
        </template>
        <n-form :model="form" label-placement="left" label-width="100" require-mark-placement="right-hanging">
          <n-form-item label="菜单名称" required>
            <n-input v-model:value="form.label" placeholder="请输入菜单名称" />
          </n-form-item>
          <n-form-item label="菜单编码" required>
            <n-input v-model:value="form.key" placeholder="请输入菜单编码，如: system:user" :disabled="isEdit" />
          </n-form-item>
          <n-form-item label="菜单路径">
            <n-input v-model:value="form.path" placeholder="请输入菜单路径，如: /system/user" />
          </n-form-item>
          <n-form-item label="图标">
            <n-select v-model:value="form.iconName" :options="iconOptions" placeholder="选择图标" clearable filterable />
          </n-form-item>
          <n-form-item label="排序">
            <n-input-number v-model:value="form.sort" :min="0" :max="9999" style="width:100%" />
          </n-form-item>
          <n-form-item label="类型">
            <n-radio-group v-model:value="form.type">
              <n-radio value="menu">菜单</n-radio>
              <n-radio value="btn">按钮</n-radio>
            </n-radio-group>
          </n-form-item>
          <n-form-item label="上级菜单" v-if="form.parentKey">
            <n-tag>{{ getMenuLabelByKey(form.parentKey) }}</n-tag>
            <n-button size="small" quaternary style="margin-left:8px" @click="form.parentKey = null">清除</n-button>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="drawerVisible = false">取消</n-button>
            <n-button type="primary" @click="submitForm" :loading="submitting">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { NCard, NButton, NTree, NSpace, NTag, NIcon, NDrawer, NDrawerContent, NForm, NFormItem, NInput, NInputNumber, NSelect, NRadioGroup, NRadio, useMessage, useDialog } from 'naive-ui'
import { AddOutline, GridOutline, ServerOutline, AlertCircleOutline, ConstructOutline, FolderOutline, SettingsOutline, PeopleOutline, KeyOutline, FlashOutline, DocumentTextOutline, HomeOutline, ListOutline, PersonOutline, ShieldOutline, RefreshOutline, CloudOutline, TerminalOutline, CubeOutline, FileTrayOutline, StatsChartOutline, GitBranchOutline, ExtensionPuzzleOutline, LockClosedOutline, EyeOutline, CreateOutline, TrashOutline, AddCircleOutline } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

const menuTree = ref([])
const selectedKeys = ref([])
const drawerVisible = ref(false)
const drawerTitle = ref('添加菜单')
const submitting = ref(false)
const isEdit = ref(false)
const defaultExpandedKeys = ref(['dashboard', 'monitoring', 'workorder', 'ai', 'automation', 'backup', 'notification', 'system', 'report'])

const ICON_MAP = {
  GridOutline, ServerOutline, AlertCircleOutline, ConstructOutline, FolderOutline, SettingsOutline,
  PeopleOutline, KeyOutline, FlashOutline, DocumentTextOutline, HomeOutline, GridOutline, ListOutline,
  PersonOutline, ShieldOutline, RefreshOutline, CloudOutline, TerminalOutline, CubeOutline,
  FileTrayOutline, StatsChartOutline, GitBranchOutline, ExtensionPuzzleOutline, LockClosedOutline,
  EyeOutline, CreateOutline, TrashOutline, AddCircleOutline
}

const iconOptions = Object.keys(ICON_MAP).map(name => ({ label: name.replace(/([A-Z])/g, '_$1').toUpperCase(), value: name }))

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
      { key: 'dashboard', label: '仪表盘', icon: GridOutline, path: '/dashboard', sort: 0 },
      { key: 'monitoring', label: '监控中心', icon: ServerOutline, sort: 1, children: [
        { key: '/monitoring/devices', label: '设备监控', path: '/monitoring/devices', sort: 0 },
        { key: '/monitoring/alerts', label: '告警管理', path: '/monitoring/alerts', sort: 1 },
        { key: '/monitoring/performance', label: '性能监控', path: '/monitoring/performance', sort: 2 },
        { key: '/management/vendor-credentials', label: '厂商账密', path: '/management/vendor-credentials', sort: 3 },
      ]},
      { key: 'workorder', label: '工单管理', icon: ConstructOutline, sort: 2, children: [
        { key: '/workorder/list', label: '工单列表', path: '/workorder/list', sort: 0 },
        { key: '/workorder/create', label: '创建工单', path: '/workorder/create', sort: 1 },
        { key: '/workorder/my', label: '我的工单', path: '/workorder/my', sort: 2 },
      ]},
      { key: 'ai', label: 'AI助手', icon: FlashOutline, sort: 4, children: [
        { key: '/ai/chat', label: 'AI聊天', path: '/ai/chat', sort: 0 },
        { key: '/ai/copilot', label: '知识库问答', path: '/ai/copilot', sort: 1 },
        { key: '/ai/analyze', label: '智能分析', path: '/ai/analyze', sort: 2 },
      ]},
      { key: 'automation', label: '自动化', icon: FlashOutline, sort: 5, children: [
        { key: '/automation/script', label: '脚本管理', path: '/automation/script', sort: 0 },
        { key: '/automation/task', label: '任务调度', path: '/automation/task', sort: 1 },
        { key: '/automation/evaluate', label: '指标评估', path: '/automation/evaluate', sort: 2 },
        { key: '/automation/execute', label: '执行记录', path: '/automation/execute', sort: 3 },
      ]},
      { key: 'backup', label: '备份管理', icon: DocumentTextOutline, sort: 6, children: [
        { key: '/backup/list', label: '备份记录', path: '/backup/list', sort: 0 },
        { key: '/backup/restore', label: '恢复管理', path: '/backup/restore', sort: 1 },
      ]},
      { key: 'notification', label: '消息中心', icon: SettingsOutline, sort: 7, children: [
        { key: '/notification/message', label: '我的消息', path: '/notification/message', sort: 0 },
        { key: '/notification/history', label: '消息历史', path: '/notification/history', sort: 1 },
        { key: '/notification/config', label: '通知配置', path: '/notification/config', sort: 2 },
      ]},
      { key: 'system', label: '系统管理', icon: SettingsOutline, sort: 99, children: [
        { key: '/system/user', label: '用户管理', path: '/system/user', sort: 0 },
        { key: '/system/role', label: '角色管理', path: '/system/role', sort: 1 },
        { key: '/system/menu', label: '菜单管理', path: '/system/menu', sort: 2 },
        { key: '/system/dict', label: '字典管理', path: '/system/dict', sort: 3 },
        { key: '/system/config', label: '参数配置', path: '/system/config', sort: 4 },
        { key: '/system/logs', label: '日志查看', path: '/system/logs', sort: 5 },
        { key: '/system/adapters', label: '适配器管理', path: '/system/adapters', sort: 6 },
      ]},
      { key: 'report', label: '报表管理', icon: DocumentTextOutline, sort: 100, children: [
        { key: '/report/list', label: '报表管理', path: '/report/list', sort: 0 },
        { key: '/report/create', label: '生成报表', path: '/report/create', sort: 1 },
        { key: '/report/template', label: '模板管理', path: '/report/template', sort: 2 },
      ]},
    ]
  }
}

function handleSelect(keys) { selectedKeys.value = keys }

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
  dialog.warning({
    title: '确认删除',
    content: `确定删除菜单"${data.label}"吗？${data.children?.length ? '（将同时删除所有子菜单）' : ''}`,
    positiveText: '确定', negativeText: '取消',
    onPositiveClick: () => {
      const remove = (nodes) => {
        const idx = nodes.findIndex(n => n.key === data.key)
        if (idx !== -1) { nodes.splice(idx, 1); return true }
        for (const node of nodes) { if (node.children && remove(node.children)) return true }
        return false
      }
      remove(menuTree.value)
      message.success('删除成功')
      drawerVisible.value = false
    }
  })
}

async function submitForm() {
  if (!form.label || !form.key) { message.warning('请填写必填项'); return }
  submitting.value = true
  const payload = { key: form.key, label: form.label, path: form.path || '', icon: form.iconName ? ICON_MAP[form.iconName] : null, iconName: form.iconName, sort: form.sort, type: form.type, parent_key: form.parentKey }
  try {
    const token = localStorage.getItem('token') || ''
    const method = isEdit.value ? 'PUT' : 'POST'
    const url = isEdit.value ? `/api/v1/system/menus/${form.key}` : '/api/v1/system/menus'
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify(payload) })
    if (res.status === 404) throw new Error('API_NOT_FOUND')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    message.success(isEdit.value ? '更新成功' : '创建成功')
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
      message.success(isEdit.value ? '更新成功（本地存储）' : '创建成功（本地存储）')
      drawerVisible.value = false
    } else { message.error(`操作失败: ${e.message}`) }
  } finally { submitting.value = false }
}

onMounted(loadMenus)
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
