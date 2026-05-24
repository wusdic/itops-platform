<template>
  <div class="scan-container">
    <el-space direction="vertical" :size="20" style="width: 100%">
      <el-card title="网段扫描配置" size="large">
        <el-space direction="vertical" :size="16" style="width: 100%">
          <!-- 网段输入 -->
          <el-form label-position="left" label-width="120px">
            <el-form-item label="扫描网段">
              <el-space>
                <el-input v-model="cidr" placeholder="例如: 192.168.1.0/24" style="width: 280px" />
                <el-button type="primary" @click="startScan" :loading="scanning" :disabled="!cidr">
                  <el-icon v-if="!scanning"><Search /></el-icon>
                  开始扫描
                </el-button>
                <el-button @click="stopScan" :disabled="!scanning" type="warning">
                  停止
                </el-button>
              </el-space>
            </el-form-item>
            <el-form-item label="扫描选项">
              <el-space>
                <el-checkbox v-model="options.scanPorts">扫描端口</el-checkbox>
                <el-checkbox v-model="options.grabBanners">获取Banner</el-checkbox>
                <el-checkbox v-model="options.snmpScan">SNMP探测</el-checkbox>
              </el-space>
            </el-form-item>
          </el-form>

          <!-- 扫描进度 -->
          <el-card v-if="scanning || scanProgress > 0" size="small" shadow="never">
            <el-progress :percentage="scanProgress" :stroke-width="10" />
            <div class="scan-status">{{ scanStatus }}</div>
          </el-card>

          <!-- 已保存的扫描任务 -->
          <el-card title="已配置网段" size="small">
            <template #header>
              <div class="card-header">
                <span>已配置网段</span>
                <el-button size="small" @click="openAddDialog">添加网段</el-button>
              </div>
            </template>
            <el-table
              v-if="savedNetworks.length > 0"
              :data="savedNetworks"
              :pagination="false"
              size="small"
              style="width: 100%"
            >
              <el-table-column v-for="col in networkColumns" :key="col.key" :="col" />
            </el-table>
            <el-empty v-else description="暂无已配置的网段，点击上方添加" />
          </el-card>
        </el-space>
      </el-card>

      <!-- 扫描结果 -->
      <el-card v-if="scanResults.length > 0" title="扫描结果" size="large">
        <template #header>
          <div class="card-header">
            <span>扫描结果</span>
            <el-space>
              <span class="result-count">发现 {{ scanResults.length }} 台主机</span>
              <el-button type="primary" size="small" @click="importSelected" :disabled="selectedHosts.length === 0">
                导入选中 ({{ selectedHosts.length }})
              </el-button>
            </el-space>
          </div>
        </template>

        <el-table
          v-model:selected="selectedHosts"
          :data="scanResults"
          row-key="ip"
          :pagination="false"
          @selection-change="onSelectionChange"
          style="width: 100%"
        >
          <el-table-column v-for="col in resultColumns" :key="col.key" :="col" />
        </el-table>

        <!-- 结果统计 -->
        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="6">
            <div class="statistic-item">
              <span class="statistic-label">在线主机</span>
              <span class="statistic-value">{{ onlineCount }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="statistic-item">
              <span class="statistic-label">Linux设备</span>
              <span class="statistic-value">{{ linuxCount }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="statistic-item">
              <span class="statistic-label">Windows设备</span>
              <span class="statistic-value">{{ windowsCount }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="statistic-item">
              <span class="statistic-label">网络设备</span>
              <span class="statistic-value">{{ networkCount }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 扫描历史 -->
      <el-card title="扫描历史" size="small">
        <el-table
          :data="scanHistory"
          :pagination="getHistoryPagination()"
          row-key="id"
          style="width: 100%"
        >
          <el-table-column v-for="col in historyColumns" :key="col.key" :="col" />
        </el-table>
      </el-card>
    </el-space>

    <!-- 添加/编辑网段对话框 -->
    <el-dialog v-model="showAddDialog" :title="editingNetwork ? '编辑扫描网段' : '添加扫描网段'" width="500px">
      <el-form label-position="left" label-width="100px">
        <el-form-item label="网段">
          <el-input v-model="editForm.cidr" placeholder="192.168.1.0/24" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" placeholder="可选描述" />
        </el-form-item>
        <el-form-item label="自动扫描">
          <el-space>
            <el-switch v-model="editForm.auto_scan" />
            <span class="help-text">启用后按调度自动扫描</span>
          </el-space>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveNetwork">保存</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const message = ElMessage

const cidr = ref('')
const scanning = ref(false)
const scanProgress = ref(0)
const scanStatus = ref('')
const scanResults = ref([])
const selectedHosts = ref([])
const scanHistory = ref([])
const showAddDialog = ref(false)
const editingNetwork = ref(null)
const savedNetworks = ref([])

const editForm = ref({ cidr: '', description: '', auto_scan: false })

const options = ref({
  scanPorts: true,
  grabBanners: true,
  snmpScan: false,
})

// ── 分页 refs ─────────────────────────────────────────────
const histPage = ref(1)
const histPageSize = ref(10)
const histTotal = ref(0)
const histPaginationVersion = ref(0)

const handleHistPageChange = (p) => {
  histPage.value = p
  histPagination.page = p
  histPaginationVersion.value++
  loadHistory()
}
const handleHistPageSizeChange = (s) => {
  histPageSize.value = s
  histPage.value = 1
  histPagination.pageSize = s
  histPagination.page = 1
  histPaginationVersion.value++
  loadHistory()
}
// 共享纯 JS 对象 — getHistoryPagination() 每次返回同一引用
const histPagination = reactive({
  page: 1,
  pageSize: 10,
  pageCount: 1,
  itemCount: 0,
  layout: 'prev, pager, next, sizes',
  pageSizes: [10, 20, 50],
  onCurrentChange: handleHistPageChange,
  onSizeChange: handleHistPageSizeChange,
})
const getHistoryPagination = () => {
  histPaginationVersion.value
  histPagination.pageCount = Math.max(1, Math.ceil((histTotal.value || 0) / (histPageSize.value || 1)))
  histPagination.itemCount = histTotal.value
  return histPagination
}

// ── Computed stats ─────────────────────────────────────────
const onlineCount = computed(() => scanResults.value.filter(r => r.status === 'up').length)
const linuxCount = computed(() => scanResults.value.filter(r => r.os_type === 'Linux').length)
const windowsCount = computed(() => scanResults.value.filter(r => r.os_type && r.os_type.includes('Windows')).length)
const networkCount = computed(() => scanResults.value.filter(r => ['Router', 'Switch', 'Firewall'].includes(r.device_type)).length)

// ── 列定义 ─────────────────────────────────────────────────
const networkColumns = [
  { title: '网段', key: 'cidr', width: 180 },
  { title: '描述', key: 'description', showOverflowTooltip: true },
  { title: '自动', key: 'auto_scan', width: 70, render: (r) => r.auto_scan ? '是' : '否' },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => h(ElSpace, { size: 8 }, () => [
      h(ElButton, { size: 'small', onClick: () => openEditDialog(row) }, () => '编辑'),
      h(ElButton, { size: 'small', onClick: () => quickScan(row.cidr) }, () => '扫描'),
      h(ElButton, { size: 'small', type: 'danger', onClick: () => deleteNetwork(row.id) }, () => '删除'),
    ])
  }
]

const resultColumns = [
  { type: 'selection' },
  { title: 'IP地址', key: 'ip', width: 150 },
  { title: '主机名', key: 'hostname', showOverflowTooltip: true, render: (r) => r.hostname || '-' },
  { title: '操作系统', key: 'os_type', width: 120, render: (r) => r.os_type || '-' },
  { title: '设备类型', key: 'device_type', width: 100, render: (r) => r.device_type || '-' },
  { title: '厂商', key: 'vendor', width: 120, render: (r) => r.vendor || '-' },
  { title: '状态', key: 'status', width: 80, render: (r) => h(ElTag, { type: r.status === 'up' ? 'success' : 'info', size: 'small' }, () => r.status === 'up' ? '在线' : '离线') },
  { title: '开放端口', key: 'ports', showOverflowTooltip: true, render: (r) => r.ports ? r.ports.join(', ') : '-' },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(ElSpace, { size: 8 }, () => [
      h(ElButton, { size: 'small', type: 'primary', onClick: () => importSingle(row) }, () => '导入'),
    ]),
  },
]

const historyColumns = [
  { title: '网段', key: 'cidr', width: 180 },
  { title: '扫描时间', key: 'scan_time', width: 180 },
  { title: '发现主机', key: 'hosts_found', width: 100 },
  { title: '在线', key: 'hosts_online', width: 80 },
  { title: '已导入', key: 'hosts_imported', width: 80 },
  { title: '状态', key: 'status', width: 100, render: (r) => h(ElTag, { type: r.status === 'completed' ? 'success' : r.status === 'failed' ? 'danger' : 'info', size: 'small' }, () => r.status) },
]

// ── 扫描 ───────────────────────────────────────────────────
function normalizeCIDR(input) {
  // Auto-fix common user mistakes:
  // - "10.168.1.0" -> "10.168.1.0/24" (treat as network, not single host)
  // - "10.168.1.1/24" -> "10.168.1.0/24" (normalize network address)
  const trimmed = input.trim()
  if (!trimmed.includes('/')) {
    // No CIDR suffix — assume /24 and fix network address
    const parts = trimmed.split('.')
    if (parts.length === 4) {
      return `${parts[0]}.${parts[1]}.${parts[2]}.0/24`
    }
    return trimmed
  }
  // Has CIDR suffix — normalize the network address
  try {
    const ip = trimmed.split('/')[0]
    const parts = ip.split('.').map(Number)
    if (parts.length === 4) {
      const normalized = `${parts[0]}.${parts[1]}.${parts[2]}.0/${trimmed.split('/')[1]}`
      return normalized
    }
  } catch (e) {
    // Let backend handle invalid input
  }
  return trimmed
}

async function startScan() {
  if (!cidr.value) return
  const normalizedCidr = normalizeCIDR(cidr.value)
  scanning.value = true
  scanProgress.value = 0
  scanStatus.value = '正在扫描...'
  scanResults.value = []
  selectedHosts.value = []

  try {
    const token = localStorage.getItem('token')
    // POST /api/v1/discovery/scan-and-import — 同步扫描，直接导入发现的设备
    const res = await fetch('/api/v1/discovery/scan-and-import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        cidr: normalizedCidr,
        scan_ports: options.value.scanPorts,
        grab_banners: options.value.grabBanners,
      }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.message || `HTTP ${res.status}`)
    }

    scanProgress.value = 80
    scanStatus.value = '解析响应...'

    const data = await res.json()
    // Backend returns {total_discovered, newly_imported, cidr} — hosts are imported directly to DB
    const discovered = data.total_discovered || 0
    const imported = data.newly_imported || 0
    scanProgress.value = 100
    if (discovered > 0) {
      scanStatus.value = `扫描完成，发现 ${discovered} 台主机，已导入 ${imported} 台新设备到设备列表`
      message.success(`发现 ${discovered} 台主机，导入 ${imported} 台新设备`)
    } else {
      scanStatus.value = '扫描完成，未发现主机（可能网络不可达或设备已存在）'
      message.warning('未发现新设备，可能网络不可达或设备已在库中')
    }
    scanResults.value = []
  } catch (e) {
    scanProgress.value = 0
    scanStatus.value = `扫描失败: ${e.message}`
    message.error(`扫描失败: ${e.message}`)
  } finally {
    scanning.value = false
  }
}

