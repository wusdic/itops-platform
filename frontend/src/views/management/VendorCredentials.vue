<template>
  <div class="vendor-credentials-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📋 厂商账密配置</h2>
      <p class="subtitle">查看和管理网络设备厂商指纹及默认登录凭据，支持搜索、新增、编辑、删除</p>
    </div>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" class="main-grid">
      <!-- 左侧：厂商列表 -->
      <n-gi :span="1" class="vendor-list-panel">
        <n-card title="🏢 厂商列表" size="small">
          <template #header-extra>
            <n-tag type="info" size="small">{{ filteredVendors.length }} 个</n-tag>
          </template>

          <!-- 搜索框 -->
          <n-input
            v-model:value="searchText"
            placeholder="搜索厂商..."
            clearable
            size="small"
            class="search-input"
          >
            <template #prefix>
              <n-icon><SearchIcon /></n-icon>
            </template>
          </n-input>

          <!-- 分类筛选 -->
          <n-select
            v-model:value="selectedCategory"
            :options="categoryOptions"
            placeholder="按分类筛选"
            clearable
            size="small"
            class="category-select"
          />

          <!-- 厂商列表 -->
          <div class="vendor-list">
            <div
              v-for="vendor in filteredVendors"
              :key="vendor.name"
              :class="['vendor-item', { active: selectedVendor?.name === vendor.name }]"
              @click="selectVendor(vendor)"
            >
              <div class="vendor-item-header">
                <n-tag size="tiny" :type="categoryColor(vendor.category)">{{ vendor.category }}</n-tag>
                <span class="vendor-name">{{ vendor.name }}</span>
              </div>
              <div class="vendor-item-meta">
                <span>🔑 {{ vendor.credential_count }} 个账密</span>
                <span>🔍 {{ vendor.fingerprint_count }} 个指纹</span>
              </div>
            </div>
            <n-empty v-if="filteredVendors.length === 0" description="未找到匹配厂商" />
          </div>
        </n-card>
      </n-gi>

      <!-- 右侧：厂商详情 -->
      <n-gi :span="3" class="vendor-detail-panel">
        <n-card v-if="selectedVendor" :title="`${selectedVendor.name} - 详细信息`" size="small">
          <template #header-extra>
            <n-space>
              <n-button size="small" @click="editMode = !editMode">
                <template #icon><n-icon><EditIcon /></n-icon></template>
                {{ editMode ? '取消编辑' : '编辑' }}
              </n-button>
              <n-button size="small" type="error" @click="handleDelete">
                <template #icon><n-icon><DeleteIcon /></n-icon></template>
                删除
              </n-button>
            </n-space>
          </template>

          <n-tabs type="line" size="small">
            <!-- 基本信息 -->
            <n-tab-pane name="basic" tab="📄 基本信息">
              <n-descriptions :column="2" label-placement="left" size="small">
                <n-descriptions-item label="厂商名称">{{ selectedVendor.name }}</n-descriptions-item>
                <n-descriptions-item label="简称">{{ selectedVendor.short_name }}</n-descriptions-item>
                <n-descriptions-item label="分类">
                  <n-tag size="tiny" :type="categoryColor(selectedVendor.category)">{{ selectedVendor.category }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item label="官网">
                  <a :href="selectedVendor.homepage" target="_blank" v-if="selectedVendor.homepage">
                    {{ selectedVendor.homepage }}
                  </a>
                  <span v-else>-</span>
                </n-descriptions-item>
                <n-descriptions-item label="描述" :span="2">{{ selectedVendor.description || '-' }}</n-descriptions-item>
                <n-descriptions-item label="建议协议">{{ selectedVendor.suggested_protocols?.join(', ') || '-' }}</n-descriptions-item>
                <n-descriptions-item label="探测端口">{{ selectedVendor.probe_ports?.join(', ') || '-' }}</n-descriptions-item>
              </n-descriptions>
            </n-tab-pane>

            <!-- 指纹模式 -->
            <n-tab-pane name="fingerprints" tab="🔍 指纹模式">
              <n-space vertical>
                <div v-for="(fp, idx) in selectedVendor.fingerprints" :key="idx" class="fingerprint-item">
                  <n-tag :type="fpTypeColor(fp.type)" size="small">{{ fp.type }}</n-tag>
                  <code class="fp-pattern">{{ fp.pattern || fp.oid_prefix }}</code>
                  <n-tag size="tiny" type="info">权重: {{ fp.weight }}</n-tag>
                </div>
                <n-empty v-if="!selectedVendor.fingerprints?.length" description="暂无指纹模式" />
              </n-space>
            </n-tab-pane>

            <!-- 默认账密 -->
            <n-tab-pane name="credentials" tab="🔑 默认账密">
              <n-table :bordered="false" size="small">
                <thead>
                  <tr>
                    <th>协议</th>
                    <th>用户名</th>
                    <th>密码</th>
                    <th>说明</th>
                    <th>优先级</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(cred, idx) in selectedVendor.default_credentials" :key="idx">
                    <td><n-tag size="tiny">{{ cred.protocol }}</n-tag></td>
                    <td><code>{{ cred.username || '-' }}</code></td>
                    <td><code>{{ cred.password || (cred.community ? `community: ${cred.community}` : '-') }}</code></td>
                    <td><span class="cred-notes">{{ cred.notes || '-' }}</span></td>
                    <td><n-tag size="tiny" type="warning">{{ cred.priority }}</n-tag></td>
                  </tr>
                </tbody>
              </n-table>
              <n-empty v-if="!selectedVendor.default_credentials?.length" description="暂无默认账密" />
            </n-tab-pane>
          </n-tabs>

          <!-- 编辑模式 -->
          <div v-if="editMode" class="edit-form">
            <n-divider>编辑模式</n-divider>
            <n-form :model="editForm" label-placement="left" label-width="100">
              <n-form-item label="厂商名称">
                <n-input v-model:value="editForm.name" />
              </n-form-item>
              <n-form-item label="简称">
                <n-input v-model:value="editForm.short_name" />
              </n-form-item>
              <n-form-item label="分类">
                <n-select v-model:value="editForm.category" :options="categoryOptions" />
              </n-form-item>
              <n-form-item label="官网">
                <n-input v-model:value="editForm.homepage" />
              </n-form-item>
              <n-form-item label="描述">
                <n-input v-model:value="editForm.description" type="textarea" />
              </n-form-item>
              <n-form-item label="建议协议">
                <n-dynamic-tags v-model:value="editForm.suggested_protocols" />
              </n-form-item>
              <n-form-item label="探测端口">
                <n-select v-model:value="editForm.probe_ports" multiple :options="portOptions" />
              </n-form-item>
            </n-form>
            <n-space>
              <n-button type="primary" @click="handleSave" :loading="saving">保存</n-button>
              <n-button @click="editMode = false">取消</n-button>
            </n-space>
          </div>
        </n-card>

        <!-- 无选中 -->
        <n-card v-else class="empty-detail">
          <n-empty description="从左侧选择一个厂商查看详情">
            <template #extra>
              <n-button size="small" type="primary" @click="startAddNew">
                <template #icon><n-icon><PlusIcon /></n-icon></template>
                新增厂商
              </n-button>
            </template>
          </n-empty>
        </n-card>

        <!-- 新增厂商 -->
        <n-card v-if="addingNew" :title="'➕ 新增厂商'" size="small" class="add-form-card">
          <n-form :model="addForm" label-placement="left" label-width="120">
            <n-form-item label="厂商名称" required>
              <n-input v-model:value="addForm.name" placeholder="例如：Cisco Systems" />
            </n-form-item>
            <n-form-item label="简称" required>
              <n-input v-model:value="addForm.short_name" placeholder="例如：Cisco" />
            </n-form-item>
            <n-form-item label="分类" required>
              <n-select v-model:value="addForm.category" :options="categoryOptions" placeholder="选择分类" />
            </n-form-item>
            <n-form-item label="官网">
              <n-input v-model:value="addForm.homepage" placeholder="https://..." />
            </n-form-item>
            <n-form-item label="描述">
              <n-input v-model:value="addForm.description" type="textarea" />
            </n-form-item>
            <n-form-item label="建议协议">
              <n-select v-model:value="addForm.suggested_protocols" multiple :options="protocolOptions" />
            </n-form-item>
            <n-form-item label="探测端口">
              <n-select v-model:value="addForm.probe_ports" multiple :options="portOptions" />
            </n-form-item>
          </n-form>
          <n-space class="add-form-actions">
            <n-button type="primary" @click="handleAdd" :loading="saving">创建</n-button>
            <n-button @click="addingNew = false">取消</n-button>
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  NGrid, NGi, NCard, NInput, NSelect, NButton, NIcon, NTag,
  NTabs, NTabPane, NDescriptions, NDescriptionsItem, NSpace,
  NEmpty, NTable, NDivider, NForm, NFormItem, NDynamicTags,
  useMessage, useDialog,
} from 'naive-ui'
import { SearchOutline as SearchIcon, AddOutline as PlusIcon } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

