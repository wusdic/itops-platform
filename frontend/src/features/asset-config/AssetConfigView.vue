<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">资产与配置台</h1>
        <p class="page-subtitle">统一管理资产、凭证和配置信息</p>
      </div>
      <el-button type="primary" @click="showAssetDialog = true">
        <el-icon><Plus /></el-icon> 新建资产
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon assets-icon"><el-icon><Box /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.asset_total }}</div>
            <div class="stat-label">资产总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon cred-icon"><el-icon><Key /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.cred_total }}</div>
            <div class="stat-label">凭证数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon config-icon"><el-icon><Setting /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.config_total }}</div>
            <div class="stat-label">配置项</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页：资产 | 凭证 | 配置 -->
    <el-card class="mt-4">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 资产列表 -->
        <el-tab-pane label="资产列表" name="assets">
          <div class="tab-toolbar">
            <el-input
              v-model="assetSearch"
              placeholder="搜索资产名称/IP"
              style="width: 240px"
              clearable
              @input="debounceAssetSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-select v-model="assetTypeFilter" placeholder="资产类型" clearable style="width: 140px" @change="loadAssets">
              <el-option label="全部" value="" />
              <el-option label="服务器" value="server" />
              <el-option label="网络设备" value="network" />
              <el-option label="存储设备" value="storage" />
              <el-option label="安全设备" value="security" />
              <el-option label="云资源" value="cloud" />
            </el-select>
          </div>

          <el-table :data="assets" v-loading="assetLoading" stripe class="mt-3" row-key="id">
            <el-table-column prop="asset_id" label="资产编号" width="120" />
            <el-table-column prop="name" label="资产名称" min-width="160">
              <template #default="{ row }">
                <div class="asset-name">{{ row.name || '-' }}</div>
                <div class="asset-ip" v-if="row.ip_address">{{ row.ip_address }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="asset_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ assetTypeLabel(row.asset_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="statusType(row.status)">{{ row.status || 'unknown' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ip_address" label="IP地址" width="140" />
            <el-table-column prop="os_type" label="操作系统" width="120" />
            <el-table-column prop="vendor" label="厂商" width="120" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="editAsset(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteAsset(row)">删除</el-button>
              </template>
            </el-table-column>
            <el-empty v-if="!assetLoading && assets.length === 0" description="暂无资产" />
          </el-table>

          <el-pagination
            v-if="assetTotal > 0"
            class="mt-3"
            v-model:current-page="assetPage"
            v-model:page-size="assetPageSize"
            :total="assetTotal"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadAssets"
            @size-change="loadAssets"
          />
        </el-tab-pane>

        <!-- 凭证列表 -->
        <el-tab-pane label="凭证管理" name="credentials">
          <div class="tab-toolbar">
            <el-input
              v-model="credSearch"
              placeholder="搜索凭证名称"
              style="width: 240px"
              clearable
              @input="debounceCredSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-button type="primary" @click="showCredDialog = true">
              <el-icon><Plus /></el-icon> 新建凭证
            </el-button>
          </div>

          <el-table :data="credentials" v-loading="credLoading" stripe class="mt-3" row-key="id">
            <el-table-column prop="name" label="凭证名称" min-width="160" />
            <el-table-column prop="credential_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ credTypeLabel(row.credential_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户名" width="140" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="usage_count" label="使用次数" width="100" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="editCred(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteCred(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-if="credTotal > 0"
            class="mt-3"
            v-model:current-page="credPage"
            v-model:page-size="credPageSize"
            :total="credTotal"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadCredentials"
            @size-change="loadCredentials"
          />
        </el-tab-pane>

        <!-- 配置列表 -->
        <el-tab-pane label="配置管理" name="configs">
          <div class="tab-toolbar">
            <el-input
              v-model="configSearch"
              placeholder="搜索配置项"
              style="width: 240px"
              clearable
              @input="debounceConfigSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-button type="primary" @click="showConfigDialog = true">
              <el-icon><Plus /></el-icon> 新建配置
            </el-button>
          </div>

          <el-table :data="configs" v-loading="configLoading" stripe class="mt-3" row-key="id">
            <el-table-column prop="key" label="配置键" min-width="200" />
            <el-table-column prop="value" label="配置值" min-width="200" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="env" label="环境" width="90">
              <template #default="{ row }">
                <el-tag size="small">{{ row.env || 'ALL' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="editConfig(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteConfig(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-if="configTotal > 0"
            class="mt-3"
            v-model:current-page="configPage"
            v-model:page-size="configPageSize"
            :total="configTotal"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadConfigs"
            @size-change="loadConfigs"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>

  <!-- 资产对话框 -->
  <el-dialog v-model="showAssetDialog" :title="editingAsset ? '编辑资产' : '新建资产'" width="600px" destroy-on-close>
    <el-form :model="assetForm" label-width="100px">
      <el-form-item label="资产名称" required>
        <el-input v-model="assetForm.name" placeholder="例如：测试服务器-01" />
      </el-form-item>
      <el-form-item label="资产类型" required>
        <el-select v-model="assetForm.asset_type" placeholder="选择类型" style="width: 100%">
          <el-option label="服务器" value="server" />
          <el-option label="网络设备" value="network" />
          <el-option label="存储设备" value="storage" />
          <el-option label="安全设备" value="security" />
          <el-option label="云资源" value="cloud" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="IP地址">
        <el-input v-model="assetForm.ip_address" placeholder="例如：192.168.1.100" />
      </el-form-item>
      <el-form-item label="主机名">
        <el-input v-model="assetForm.hostname" placeholder="例如：web-server-01" />
      </el-form-item>
      <el-form-item label="操作系统">
        <el-input v-model="assetForm.os_type" placeholder="例如：Linux, Windows Server 2019" />
      </el-form-item>
      <el-form-item label="SSH端口">
        <el-input-number v-model="assetForm.ssh_port" :min="1" :max="65535" style="width: 100%" />
      </el-form-item>
      <el-form-item label="厂商">
        <el-input v-model="assetForm.vendor" placeholder="例如：Dell, HP, Lenovo" />
      </el-form-item>
      <el-form-item label="型号">
        <el-input v-model="assetForm.model" placeholder="例如：PowerEdge R740" />
      </el-form-item>
      <el-form-item label="序列号">
        <el-input v-model="assetForm.serial_number" placeholder="设备序列号" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="assetForm.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showAssetDialog = false">取消</el-button>
      <el-button type="primary" :loading="assetSaving" @click="saveAsset">保存</el-button>
    </template>
  </el-dialog>

  <!-- 凭证对话框 -->
  <el-dialog v-model="showCredDialog" :title="editingCred ? '编辑凭证' : '新建凭证'" width="500px" destroy-on-close>
    <el-form :model="credForm" label-width="100px">
      <el-form-item label="凭证名称" required>
        <el-input v-model="credForm.name" placeholder="例如：测试环境SSH" />
      </el-form-item>
      <el-form-item label="凭证类型" required>
        <el-select v-model="credForm.credential_type" placeholder="选择类型" style="width: 100%">
          <el-option label="SSH" value="ssh" />
          <el-option label="Windows" value="windows" />
          <el-option label="API Key" value="api_key" />
          <el-option label="密钥对" value="key_pair" />
        </el-select>
      </el-form-item>
      <el-form-item label="用户名" required>
        <el-input v-model="credForm.username" placeholder="登录用户名" />
      </el-form-item>
      <el-form-item label="密码/密钥">
        <el-input v-model="credForm.password" type="password" show-password placeholder="密码或密钥内容" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="credForm.description" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCredDialog = false">取消</el-button>
      <el-button type="primary" :loading="credSaving" @click="saveCred">保存</el-button>
    </template>
  </el-dialog>

  <!-- 配置对话框 -->
  <el-dialog v-model="showConfigDialog" :title="editingConfig ? '编辑配置' : '新建配置'" width="500px" destroy-on-close>
    <el-form :model="configForm" label-width="100px">
      <el-form-item label="配置键" required>
        <el-input v-model="configForm.key" placeholder="例如：alert.threshold.cpu" />
      </el-form-item>
      <el-form-item label="配置值" required>
        <el-input v-model="configForm.value" type="textarea" :rows="3" placeholder="配置值" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="configForm.category" placeholder="选择分类" style="width: 100%">
          <el-option label="监控" value="monitoring" />
          <el-option label="告警" value="alerting" />
          <el-option label="采集" value="collection" />
          <el-option label="自动化" value="automation" />
          <el-option label="系统" value="system" />
        </el-select>
      </el-form-item>
      <el-form-item label="环境">
        <el-select v-model="configForm.env" placeholder="应用环境" style="width: 100%">
          <el-option label="全部" value="ALL" />
          <el-option label="开发" value="DEV" />
          <el-option label="测试" value="TEST" />
          <el-option label="预发布" value="STAGING" />
          <el-option label="生产" value="PROD" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="configForm.description" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showConfigDialog = false">取消</el-button>
      <el-button type="primary" :loading="configSaving" @click="saveConfig">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetConfig } from './api'
import { Box, Key, Setting, Plus, Search } from '@element-plus/icons-vue'

// ========== 状态 ==========
const activeTab = ref('assets')
const stats = reactive({ asset_total: 0, cred_total: 0, config_total: 0 })

// 资产
const assets = ref([])
const assetLoading = ref(false)
const assetSearch = ref('')
const assetTypeFilter = ref('')
const assetPage = ref(1)
const assetPageSize = ref(20)
const assetTotal = ref(0)
const showAssetDialog = ref(false)
const editingAsset = ref(null)
const assetSaving = ref(false)
const assetForm = reactive({
  name: '', asset_type: 'server', ip_address: '', hostname: '',
  os_type: '', ssh_port: 22, vendor: '', model: '', serial_number: '', remark: ''
})

// 凭证
const credentials = ref([])
const credLoading = ref(false)
const credSearch = ref('')
const credPage = ref(1)
const credPageSize = ref(20)
const credTotal = ref(0)
const showCredDialog = ref(false)
const editingCred = ref(null)
const credSaving = ref(false)
const credForm = reactive({
  name: '', credential_type: 'ssh', username: '', password: '', description: ''
})

// 配置
const configs = ref([])
const configLoading = ref(false)
const configSearch = ref('')
const configPage = ref(1)
const configPageSize = ref(20)
const configTotal = ref(0)
const showConfigDialog = ref(false)
const editingConfig = ref(null)
const configSaving = ref(false)
const configForm = reactive({
  key: '', value: '', category: 'monitoring', env: 'ALL', description: ''
})

// ========== 辅助函数 ==========
const assetTypeLabel = (type) => {
  const map = { server: '服务器', network: '网络设备', storage: '存储设备', security: '安全设备', cloud: '云资源', other: '其他' }
  return map[type] || type || '未知'
}

const credTypeLabel = (type) => {
  const map = { ssh: 'SSH', windows: 'Windows', api_key: 'API Key', key_pair: '密钥对' }
  return map[type] || type || '未知'
}

const statusType = (status) => {
  const map = { active: 'success', inactive: 'info', warning: 'warning', critical: 'danger', maintenance: 'warning' }
  return map[status] || 'info'
}

let assetTimer = null
const debounceAssetSearch = () => {
  clearTimeout(assetTimer)
  assetTimer = setTimeout(() => { assetPage.value = 1; loadAssets() }, 300)
}

let credTimer = null
const debounceCredSearch = () => {
  clearTimeout(credTimer)
  credTimer = setTimeout(() => { credPage.value = 1; loadCredentials() }, 300)
}

let configTimer = null
const debounceConfigSearch = () => {
  clearTimeout(configTimer)
  configTimer = setTimeout(() => { configPage.value = 1; loadConfigs() }, 300)
}

// ========== 加载函数 ==========
async function loadStats() {
  try {
    const [assetRes, credRes, configRes] = await Promise.all([
      assetConfig.assets.getStats().catch(() => null),
      assetConfig.credentials.getSummary().catch(() => null),
      assetConfig.configs.getSummary().catch(() => null)
    ])
    stats.asset_total = assetRes?.total || assetRes?.asset_count || 0
    stats.cred_total = credRes?.total || 0
    stats.config_total = configRes?.total || 0
  } catch (e) {
    console.error('loadStats failed:', e)
  }
}

async function loadAssets() {
  assetLoading.value = true
  try {
    const params = { page: assetPage.value, page_size: assetPageSize.value }
    if (assetSearch.value) params.search = assetSearch.value
    if (assetTypeFilter.value) params.asset_type = assetTypeFilter.value

    const res = await assetConfig.assets.getList(params)
    const data = res?.data || res || {}
    assets.value = data.items || []
    assetTotal.value = data.total || assets.value.length
  } catch (e) {
    ElMessage.error('加载资产列表失败')
  } finally {
    assetLoading.value = false
  }
}

async function loadCredentials() {
  credLoading.value = true
  try {
    const params = { page: credPage.value, page_size: credPageSize.value }
    if (credSearch.value) params.search = credSearch.value

    const res = await assetConfig.credentials.getList(params)
    const data = res?.data || res || {}
    credentials.value = data.items || []
    credTotal.value = data.total || credentials.value.length
  } catch (e) {
    ElMessage.error('加载凭证列表失败')
  } finally {
    credLoading.value = false
  }
}

async function loadConfigs() {
  configLoading.value = true
  try {
    const params = { page: configPage.value, page_size: configPageSize.value }
    if (configSearch.value) params.search = configSearch.value

    const res = await assetConfig.configs.getList(params)
    const data = res?.data || res || {}
    configs.value = data.items || []
    configTotal.value = data.total || configs.value.length
  } catch (e) {
    ElMessage.error('加载配置列表失败')
  } finally {
    configLoading.value = false
  }
}

function onTabChange(tab) {
  if (tab === 'assets' && assets.value.length === 0) loadAssets()
  if (tab === 'credentials' && credentials.value.length === 0) loadCredentials()
  if (tab === 'configs' && configs.value.length === 0) loadConfigs()
}

// ========== 保存操作 ==========
async function saveAsset() {
  if (!assetForm.name) { ElMessage.warning('请填写资产名称'); return }
  assetSaving.value = true
  try {
    if (editingAsset.value) {
      await assetConfig.assets.update(editingAsset.value.id, assetForm)
      ElMessage.success('资产已更新')
    } else {
      await assetConfig.assets.create(assetForm)
      ElMessage.success('资产已创建')
    }
    showAssetDialog.value = false
    loadAssets()
    loadStats()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    assetSaving.value = false
  }
}

async function saveCred() {
  if (!credForm.name || !credForm.username) { ElMessage.warning('请填写名称和用户名'); return }
  credSaving.value = true
  try {
    if (editingCred.value) {
      await assetConfig.credentials.update(editingCred.value.id, credForm)
      ElMessage.success('凭证已更新')
    } else {
      await assetConfig.credentials.create(credForm)
      ElMessage.success('凭证已创建')
    }
    showCredDialog.value = false
    loadCredentials()
    loadStats()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    credSaving.value = false
  }
}

async function saveConfig() {
  if (!configForm.key || !configForm.value) { ElMessage.warning('请填写配置键和值'); return }
  configSaving.value = true
  try {
    if (editingConfig.value) {
      await assetConfig.configs.update(editingConfig.value.id, configForm)
      ElMessage.success('配置已更新')
    } else {
      await assetConfig.configs.create(configForm)
      ElMessage.success('配置已创建')
    }
    showConfigDialog.value = false
    loadConfigs()
    loadStats()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    configSaving.value = false
  }
}

function editAsset(row) {
  editingAsset.value = row
  Object.assign(assetForm, {
    name: row.name, asset_type: row.asset_type, ip_address: row.ip_address || '',
    hostname: row.hostname || '', os_type: row.os_type || '', ssh_port: row.ssh_port || 22,
    vendor: row.vendor || '', model: row.model || '', serial_number: row.serial_number || '', remark: row.remark || ''
  })
  showAssetDialog.value = true
}

function editCred(row) {
  editingCred.value = row
  Object.assign(credForm, { name: row.name, credential_type: row.credential_type, username: row.username, password: '', description: row.description || '' })
  showCredDialog.value = true
}

function editConfig(row) {
  editingConfig.value = row
  Object.assign(configForm, { key: row.key, value: row.value, category: row.category || 'monitoring', env: row.env || 'ALL', description: row.description || '' })
  showConfigDialog.value = true
}

async function deleteAsset(row) {
  try {
    await ElMessageBox.confirm(`确定删除资产"${row.name}"吗？`, '确认', { type: 'warning' })
    await assetConfig.assets.delete(row.id)
    ElMessage.success('已删除')
    loadAssets()
    loadStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

async function deleteCred(row) {
  try {
    await ElMessageBox.confirm(`确定删除凭证"${row.name}"吗？`, '确认', { type: 'warning' })
    await assetConfig.credentials.delete(row.id)
    ElMessage.success('已删除')
    loadCredentials()
    loadStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

async function deleteConfig(row) {
  try {
    await ElMessageBox.confirm(`确定删除配置"${row.key}"吗？`, '确认', { type: 'warning' })
    await assetConfig.configs.delete(row.id)
    ElMessage.success('已删除')
    loadConfigs()
    loadStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadStats()
  loadAssets()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 4px 0 0; }
.stats-row { margin-bottom: 16px; }
.stat-card { display: flex; align-items: center; gap: 16px; padding: 8px 0; }
.stat-icon { font-size: 32px; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.assets-icon { background: #e6f7ff; color: #1890ff; }
.cred-icon { background: #fff7e6; color: #fa8c16; }
.config-icon { background: #f6ffed; color: #52c41a; }
.stat-content { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; line-height: 1.2; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.tab-toolbar { display: flex; gap: 12px; align-items: center; }
.asset-name { font-weight: 500; }
.asset-ip { font-size: 12px; color: #909399; }
</style>
