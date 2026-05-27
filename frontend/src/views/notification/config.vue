<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>通知渠道配置</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加渠道
          </el-button>
        </div>
      </template>
      <el-table :data="channelList" :loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="props">
            {{ typeMap[props.row.type] || props.row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="props">
            <el-tag :type="props.row.enabled ? 'success' : 'info'" size="small">
              {{ props.row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="props">
            <el-button link type="primary" size="small" @click="handleEdit(props.row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="async () => { await ElMessageBox.confirm('确定删除该记录吗？', '删除确认', { type: 'warning' }); handleDelete(props.row.id); }">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && channelList.length === 0" description="暂无数据" />
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>通知类型</template>
      <el-space direction="vertical" :size="12">
        <el-alert
          v-for="t in notificationTypes"
          :key="t.value"
          :type="getAlertType(t.value)"
          :title="t.label"
          :description="t.description"
          :closable="false"
        />
      </el-space>
    </el-card>

    <el-drawer v-model="drawerVisible" :title="editingChannel && editingChannel.id ? '编辑渠道' : '添加渠道'" size="500px">
      <el-form :model="form" label-position="top" label-width="100">
        <el-form-item label="渠道名称">
          <el-input v-model.trim="form.name" placeholder="如：邮件通知" />
        </el-form-item>
        <el-form-item label="渠道类型">
          <el-select v-model="form.type" placeholder="选择类型" style="width: 100%">
            <el-option label="邮件 (Email)" value="email" />
            <el-option label="钉钉 (DingTalk)" value="dingtalk" />
            <el-option label="飞书 (Feishu)" value="feishu" />
            <el-option label="企业微信" value="wechat_work" />
            <el-option label="Webhook" value="webhook" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置JSON">
          <el-input v-model.trim="form.config" type="textarea" :rows="6" placeholder='{"webhook": "https://..."}' />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const saving = ref(false)
const channelList = ref([])
const notificationTypes = ref([])
const drawerVisible = ref(false)
const editingChannel = ref(null)
const form = reactive({ name: '', type: '', config: '{}', enabled: true })

const typeMap = { email: '邮件', dingtalk: '钉钉', feishu: '飞书', wechat_work: '企业微信', webhook: 'Webhook' }

onMounted(() => { loadChannels(); loadTypes() })

async function loadChannels() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/notifications/channels', { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    channelList.value = data.items || []
  } catch (e) {
    ElMessage.error('加载渠道失败: ' + e.message)
    channelList.value = []
  } finally {
    loading.value = false
  }
}

async function loadTypes() {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/notifications/types', { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    notificationTypes.value = data.types || []
  } catch (e) { ElMessage.error('加载通知类型失败') }
}

function getAlertType(type) {
  return { email: 'info', dingtalk: 'warning', feishu: 'success', wechat_work: 'info', webhook: 'default' }[type] || 'default'
}

function handleAdd() {
  editingChannel.value = null
  Object.assign(form, { name: '', type: '', config: '{}', enabled: true })
  drawerVisible.value = true
}

function handleEdit(row) {
  editingChannel.value = row
  Object.assign(form, { name: row.name, type: row.type, config: JSON.stringify(row.config || {}), enabled: row.enabled })
  drawerVisible.value = true
}

async function handleSave() {
  if (!form.name || !form.type) { ElMessage.warning('请填写名称和类型'); return }
  saving.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const method = editingChannel.value ? 'PUT' : 'POST'
    const url = editingChannel.value ? `/api/v1/notifications/channels/${editingChannel.value.id}` : '/api/v1/notifications/channels'
    const res = await fetch(url, { method, headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ name: form.name, type: form.type, config: JSON.parse(form.config || '{}'), enabled: form.enabled }) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success(editingChannel.value ? '更新成功' : '添加成功')
    drawerVisible.value = false
    loadChannels()
  } catch (e) {
    ElMessage.error('保存失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/notifications/channels/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    ElMessage.success('删除成功')
    loadChannels()
  } catch (e) {
    ElMessage.error('删除失败: ' + e.message)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