// 数据
const vendors = ref([])
const selectedVendor = ref(null)
const searchText = ref('')
const selectedCategory = ref(null)
const editMode = ref(false)
const addingNew = ref(false)
const saving = ref(false)

// 表单
const editForm = ref({})
const addForm = ref({
  name: '',
  short_name: '',
  category: '',
  homepage: '',
  description: '',
  fingerprints: [],
  default_credentials: [],
  suggested_protocols: [],
  probe_ports: [],
})

// 选项
const categoryOptions = [
  { label: '交换机 (switch)', value: 'switch' },
  { label: '路由器 (router)', value: 'router' },
  { label: '防火墙 (firewall)', value: 'firewall' },
  { label: '服务器 (server)', value: 'server' },
  { label: '无线AP (wireless)', value: 'wireless' },
  { label: 'UPS电源 (ups)', value: 'ups' },
  { label: '存储/NAS (storage)', value: 'storage' },
  { label: '摄像头 (camera)', value: 'camera' },
  { label: '打印机 (printer)', value: 'printer' },
  { label: '负载均衡 (loadbalancer)', value: 'loadbalancer' },
  { label: '入侵检测 (ids_ips)', value: 'ids_ips' },
  { label: '虚拟化 (virtualization)', value: 'virtualization' },
  { label: '云平台 (cloud)', value: 'cloud' },
  { label: '物联网 (iot)', value: 'iot' },
  { label: '其他 (other)', value: 'other' },
]