function stopScan() {
  scanning.value = false
  scanStatus.value = '扫描已停止'
}

async function quickScan(cidrValue) {
  cidr.value = normalizeCIDR(cidrValue)
  await startScan()
}

async function importSelected() {
  if (!selectedHosts.value.length) return
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/scan-and-import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        cidr: cidr.value,
        hosts: selectedHosts.value,
      }),
    })
    if (res.ok) {
      const data = await res.json()
      message.success(`成功导入 ${data.newly_imported || selectedHosts.value.length} 台新设备`)
      scanResults.value = scanResults.value.filter(r => !selectedHosts.value.includes(r.ip))
      selectedHosts.value = []
    } else {
      const err = await res.json().catch(() => ({}))
      message.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    message.error(`导入失败: ${e.message}`)
  }
}

async function importSingle(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/scan-and-import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32' }),
    })
    if (res.ok) {
      message.success('设备导入成功')
      scanResults.value = scanResults.value.filter(r => r.ip !== row.ip)
    } else {
      const err = await res.json().catch(() => ({}))
      message.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    message.error(`导入失败: ${e.message}`)
  }
}

function onSelectionChange(keys) {
  selectedHosts.value = keys
}

// ── 网段管理 ───────────────────────────────────────────────
function openAddDialog() {
  editingNetwork.value = null
  editForm.value = { cidr: '', description: '', auto_scan: false }
  showAddDialog.value = true
}

