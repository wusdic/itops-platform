<template>
  <div class="vendor-credentials-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📋 厂商账密配置</h2>
      <p class="subtitle">查看和管理网络设备厂商指纹及默认登录凭据，支持搜索、新增、编辑、删除</p>
    </div>

    <el-row :gutter="16" class="main-grid">
      <!-- 左侧：厂商列表 -->
      <el-col :span="6" class="vendor-list-panel">
        <el-card size="small">
          <template #header>
            <div class="card-header">
              <span>🏢 厂商列表</span>
              <el-tag type="info" size="small">{{ filteredVendors.length }} 个</el-tag>
            </div>
          </template>

          <!-- 搜索框 -->
          <el-input
            v-model="searchText"
            placeholder="搜索厂商..."
            clearable
            size="small"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <!-- 分类筛选 -->
          <el-select
            v-model="selectedCategory"
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
                <el-tag size="small" :type="categoryColor(vendor.category)">{{ vendor.category }}</el-tag>
                <span class="vendor-name">{{ vendor.name }}</span>
              </div>
              <div class="vendor-item-meta">
                <span>🔑 {{ vendor.credential_count }} 个账密</span>
                <span>🔍 {{ vendor.fingerprint_count }} 个指纹</span>
              </div>
            </div>
            <el-empty v-if="filteredVendors.length === 0" description="未找到匹配厂商" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：厂商详情 -->
      <el-col :span="18" class="vendor-detail-panel">
        <el-card v-if="selectedVendor" size="small">
          <template #header>
            <div class="card-header">
              <span>{{ selectedVendor.name }} - 详细信息</span>
              <el-space>
                <el-button size="small" @click="editMode = !editMode">
                  <el-icon><Edit /></el-icon>
                  {{ editMode ? '取消编辑' : '编辑' }}
                </el-button>
                <el-button size="small" type="danger" @click="handleDelete">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </el-space>
            </div>
          </template>

          <el-tabs type="border-card" size="small">
            <!-- 基本信息 -->
            <el-tab-pane label="📄 基本信息">
              <el-descriptions :column="2" label-placement="left" size="small" border>
                <el-descriptions-item label="厂商名称">{{ selectedVendor.name }}</el-descriptions-item>
                <el-descriptions-item label="简称">{{ selectedVendor.short_name }}</el-descriptions-item>
                <el-descriptions-item label="分类">
                  <el-tag size="small" :type="categoryColor(selectedVendor.category)">{{ selectedVendor.category }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="官网">
                  <a :href="selectedVendor.homepage" target="_blank" v-if="selectedVendor.homepage">
                    {{ selectedVendor.homepage }}
                  </a>
                  <span v-else>-</span>
                </el-descriptions-item>
                <el-descriptions-item label="描述" :span="2">{{ selectedVendor.description || '-' }}</el-descriptions-item>
                <el-descriptions-item label="建议协议">{{ selectedVendor.suggested_protocols?.join(', ') || '-' }}</el-descriptions-item>
                <el-descriptions-item label="探测端口">{{ selectedVendor.probe_ports?.join(', ') || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>

            <!-- 指纹模式 -->
            <el-tab-pane label="🔍 指纹模式">
              <el-space direction="vertical" style="width: 100%">
                <div v-for="(fp, idx) in selectedVendor.fingerprints" :key="idx" class="fingerprint-item">
                  <el-tag :type="fpTypeColor(fp.type)" size="small">{{ fp.type }}</el-tag>
                  <code class="fp-pattern">{{ fp.pattern || fp.oid_prefix }}</code>
                  <el-tag size="small" type="info">权重: {{ fp.weight }}</el-tag>
                </div>
                <el-empty v-if="!selectedVendor.fingerprints?.length" description="暂无指纹模式" :image-size="60" />
              </el-space>
            </el-tab-pane>

            <!-- 默认账密 -->
            <el-tab-pane label="🔑 默认账密">
              <el-table :border="false" size="small" style="width: 100%">
                <el-table-column prop="protocol" label="协议" width="100">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.protocol }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="username" label="用户名">
                  <template #default="{ row }">
                    <code>{{ row.username || '-' }}</code>
                  </template>
                </el-table-column>
                <el-table-column prop="password" label="密码">
                  <template #default="{ row }">
                    <code>{{ row.password || (row.community ? `community: ${row.community}` : '-') }}</code>
                  </template>
                </el-table-column>
                <el-table-column prop="notes" label="说明">
                  <template #default="{ row }">
                    <span class="cred-notes">{{ row.notes || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="priority" label="优先级" width="80">
                  <template #default="{ row }">
                    <el-tag size="small" type="warning">{{ row.priority }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!selectedVendor.default_credentials?.length" description="暂无默认账密" :image-size="60" />
            </el-tab-pane>
          </el-tabs>

          <!-- 编辑模式 -->
          <div v-if="editMode" class="edit-form">
            <el-divider>编辑模式</el-divider>
            <el-form :model="editForm" label-position="left" label-width="100">
              <el-form-item label="厂商名称">
                <el-input v-model="editForm.name" />
              </el-form-item>
              <el-form-item label="简称">
                <el-input v-model="editForm.short_name" />
              </el-form-item>
              <el-form-item label="分类">
                <el-select v-model="editForm.category" :options="categoryOptions" />
              </el-form-item>
              <el-form-item label="官网">
                <el-input v-model="editForm.homepage" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="editForm.description" type="textarea" />
              </el-form-item>
              <el-form-item label="建议协议">
                <el-select v-model="editForm.suggested_protocols" multiple filterable allow-create default-first-option placeholder="输入或选择协议" style="width: 100%">
                  <el-option v-for="p in protocolOptions" :key="p.value" :label="p.label" :value="p.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="探测端口">
                <el-select v-model="editForm.probe_ports" multiple :options="portOptions" style="width: 100%" />
              </el-form-item>
            </el-form>
            <el-space>
              <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
              <el-button @click="editMode = false">取消</el-button>
            </el-space>
          </div>
        </el-card>

        <!-- 无选中 -->
        <el-card v-else class="empty-detail">
          <el-empty description="从左侧选择一个厂商查看详情">
            <template #extra>
              <el-button size="small" type="primary" @click="startAddNew">
                <el-icon><Plus /></el-icon>
                新增厂商
              </el-button>
            </template>
          </el-empty>
        </el-card>

        <!-- 新增厂商 -->
        <el-card v-if="addingNew" size="small" class="add-form-card">
          <template #header>
            <span>➕ 新增厂商</span>
          </template>
          <el-form :model="addForm" label-position="left" label-width="120">
            <el-form-item label="厂商名称" required>
              <el-input v-model="addForm.name" placeholder="例如：Cisco Systems" />
            </el-form-item>
            <el-form-item label="简称" required>
              <el-input v-model="addForm.short_name" placeholder="例如：Cisco" />
            </el-form-item>
            <el-form-item label="分类" required>
              <el-select v-model="addForm.category" :options="categoryOptions" placeholder="选择分类" style="width: 100%" />
            </el-form-item>
            <el-form-item label="官网">
              <el-input v-model="addForm.homepage" placeholder="https://..." />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="addForm.description" type="textarea" />
            </el-form-item>
            <el-form-item label="建议协议">
              <el-select v-model="addForm.suggested_protocols" multiple filterable allow-create default-first-option placeholder="输入或选择协议" style="width: 100%">
                <el-option v-for="p in protocolOptions" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="探测端口">
              <el-select v-model="addForm.probe_ports" multiple :options="portOptions" style="width: 100%" />
            </el-form-item>
          </el-form>
          <el-space class="add-form-actions">
            <el-button type="primary" @click="handleAdd" :loading="saving">创建</el-button>
            <el-button @click="addingNew = false">取消</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'

const message = ElMessage

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
    switch: 'success', router: 'warning', firewall: 'danger',
    server: 'info', wireless: 'success', ups: 'warning',
    storage: 'info', camera: 'danger', printer: 'info',
    loadbalancer: 'info', virtualization: 'info', cloud: 'success',
    iot: 'warning', other: 'info',
  }
  return colors[cat] || 'info'
}

function fpTypeColor(type) {
  const colors = {
    ssh_banner: 'success', http_header: 'info', snmp_sysObjectID: 'warning',
    snmp_sysDesc: 'warning', dns_reverse: 'info',
  }
  return colors[type] || 'info'
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
  ElMessageBox.confirm(
    `确定要删除厂商「${selectedVendor.value.name}」吗？`,
    '确认删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
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
    }).catch(e => message.error('删除失败: ' + (e.message || e)))
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

.vendor-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 8px;
}

.search-input,
.category-select {
  margin-bottom: 8px;
  width: 100%;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