const protocolOptions = [
  { label: 'SSH', value: 'ssh' },
  { label: 'SNMP v2c', value: 'snmp_v2c' },
  { label: 'HTTP', value: 'http' },
  { label: 'HTTPS', value: 'https' },
  { label: 'Telnet', value: 'telnet' },
  { label: 'RTSP', value: 'rtsp' },
  { label: 'WinRM', value: 'winrm' },
  { label: 'RDP', value: 'rdp' },
  { label: 'IPMI', value: 'ipmi' },
  { label: 'Redfish', value: 'redfish' },
  { label: 'SNMP v3', value: 'snmp_v3' },
  { label: 'iDRAC', value: 'idrac' },
  { label: 'vSphere/VMware', value: 'vmware-api' },
]

const portOptions = Array.from({ length: 20 }, (_, i) => ({
  label: String(i * 10 + 10),
  value: i * 10 + 10,
}))

// 计算属性
const filteredVendors = computed(() => {
  let list = vendors.value
  if (selectedCategory.value) {
    list = list.filter(v => v.category === selectedCategory.value)
  }
  if (searchText.value) {
    const s = searchText.value.toLowerCase()
    list = list.filter(v => v.name.toLowerCase().includes(s) || v.short_name.toLowerCase().includes(s))
  }
  return list
})

// 方法
function categoryColor(cat) {
  const colors = {
    switch: 'success', router: 'warning', firewall: 'error',
    server: 'info', wireless: 'success', ups: 'warning',
    storage: 'default', camera: 'error', printer: 'default',
    loadbalancer: 'info', virtualization: 'info', cloud: 'success',
    iot: 'warning', other: 'default',
  }
  return colors[cat] || 'default'
}

