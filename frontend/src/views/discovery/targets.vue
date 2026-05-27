<template>
  <div class="targets-container">
    <div class="page-header">
      <div>
        <h2>发现目标</h2>
        <p class="page-subtitle">管理网络扫描目标，支持 IP / SNMP / ARP 多种扫描方式</p>
      </div>
    </div>

    <!-- 扫描类型切换 -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-tabs v-model="activeTab" class="scan-tabs">
        <el-tab-pane label="IP 扫描" name="ip">
          <template #label>
            <span class="tab-label">
              <el-icon><Connection /></el-icon>
              IP 扫描
            </span>
          </template>
          <!-- IP 扫描面板 -->
          <div class="scan-panel">
            <el-form label-position="left" label-width="120px">
              <el-form-item label="目标网段">
                <el-space wrap>
                  <el-input v-model.trim="ipForm.cidr" placeholder="例如: 192.168.1.0/24" style="width: 260px" />
                  <el-button type="primary" @click="startIpScan" :loading="ipScanning" :disabled="!ipForm.cidr">
                    <el-icon v-if="!ipScanning"><Search /></el-icon>
                    开始扫描
                  </el-button>
                  <el-button @click="stopIpScan" :disabled="!ipScanning" type="warning">停止</el-button>
                </el-space>
              </el-form-item>
              <el-form-item label="扫描选项">
                <el-space>
                  <el-checkbox v-model="ipForm.scanPorts">扫描端口</el-checkbox>
                  <el-checkbox v-model="ipForm.grabBanners">获取Banner</el-checkbox>
                  <el-checkbox v-model="ipForm.snmpDetect">SNMP探测</el-checkbox>
                </el-space>
              </el-form-item>
            </el-form>

            <!-- 扫描进度 -->
            <el-card v-if="ipScanning || ipProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="ipProgress" :stroke-width="8" />
              <div class="scan-status">{{ ipStatus }}</div>
              <div class="scan-current-ip" v-if="ipCurrentIp">正在扫描: {{ ipCurrentIp }}</div>
            </el-card>

            <!-- IP 扫描结果 -->
            <div class="results-section">
              <div class="results-header">
                <span class="results-title">扫描结果</span>
                <el-space>
                  <span class="result-count">发现 {{ ipResults.length }} 台主机</span>
                  <el-button type="primary" size="small" @click="importSelectedDevices" :disabled="selectedDevices.length === 0">
                    导入选中 ({{ selectedDevices.length }})
                  </el-button>
                </el-space>
              </div>
              <el-table
                v-model:selected="selectedDevices"
                :data="ipResults"
                row-key="ip"
                :pagination="false"
                @selection-change="onDeviceSelectionChange"
                size="small"
              >
                <el-table-column type="selection" width="40" />
                <el-table-column label="IP地址" prop="ip" width="150" />
                <el-table-column label="主机名" prop="hostname" show-overflow-tooltip />
                <el-table-column label="操作系统" prop="os_type" width="120" />
                <el-table-column label="设备类型" prop="device_type" width="120" />
                <el-table-column label="厂商" prop="vendor" width="120" />
                <el-table-column label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">
                      {{ row.status === 'up' ? '在线' : '离线' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="开放端口" prop="ports" show-overflow-tooltip>
                  <template #default="{ row }">{{ row.ports ? row.ports.join(', ') : '-' }}</template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" link @click="importSingleDevice(row)">导入</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!ipScanning && ipResults.length === 0" description="暂无扫描结果，请先输入网段开始扫描" />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="SNMP 扫描" name="snmp">
          <template #label>
            <span class="tab-label">
              <el-icon><Monitor /></el-icon>
              SNMP 扫描
            </span>
          </template>
          <!-- SNMP 扫描面板 -->
          <div class="scan-panel">
            <el-form label-position="left" label-width="120px">
              <el-form-item label="目标地址">
                <el-space wrap>
                  <el-input v-model.trim="snmpForm.target" placeholder="例如: 192.168.1.1" style="width: 220px" />
                  <el-select v-model="snmpForm.version" placeholder="SNMP版本" style="width:140px">
                    <el-option label="v1" value="v1" />
                    <el-option label="v2c" value="v2c" />
                    <el-option label="v3" value="v3" />
                  </el-select>
                  <el-input v-model.trim="snmpForm.community" placeholder="Community" style="width:160px" />
                </el-space>
              </el-form-item>
              <el-form-item label="扫描选项">
                <el-space wrap>
                  <el-checkbox v-model="snmpForm.getDeviceInfo">获取设备信息</el-checkbox>
                  <el-checkbox v-model="snmpForm.getInterfaces">获取接口列表</el-checkbox>
                  <el-checkbox v-model="snmpForm.getRouting">获取路由表</el-checkbox>
                </el-space>
              </el-form-item>
              <el-form-item label="">
                <el-button type="primary" @click="startSnmpScan" :loading="snmpScanning" :disabled="!snmpForm.target">
                  <el-icon v-if="!snmpScanning"><Search /></el-icon>
                  开始扫描
                </el-button>
              </el-form-item>
            </el-form>

            <!-- SNMP 扫描进度 -->
            <el-card v-if="snmpScanning || snmpProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="snmpProgress" :stroke-width="8" />
              <div class="scan-status">{{ snmpStatus }}</div>
            </el-card>

            <!-- SNMP 设备列表 -->
            <div class="results-section">
              <div class="results-header">
                <span class="results-title">SNMP 设备列表</span>
                <span class="result-count">共 {{ snmpDevices.length }} 台设备</span>
              </div>
              <el-table :data="snmpDevices" row-key="ip" :pagination="false" size="small">
                <el-table-column label="IP地址" prop="ip" width="150" />
                <el-table-column label="设备名称" prop="sysName" show-overflow-tooltip />
                <el-table-column label="描述" prop="sysDescr" show-overflow-tooltip />
                <el-table-column label="联系" prop="sysContact" width="150" show-overflow-tooltip />
                <el-table-column label="位置" prop="sysLocation" width="120" show-overflow-tooltip />
                <el-table-column label="接口数" prop="ifCount" width="80" align="center" />
                <el-table-column label="类型" prop="device_type" width="100">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.device_type || '未知' }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" link @click="importSnmpDevice(row)">导入</el-button>
                    <el-button size="small" type="info" link @click="showSnmpDetail(row)">详情</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!snmpScanning && snmpDevices.length === 0" description="暂无SNMP设备，请先输入目标地址开始扫描" />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="ARP 扫描" name="arp">
          <template #label>
            <span class="tab-label">
              <el-icon><DataAnalysis /></el-icon>
              ARP 扫描
            </span>
          </template>
          <!-- ARP 扫描面板 -->
          <div class="scan-panel">
            <el-form label-position="left" label-width="120px">
              <el-form-item label="目标网段">
                <el-space wrap>
                  <el-input v-model.trim="arpForm.cidr" placeholder="例如: 192.168.1.0/24" style="width: 260px" />
                  <el-button type="primary" @click="startArpScan" :loading="arpScanning" :disabled="!arpForm.cidr">
                    <el-icon v-if="!arpScanning"><Search /></el-icon>
                    开始扫描
                  </el-button>
                  <el-button @click="stopArpScan" :disabled="!arpScanning" type="warning">停止</el-button>
                </el-space>
              </el-form-item>
            </el-form>

            <!-- ARP 扫描进度 -->
            <el-card v-if="arpScanning || arpProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="arpProgress" :stroke-width="8" />
              <div class="scan-status">{{ arpStatus }}</div>
            </el-card>

            <!-- ARP 扫描结果 -->
            <div class="results-section">
              <div class="results-header">
                <span class="results-title">ARP 扫描结果</span>
                <span class="result-count">发现 {{ arpResults.length }} 条记录</span>
              </div>
              <el-table :data="arpResults" row-key="ip" :pagination="false" size="small">
                <el-table-column label="IP地址" prop="ip" width="150" />
                <el-table-column label="MAC地址" prop="mac" width="180" />
                <el-table-column label="设备类型" prop="device_type" width="120" />
                <el-table-column label="厂商标识" prop="vendor" show-overflow-tooltip />
                <el-table-column label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">
                      {{ row.status === 'up' ? '在线' : '离线' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="最后发现" prop="last_seen" width="170">
                  <template #default="{ row }">{{ row.last_seen ? row.last_seen.slice(0, 16) : '-' }}</template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" link @click="importArpDevice(row)">导入</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!arpScanning && arpResults.length === 0" description="暂无ARP扫描结果，请先输入网段开始扫描" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 扫描历史记录 -->
    <el-card title="扫描历史" shadow="never">
      <template #header>
        <div class="card-header">
          <span>扫描历史</span>
        </div>
      </template>
      <el-table :data="scanHistory" row-key="id" :pagination="historyPagination">
        <el-table-column label="扫描类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="scanTypeTag(row.scan_type)">{{ scanTypeText(row.scan_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标" prop="target" width="200" show-overflow-tooltip />
        <el-table-column label="扫描时间" prop="scan_time" width="170">
          <template #default="{ row }">{{ row.scan_time ? row.scan_time.slice(0, 16) : '-' }}</template>
        </el-table-column>
        <el-table-column label="发现主机" prop="hosts_found" width="100" align="center" />
        <el-table-column label="在线" prop="hosts_online" width="80" align="center" />
        <el-table-column label="已导入" prop="hosts_imported" width="80" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="scanStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewScanDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && scanHistory.length === 0" description="暂无扫描历史" />
    </el-card>

    <!-- SNMP 设备详情弹窗 -->
    <el-dialog v-model="snmpDetailVisible" title="SNMP 设备详情" width="640px" destroy-on-close>
      <el-descriptions v-if="snmpDetailData" :column="2" border direction="vertical" size="default">
        <el-descriptions-item label="IP地址">{{ snmpDetailData.ip }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ snmpDetailData.device_type || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ snmpDetailData.sysName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="接口数量">{{ snmpDetailData.ifCount || 0 }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ snmpDetailData.sysDescr || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系">{{ snmpDetailData.sysContact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="位置">{{ snmpDetailData.sysLocation || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运行时间">{{ snmpDetailData.sysUptime || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="snmpInterfaces.length > 0" class="interfaces-section">
        <div class="interfaces-title">网络接口</div>
        <el-table :data="snmpInterfaces" size="small">
          <el-table-column label="接口名" prop="ifDescr" width="150" show-overflow-tooltip />
          <el-table-column label="类型" prop="ifType" width="100" />
          <el-table-column label="MAC" prop="ifPhysAddress" width="180" />
          <el-table-column label="状态" width="70">
            <template #default="{ row }">
              <el-tag size="small" :type="row.ifOperStatus === 'up' ? 'success' : 'info'">
                {{ row.ifOperStatus }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="IP地址" prop="ifIpAddress" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-space justify="end">
          <el-button @click="snmpDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="importSnmpDevice(snmpDetailData)">导入设备</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Connection, Monitor, DataAnalysis } from '@element-plus/icons-vue'
import { discovery } from '@/api'

// ── Tab 状态 ──────────────────────────────────────────────
const activeTab = ref('ip')

// ── IP 扫描 ───────────────────────────────────────────────
const ipScanning = ref(false)
const ipProgress = ref(0)
const ipStatus = ref('')
const ipCurrentIp = ref('')
const ipResults = ref([])
const selectedDevices = ref([])

const ipForm = reactive({
  cidr: '',
  scanPorts: true,
  grabBanners: true,
  snmpDetect: false
})

let ipPollTimer = null

async function startIpScan() {
  if (!ipForm.cidr) return
  ipScanning.value = true
  ipProgress.value = 0
  ipStatus.value = '正在启动扫描任务...'
  ipResults.value = []
  selectedDevices.value = []
  ipCurrentIp.value = ''

  try {
    const token = localStorage.getItem('token')
    const startRes = await fetch('/api/v1/discovery/ip/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        cidr: ipForm.cidr,
        scan_ports: ipForm.scanPorts,
        grab_banners: ipForm.grabBanners,
        snmp_detect: ipForm.snmpDetect
      })
    })

    if (!startRes.ok) throw new Error(`启动扫描失败 HTTP ${startRes.status}`)
    const { task_id } = await startRes.json()

    // 轮询进度
    while (true) {
      await new Promise(r => setTimeout(r, 1000))
      const pollRes = await fetch(`/api/v1/discovery/scan/${task_id}/status`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!pollRes.ok) continue

      const data = await pollRes.json()
      const { status, progress, result, error } = data

      if (progress) {
        const { complete = 0, total = 0, current_ip = '', phase = '' } = progress
        if (total > 0) ipProgress.value = Math.round(complete / total * 100)
        if (current_ip) ipCurrentIp.value = current_ip
        if (phase === 'scanning') {
          ipStatus.value = `正在扫描 ${current_ip}（${complete}/${total}）`
        } else if (phase === 'importing') {
          ipStatus.value = `正在导入 ${current_ip}（${complete}/${total}）`
        }
      }

      if (status === 'done') {
        ipProgress.value = 100
        const discovered = result?.total_discovered || 0
        const imported = result?.newly_imported || 0
        ipStatus.value = `扫描完成，发现 ${discovered} 台主机，已导入 ${imported} 台新设备`
        ipResults.value = result?.hosts || []
        if (discovered > 0) {
          if (imported > 0) {
            ElMessage.success(`发现 ${discovered} 台主机，导入 ${imported} 台新设备`)
          } else {
            ElMessage.info(`发现 ${discovered} 台主机（均已存在，无需重复导入）`)
          }
        } else {
          ElMessage.warning('未发现新设备')
        }
        loadScanHistory()
        break
      } else if (status === 'error') {
        ipProgress.value = 0
        ipStatus.value = `扫描失败: ${error}`
        ElMessage.error(`扫描失败: ${error}`)
        break
      } else if (status === 'stopped') {
        ipStatus.value = '扫描已停止'
        break
      }
    }
  } catch (e) {
    ipProgress.value = 0
    ipStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`扫描失败: ${e.message}`)
  } finally {
    ipScanning.value = false
    ipCurrentIp.value = ''
  }
}

function stopIpScan() {
  ipScanning.value = false
  ipStatus.value = '扫描已停止'
}

function onDeviceSelectionChange(keys) {
  selectedDevices.value = keys
}

async function importSelectedDevices() {
  if (!selectedDevices.value.length) return
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ ips: selectedDevices.value.map(h => h.ip), device_type: 'server' })
    })
    if (res.ok) {
      ElMessage.success(`成功导入 ${selectedDevices.value.length} 台设备`)
      ipResults.value = ipResults.value.filter(r => !selectedDevices.value.map(h => h.ip).includes(r.ip))
      selectedDevices.value = []
      loadScanHistory()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

async function importSingleDevice(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32' })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      ipResults.value = ipResults.value.filter(r => r.ip !== row.ip)
      loadScanHistory()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

// ── SNMP 扫描 ─────────────────────────────────────────────
const snmpScanning = ref(false)
const snmpProgress = ref(0)
const snmpStatus = ref('')
const snmpDevices = ref([])
const snmpDetailVisible = ref(false)
const snmpDetailData = ref({})
const snmpInterfaces = ref([])

const snmpForm = reactive({
  target: '',
  version: 'v2c',
  community: 'public',
  getDeviceInfo: true,
  getInterfaces: true,
  getRouting: false
})

async function startSnmpScan() {
  if (!snmpForm.target) return
  snmpScanning.value = true
  snmpProgress.value = 0
  snmpStatus.value = '正在执行 SNMP 扫描...'
  snmpDevices.value = []

  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/discovery/snmp/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(snmpForm)
    })

    if (!res.ok) throw new Error(`扫描失败 HTTP ${res.status}`)
    const data = await res.json()

    snmpProgress.value = 100
    snmpDevices.value = data.devices || [data] || []
    snmpStatus.value = `扫描完成，发现 ${snmpDevices.value.length} 台 SNMP 设备`
    ElMessage.success(snmpStatus.value)
    loadScanHistory()
  } catch (e) {
    snmpProgress.value = 0
    snmpStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`SNMP 扫描失败: ${e.message}`)
  } finally {
    snmpScanning.value = false
  }
}