function openEditDialog(row) {
  editingNetwork.value = row
  editForm.value = { cidr: row.cidr, description: row.description || '', auto_scan: row.auto_scan || false }
  showAddDialog.value = true
}

async function saveNetwork() {
  if (!editForm.value.cidr) {
    message.warning('请输入网段')
    return
  }

  const token = localStorage.getItem('token')
  if (editingNetwork.value) {
    // 编辑现有
    try {
      const res = await fetch(`/api/v1/discovery/networks/${editingNetwork.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(editForm.value),
      })
      if (res.ok) {
        const updated = await res.json()
        const idx = savedNetworks.value.findIndex(n => n.id === editingNetwork.value.id)
        if (idx !== -1) savedNetworks.value[idx] = updated
        message.success('网段已更新')
      } else {
        message.error('更新失败')
      }
    } catch (e) {
      message.error(`更新失败: ${e.message}`)
    }
  } else {
    // 新增 — 保存到后端
    try {
      const res = await fetch('/api/v1/discovery/networks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(editForm.value),
      })
      if (res.ok) {
        const newNet = await res.json()
        savedNetworks.value.push(newNet)
        message.success('网段已保存')
      } else {
        // 如果后端没有此 API，退化为 localStorage
        savedNetworks.value.push({ id: Date.now(), ...editForm.value })
        localStorage.setItem('scan_networks', JSON.stringify(savedNetworks.value))
        message.success('网段已保存（本地存储）')
      }
    } catch {
      savedNetworks.value.push({ id: Date.now(), ...editForm.value })
      localStorage.setItem('scan_networks', JSON.stringify(savedNetworks.value))
      message.success('网段已保存（本地存储）')
    }
  }
  showAddDialog.value = false
}

async function deleteNetwork(id) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`/api/v1/discovery/networks/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    savedNetworks.value = savedNetworks.value.filter(n => n.id !== id)
    if (!res.ok) throw new Error()
    message.success('网段已删除')
  } catch {
    savedNetworks.value = savedNetworks.value.filter(n => n.id !== id)
    localStorage.setItem('scan_networks', JSON.stringify(savedNetworks.value))
    message.success('网段已删除（本地）')
  }
}

// ── 扫描历史 ───────────────────────────────────────────────
async function loadHistory() {
  const token = localStorage.getItem('token')
  try {
    const params = new URLSearchParams({
      page: histPage.value,
      page_size: histPageSize.value,
    })
    const res = await fetch(`/api/v1/discovery/scan-history?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      scanHistory.value = data.items || []
      histTotal.value = data.total || scanHistory.value.length
    } else {
      throw new Error()
    }
  } catch {
    // fallback: 从 localStorage
    const history = localStorage.getItem('scan_history')
    if (history) {
      scanHistory.value = JSON.parse(history)
    } else {
      scanHistory.value = []
    }
    histTotal.value = scanHistory.value.length
  }
}

// 加载网段列表
async function loadNetworks() {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/networks', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      // 后端返回数组，不是 {items: [...]} 格式
      savedNetworks.value = Array.isArray(data) ? data : (data.items || [])
      // 同时备份到 localStorage
      localStorage.setItem('scan_networks', JSON.stringify(savedNetworks.value))
    } else {
      throw new Error()
    }
  } catch {
    const networks = localStorage.getItem('scan_networks')
    if (networks) savedNetworks.value = JSON.parse(networks)
  }
}

onMounted(async () => {
  await loadNetworks()

  // 对所有 auto_scan=true 的网段自动触发扫描
  const autoScanNetworks = savedNetworks.value.filter(n => n.auto_scan)
  if (autoScanNetworks.length > 0) {
    message.info(`自动扫描 ${autoScanNetworks.length} 个已配置网段...`)
    for (const net of autoScanNetworks) {
      await quickScan(net.cidr)
    }
  }

  loadHistory()
})
</script>

<style scoped>
.scan-container {
  padding: 20px;
  max-width: 1200px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.scan-status {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}
.result-count {
  color: #909399;
  font-size: 14px;
}
.statistic-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.statistic-label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}
.statistic-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}
.help-text {
  color: #909399;
  font-size: 13px;
}
</style>