function fpTypeColor(type) {
  const colors = {
    ssh_banner: 'success', http_header: 'info', snmp_sysObjectID: 'warning',
    snmp_sysDesc: 'warning', dns_reverse: 'default',
  }
  return colors[type] || 'default'
}

async function loadVendors() {
  try {
    const res = await fetch('/api/v1/credentials/vendors')
    const data = await res.json()
    vendors.value = data.items || []
  } catch (e) {
    message.error('加载厂商列表失败: ' + e.message)
  }
}

async function loadCategories() {
  try {
    const res = await fetch('/api/v1/credentials/vendors/categories')
    const data = await res.json()
    // categories already loaded
  } catch (e) {
    // load categories failed silently
  }
}

async function selectVendor(vendor) {
  try {
    const res = await fetch(`/api/v1/credentials/vendors/${encodeURIComponent(vendor.name)}`)
    if (!res.ok) throw new Error('加载失败')
    selectedVendor.value = await res.json()
    editMode.value = false
    addingNew.value = false
    // 初始化编辑表单
    editForm.value = { ...selectedVendor.value }
  } catch (e) {
    message.error('加载厂商详情失败: ' + e.message)
  }
}

function startAddNew() {
  addingNew.value = true
  editMode.value = false
  selectedVendor.value = null
  addForm.value = {
    name: '', short_name: '', category: '', homepage: '',
    description: '', fingerprints: [], default_credentials: [],
    suggested_protocols: [], probe_ports: [],
  }
}

async function handleAdd() {
  if (!addForm.value.name || !addForm.value.short_name || !addForm.value.category) {
    message.warning('请填写必填项')
    return
  }
  saving.value = true
  try {
    const res = await fetch('/api/v1/credentials/vendors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(addForm.value),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '创建失败')
    }
    message.success('创建成功')
    addingNew.value = false
    await loadVendors()
  } catch (e) {
    message.error('创建失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const res = await fetch(`/api/v1/credentials/vendors/${encodeURIComponent(selectedVendor.value.name)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm.value),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '保存失败')
    }
    message.success('保存成功')
    editMode.value = false
    await loadVendors()
    await selectVendor({ name: editForm.value.name })
  } catch (e) {
    message.error('保存失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

function handleDelete() {
  if (!selectedVendor.value) return
  dialog.warning({
    title: '确认删除',
    content: `确定要删除厂商「${selectedVendor.value.name}」吗？`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`/api/v1/credentials/vendors/${encodeURIComponent(selectedVendor.value.name)}`, {
          method: 'DELETE',
        })
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail || '删除失败')
        }
        message.success('删除成功')
        selectedVendor.value = null
        await loadVendors()
      } catch (e) {
        message.error('删除失败: ' + e.message)
      }
    },
  })
}

onMounted(() => {
  loadVendors()
  loadCategories()
})
</script>

<style scoped>
.vendor-credentials-page {
  padding: 16px;
  height: 100%;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
}

.subtitle {
  margin: 0;
  color: var(--text-color-3);
  font-size: 13px;
}

.main-grid {
  height: calc(100vh - 140px);
}

.vendor-list-panel {
  height: 100%;
  overflow: hidden;
}

.vendor-list-panel :deep(.n-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vendor-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 8px;
}

.search-input,
.category-select {
  margin-bottom: 8px;
}

.vendor-item {
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.vendor-item:hover {
  background: var(--hover-color);
}

.vendor-item.active {
  background: var(--primary-color-hover);
}

.vendor-item-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.vendor-name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.vendor-item-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-color-3);
}

.vendor-detail-panel {
  height: 100%;
  overflow-y: auto;
}

.empty-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.fingerprint-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border-color);
}

.fp-pattern {
  font-size: 12px;
  background: var(--code-color);
  padding: 2px 6px;
  border-radius: 4px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cred-notes {
  font-size: 12px;
  color: var(--text-color-3);
}

.edit-form {
  margin-top: 16px;
  padding: 16px;
  background: var(--body-color);
  border-radius: 8px;
}

.add-form-card {
  margin-top: 16px;
}

.add-form-actions {
  margin-top: 16px;
}
</style>