function showSnmpDetail(row) {
  snmpDetailData.value = row
  snmpInterfaces.value = row.interfaces || []
  snmpDetailVisible.value = true
}

async function importSnmpDevice(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32', device_type: 'snmp_device', snmp_data: row })
    })
    if (res.ok) {
      ElMessage.success('SNMP 设备导入成功')
      snmpDevices.value = snmpDevices.value.filter(d => d.ip !== row.ip)
      snmpDetailVisible.value = false
      loadScanHistory()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

// ── ARP 扫描 ───────────────────────────────────────────────
const arpScanning = ref(false)
const arpProgress = ref(0)
const arpStatus = ref('')
const arpResults = ref([])

const arpForm = reactive({
  cidr: ''
})

let arpPollTimer = null

async function startArpScan() {
  if (!arpForm.cidr) return
  arpScanning.value = true
  arpProgress.value = 0
  arpStatus.value = '正在执行 ARP 扫描...'
  arpResults.value = []

  try {
    const token = localStorage.getItem('token')
    const startRes = await fetch('/api/v1/discovery/arp/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: arpForm.cidr })
    })

    if (!startRes.ok) throw new Error(`ARP扫描失败 HTTP ${startRes.status}`)
    const result = await startRes.json()

    // ARP 扫描是同步的，直接返回结果，无需轮询
    arpProgress.value = 100
    arpResults.value = result?.hosts || []
    arpStatus.value = `ARP 扫描完成，发现 ${arpResults.value.length} 条记录`
    if (arpResults.value.length > 0) {
      ElMessage.success(arpStatus.value)
    }
    loadScanHistory()
  } catch (e) {
    arpProgress.value = 0
    arpStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`ARP 扫描失败: ${e.message}`)
  } finally {
    arpScanning.value = false
  }
}

function stopArpScan() {
  arpScanning.value = false
  arpStatus.value = '扫描已停止'
}

async function importArpDevice(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32', device_type: 'arp_device', mac: row.mac })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      arpResults.value = arpResults.value.filter(r => r.ip !== row.ip)
      loadScanHistory()
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

// ── 扫描历史 ───────────────────────────────────────────────
const scanHistory = ref([])
const historyPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  layout: 'prev, pager, next, sizes',
  pageSizes: [10, 20, 50],
  onCurrentChange: (p) => { historyPagination.currentPage = p; loadScanHistory() },
  onSizeChange: (s) => { historyPagination.pageSize = s; historyPagination.currentPage = 1; loadScanHistory() }
})

async function loadScanHistory() {
  try {
    const params = { page: historyPagination.currentPage, page_size: historyPagination.pageSize }
    const res = await discovery.scan.getHistory(params)
    scanHistory.value = res.items || res.data?.items || []
    historyPagination.total = res.total || res.data?.total || 0
  } catch (e) {
    // 历史记录加载失败不影响主流程
  }
}

function viewScanDetail(row) {
  ElMessage.info(`扫描详情: ${row.target}`)
}

const scanTypeTag = (t) => ({ ip: 'primary', snmp: 'success', arp: 'warning' })[t] || 'info'
const scanTypeText = (t) => ({ ip: 'IP', snmp: 'SNMP', arp: 'ARP' })[t] || t
const scanStatusTag = (s) => ({ completed: 'success', failed: 'danger', running: 'warning' })[s] || 'info'

onMounted(() => { loadScanHistory() })
</script>

<style scoped>
.targets-container {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.page-subtitle {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.scan-panel {
  padding: 16px 0;
}

.progress-card {
  margin-top: 16px;
  background: var(--el-fill-color-light);
}

.scan-status {
  margin-top: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.scan-current-ip {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-tertiary);
  font-family: monospace;
}

.results-section {
  margin-top: 20px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.results-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.result-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.interfaces-section {
  margin-top: 16px;
}
.interfaces-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

/* 暗色主题适配 */
:deep(.el-card) {
  background: var(--el-bg-color);
  border-color: var(--el-border-color);
}
:deep(.el-tabs__item) {
  color: var(--el-text-color-secondary);
}
:deep(.el-tabs__item.is-active) {
  color: var(--el-color-primary);
}
:deep(.el-progress-bar__outer) {
  background: var(--el-fill-color-dark);
}
</style>
