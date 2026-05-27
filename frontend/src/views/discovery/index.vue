<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">网络扫描配置</h1>
        <p class="page-subtitle">配置和管理网络扫描任务，发现并导入网络设备</p>
      </div>
      <el-space>
        <el-button @click="loadConfigs" :loading="loadingConfig">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> 新建扫描任务
        </el-button>
      </el-space>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">扫描任务</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #18a058">{{ stats.running }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #909399">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #e6a23c">{{ stats.scheduled }}</div>
            <div class="stat-label">已配置网段</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 扫描类型切换 -->
    <el-card class="mt-4" shadow="never">
      <el-tabs v-model="activeTab" class="scan-tabs">
        <!-- 快速扫描 -->
        <el-tab-pane label="快速扫描" name="quick">
          <template #label>
            <span class="tab-label">
              <el-icon><Lightning /></el-icon>
              快速扫描
            </span>
          </template>
          <div class="scan-panel">
            <el-form label-position="top" label-width="100px">
              <el-form-item label="目标网段">
                <el-space wrap>
                  <el-input v-model.trim="quickForm.cidr" placeholder="例如: 192.168.1.0/24" style="width: 280px" />
                  <el-button type="primary" @click="startQuickScan" :loading="quickScanning" :disabled="!quickForm.cidr">
                    <el-icon v-if="!quickScanning"><Search /></el-icon>
                    开始扫描
                  </el-button>
                </el-space>
                <div class="form-help">支持 CIDR 格式，如 192.168.1.0/24，不填后缀则默认为 /24</div>
              </el-form-item>
              <el-form-item label="扫描选项">
                <el-space>
                  <el-checkbox v-model="quickForm.scanPorts">扫描端口</el-checkbox>
                  <el-checkbox v-model="quickForm.grabBanners">获取Banner</el-checkbox>
                  <el-checkbox v-model="quickForm.autoImport">自动导入新设备</el-checkbox>
                </el-space>
              </el-form-item>
            </el-form>

            <!-- 快速扫描进度 -->
            <el-card v-if="quickScanning || quickProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="quickProgress" :stroke-width="8" />
              <div class="scan-status">{{ quickStatus }}</div>
              <div class="scan-current-ip" v-if="quickCurrentIp">正在扫描: {{ quickCurrentIp }}</div>
            </el-card>

            <!-- 快速扫描结果 -->
            <div v-if="quickResults.length > 0" class="results-section">
              <div class="results-header">
                <span class="results-title">扫描结果</span>
                <el-space>
                  <span class="result-count">发现 {{ quickResults.length }} 台主机</span>
                  <el-button type="primary" size="small" @click="importAllQuickResults" :disabled="quickResults.length === 0">
                    全部导入
                  </el-button>
                </el-space>
              </div>
              <el-table :data="quickResults" row-key="ip" :pagination="false" size="small">
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
                    <el-button size="small" type="primary" link @click="importSingleQuick(row)">导入</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- IP 扫描 -->
        <el-tab-pane label="IP 扫描" name="ip">
          <template #label>
            <span class="tab-label">
              <el-icon><Connection /></el-icon>
              IP 扫描
            </span>
          </template>
          <div class="scan-panel">
            <el-form label-position="top" label-width="100px">
              <el-form-item label="目标网段">
                <el-space wrap>
                  <el-input v-model.trim="ipForm.cidr" placeholder="例如: 192.168.1.0/24" style="width: 280px" />
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

            <!-- IP 扫描进度 -->
            <el-card v-if="ipScanning || ipProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="ipProgress" :stroke-width="8" />
              <div class="scan-status">{{ ipStatus }}</div>
              <div class="scan-current-ip" v-if="ipCurrentIp">正在扫描: {{ ipCurrentIp }}</div>
            </el-card>

            <!-- IP 扫描结果 -->
            <div v-if="ipResults.length > 0" class="results-section">
              <div class="results-header">
                <span class="results-title">扫描结果</span>
                <el-space>
                  <span class="result-count">发现 {{ ipResults.length }} 台主机</span>
                  <el-button type="primary" size="small" @click="importSelectedIpDevices" :disabled="selectedIpDevices.length === 0">
                    导入选中 ({{ selectedIpDevices.length }})
                  </el-button>
                </el-space>
              </div>
              <el-table
                v-model:selection="selectedIpDevices"
                :data="ipResults"
                row-key="ip"
                :pagination="false"
                @selection-change="onIpSelectionChange"
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
                    <el-button size="small" type="primary" link @click="importSingleIpDevice(row)">导入</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- ARP 扫描 -->
        <el-tab-pane label="ARP 扫描" name="arp">
          <template #label>
            <span class="tab-label">
              <el-icon><DataAnalysis /></el-icon>
              ARP 扫描
            </span>
          </template>
          <div class="scan-panel">
            <el-form label-position="top" label-width="100px">
              <el-form-item label="目标网段">
                <el-space wrap>
                  <el-input v-model.trim="arpForm.cidr" placeholder="例如: 192.168.1.0/24" style="width: 280px" />
                  <el-button type="primary" @click="startArpScan" :loading="arpScanning" :disabled="!arpForm.cidr">
                    <el-icon v-if="!arpScanning"><Search /></el-icon>
                    开始扫描
                  </el-button>
                  <el-button @click="stopArpScan" :disabled="!arpScanning" type="warning">停止</el-button>
                </el-space>
                <div class="form-help">ARP 扫描通过读取本地 ARP 缓存发现同网段设备，需要 root 权限</div>
              </el-form-item>
            </el-form>

            <!-- ARP 扫描进度 -->
            <el-card v-if="arpScanning || arpProgress > 0" size="small" shadow="never" class="progress-card">
              <el-progress :percentage="arpProgress" :stroke-width="8" />
              <div class="scan-status">{{ arpStatus }}</div>
            </el-card>

            <!-- ARP 扫描结果 -->
            <div v-if="arpResults.length > 0" class="results-section">
              <div class="results-header">
                <span class="results-title">ARP 扫描结果</span>
                <span class="result-count">发现 {{ arpResults.length }} 条记录</span>
              </div>
              <el-table :data="arpResults" row-key="ip" :pagination="false" size="small">
                <el-table-column label="IP地址" prop="ip" width="150" />
                <el-table-column label="MAC地址" prop="mac" width="180" />
                <el-table-column label="设备类型" prop="os_type" width="120" />
                <el-table-column label="厂商标识" prop="vendor" show-overflow-tooltip />
                <el-table-column label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">
                      {{ row.status === 'up' ? '在线' : '离线' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="响应时间" prop="response_time" width="100">
                  <template #default="{ row }">{{ row.response_time ? row.response_time + 'ms' : '-' }}</template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" type="primary" link @click="importArpDevice(row)">导入</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- SNMP 扫描 -->
        <el-tab-pane label="SNMP 扫描" name="snmp">
          <template #label>
            <span class="tab-label">
              <el-icon><Monitor /></el-icon>
              SNMP 扫描
            </span>
          </template>
          <div class="scan-panel">
            <el-form label-position="top" label-width="100px">
              <el-form-item label="目标地址">
                <el-space wrap>
                  <el-input v-model.trim="snmpForm.target" placeholder="例如: 192.168.1.1" style="width: 220px" />
                  <el-select v-model="snmpForm.version" placeholder="SNMP版本" style="width: 120px">
                    <el-option label="v1" value="v1" />
                    <el-option label="v2c" value="v2c" />
                    <el-option label="v3" value="v3" />
                  </el-select>
                  <el-input v-model.trim="snmpForm.community" placeholder="Community" style="width: 160px" />
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
            <div v-if="snmpDevices.length > 0" class="results-section">
              <div class="results-header">
                <span class="results-title">SNMP 设备列表</span>
                <span class="result-count">共 {{ snmpDevices.length }} 台设备</span>
              </div>
              <el-table :data="snmpDevices" row-key="ip" :pagination="false" size="small">
                <el-table-column label="IP地址" prop="ip" width="150" />
                <el-table-column label="设备名称" prop="hostname" show-overflow-tooltip />
                <el-table-column label="描述" prop="sys_descr" show-overflow-tooltip />
                <el-table-column label="厂商" prop="vendor" width="120" />
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
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 已配置扫描任务 -->
    <el-card class="mt-4" shadow="never">
      <template #header>
        <div class="card-header">
          <span>已配置的扫描任务</span>
          <el-button size="small" @click="openAddDialog">添加任务</el-button>
        </div>
      </template>
      <el-table :data="scanConfigs" v-loading="loadingConfig" row-key="id" :pagination="configPagination">
        <el-table-column label="网段" prop="cidr" width="180" />
        <el-table-column label="名称" prop="name" min-width="150" show-overflow-tooltip />
        <el-table-column label="扫描类型" prop="scan_type" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ scanTypeText(row.scan_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="自动扫描" prop="auto_scan" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.auto_scan ? 'success' : 'info'" size="small">
              {{ row.auto_scan ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后扫描" prop="last_scan" width="170">
          <template #default="{ row }">{{ row.last_scan ? row.last_scan.slice(0, 16) : '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="runScanTask(row)">执行</el-button>
            <el-button size="small" type="info" link @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="deleteConfig(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    <el-empty v-if="!loading && networkList.length === 0" description="暂无数据" />
    </el-card>

    <!-- 添加/编辑扫描任务对话框 -->
    <el-dialog v-model="showAddDialog" :title="editingConfig ? '编辑扫描任务' : '新建扫描任务'" width="500px" destroy-on-close>
      <el-form label-position="top" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model.trim="editForm.name" placeholder="例如: 生产网段扫描" />
        </el-form-item>
        <el-form-item label="目标网段">
          <el-input v-model.trim="editForm.cidr" placeholder="192.168.1.0/24" />
        </el-form-item>
        <el-form-item label="扫描类型">
          <el-select v-model="editForm.scan_type" style="width: 100%">
            <el-option label="IP 扫描" value="ip" />
            <el-option label="ARP 扫描" value="arp" />
            <el-option label="SNMP 扫描" value="snmp" />
          </el-select>
        </el-form-item>
        <el-form-item label="自动扫描">
          <el-space>
            <el-switch v-model="editForm.auto_scan" />
            <span class="form-help">启用后按调度自动执行扫描</span>
          </el-space>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="editForm.description" type="textarea" :rows="2" placeholder="可选描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveConfig">保存</el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- SNMP 设备详情弹窗 -->
    <el-dialog v-model="snmpDetailVisible" title="SNMP 设备详情" width="600px" destroy-on-close>
      <el-descriptions v-if="snmpDetailData" :column="2" border direction="vertical" size="default">
        <el-descriptions-item label="IP地址">{{ snmpDetailData.ip }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ snmpDetailData.device_type || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ snmpDetailData.hostname || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运行时间">{{ snmpDetailData.sys_uptime ? formatUptime(snmpDetailData.sys_uptime) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ snmpDetailData.sys_descr || '-' }}</el-descriptions-item>
        <el-descriptions-item label="厂商">{{ snmpDetailData.vendor || '-' }}</el-descriptions-item>
        <el-descriptions-item label="位置">{{ snmpDetailData.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ snmpDetailData.contact || '-' }}</el-descriptions-item>
      </el-descriptions>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Lightning, Connection, Monitor, DataAnalysis } from '@element-plus/icons-vue'
import { discovery } from '@/api'

// ── Tab 状态 ──────────────────────────────────────────────
const activeTab = ref('quick')
const loadingConfig = ref(false)

// ── 统计数据 ──────────────────────────────────────────────
const stats = reactive({ total: 0, running: 0, completed: 0, scheduled: 0 })

// ── 快速扫描 ──────────────────────────────────────────────
const quickScanning = ref(false)
const quickProgress = ref(0)
const quickStatus = ref('')
const quickCurrentIp = ref('')
const quickResults = ref([])

const quickForm = reactive({
  cidr: '',
  scanPorts: true,
  grabBanners: true,
  autoImport: true
})

function normalizeCIDR(input) {
  const trimmed = input.trim()
  if (!trimmed) return ''
  if (!trimmed.includes('/')) {
    const parts = trimmed.split('.')
    if (parts.length === 4) {
      return `${parts[0]}.${parts[1]}.${parts[2]}.0/24`
    }
    return trimmed
  }
  return trimmed
}

async function startQuickScan() {
  if (!quickForm.cidr) return
  const normalizedCidr = normalizeCIDR(quickForm.cidr)
  quickScanning.value = true
  quickProgress.value = 0
  quickStatus.value = '正在启动扫描任务...'
  quickResults.value = []
  quickCurrentIp.value = ''

  try {
    const token = localStorage.getItem('token')

    const startRes = await fetch('/api/v1/discovery/scan-and-import-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        cidr: normalizedCidr,
        scan_ports: quickForm.scanPorts,
        grab_banners: quickForm.grabBanners
      })
    })

    if (!startRes.ok) throw new Error(`启动扫描失败 HTTP ${startRes.status}`)
    const { scan_id } = await startRes.json()

    while (true) {
      await new Promise(r => setTimeout(r, 1000))

      const pollRes = await fetch(`/api/v1/discovery/scan-and-import-stream/${scan_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!pollRes.ok) continue

      const data = await pollRes.json()
      const { status, progress, result, error } = data

      if (progress) {
        const { complete = 0, total = 0, current_ip = '', phase = '' } = progress
        if (total > 0) quickProgress.value = Math.round(complete / total * 100)
        if (current_ip) quickCurrentIp.value = current_ip
        if (phase === 'scanning') {
          quickStatus.value = `正在扫描 ${current_ip}（${complete}/${total}）`
        } else if (phase === 'importing') {
          quickStatus.value = `正在导入 ${current_ip}（${complete}/${total}）`
        }
      }

      if (status === 'done') {
        quickProgress.value = 100
        const discovered = result?.total_discovered || 0
        const imported = result?.newly_imported || 0
        quickStatus.value = `扫描完成，发现 ${discovered} 台主机，已导入 ${imported} 台新设备`
        quickResults.value = result?.hosts || []
        if (discovered > 0) {
          if (imported > 0) {
            ElMessage.success(`发现 ${discovered} 台主机，导入 ${imported} 台新设备到设备列表`)
          } else {
            ElMessage.info(`发现 ${discovered} 台主机（均已存在，无需重复导入）`)
          }
        } else {
          ElMessage.warning('未发现新设备')
        }
        break
      } else if (status === 'error') {
        quickProgress.value = 0
        quickStatus.value = `扫描失败: ${error}`
        ElMessage.error(`扫描失败: ${error}`)
        break
      }
    }
  } catch (e) {
    quickProgress.value = 0
    quickStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`扫描失败: ${e.message}`)
  } finally {
    quickScanning.value = false
    quickCurrentIp.value = ''
  }
}

async function importSingleQuick(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/scan-and-import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32' })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      quickResults.value = quickResults.value.filter(r => r.ip !== row.ip)
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

async function importAllQuickResults() {
  if (!quickResults.value.length) return
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        ips: quickResults.value.map(h => h.ip),
        device_type: 'server'
      })
    })
    if (res.ok) {
      ElMessage.success(`成功导入 ${quickResults.value.length} 台设备`)
      quickResults.value = []
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

// ── IP 扫描 ───────────────────────────────────────────────
const ipScanning = ref(false)
const ipProgress = ref(0)
const ipStatus = ref('')
const ipCurrentIp = ref('')
const ipResults = ref([])
const selectedIpDevices = ref([])

const ipForm = reactive({
  cidr: '',
  scanPorts: true,
  grabBanners: true,
  snmpDetect: false
})

async function startIpScan() {
  if (!ipForm.cidr) return
  ipScanning.value = true
  ipProgress.value = 0
  ipStatus.value = '正在启动扫描任务...'
  ipResults.value = []
  selectedIpDevices.value = []
  ipCurrentIp.value = ''

  try {
    const token = localStorage.getItem('token')

    const startRes = await fetch('/api/v1/discovery/scan-and-import-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        cidr: normalizeCIDR(ipForm.cidr),
        scan_ports: ipForm.scanPorts,
        grab_banners: ipForm.grabBanners
      })
    })

    if (!startRes.ok) throw new Error(`启动扫描失败 HTTP ${startRes.status}`)
    const { scan_id } = await startRes.json()

    while (true) {
      await new Promise(r => setTimeout(r, 1000))
      const pollRes = await fetch(`/api/v1/discovery/scan-and-import-stream/${scan_id}`, {
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
        break
      } else if (status === 'error') {
        ipProgress.value = 0
        ipStatus.value = `扫描失败: ${error}`
        ElMessage.error(`扫描失败: ${error}`)
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

function onIpSelectionChange(keys) {
  selectedIpDevices.value = keys
}

async function importSelectedIpDevices() {
  if (!selectedIpDevices.value.length) return
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ ips: selectedIpDevices.value.map(h => h.ip), device_type: 'server' })
    })
    if (res.ok) {
      ElMessage.success(`成功导入 ${selectedIpDevices.value.length} 台设备`)
      ipResults.value = ipResults.value.filter(r => !selectedIpDevices.value.map(h => h.ip).includes(r.ip))
      selectedIpDevices.value = []
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

async function importSingleIpDevice(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/scan-and-import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: row.ip + '/32' })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      ipResults.value = ipResults.value.filter(r => r.ip !== row.ip)
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

async function startArpScan() {
  if (!arpForm.cidr) return
  arpScanning.value = true
  arpProgress.value = 0
  arpStatus.value = '正在执行 ARP 扫描...'
  arpResults.value = []

  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/discovery/arp/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ cidr: normalizeCIDR(arpForm.cidr) })
    })

    if (!res.ok) throw new Error(`扫描失败 HTTP ${res.status}`)
    const data = await res.json()

    arpProgress.value = 100
    arpResults.value = data.hosts || []
    arpStatus.value = `扫描完成，发现 ${arpResults.value.length} 条记录`
    ElMessage.success(arpStatus.value)
  } catch (e) {
    arpProgress.value = 0
    arpStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`扫描失败: ${e.message}`)
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
      body: JSON.stringify({ ips: [row.ip], device_type: 'server' })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      arpResults.value = arpResults.value.filter(r => r.ip !== row.ip)
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

// ── SNMP 扫描 ──────────────────────────────────────────────
const snmpScanning = ref(false)
const snmpProgress = ref(0)
const snmpStatus = ref('')
const snmpDevices = ref([])
const snmpDetailVisible = ref(false)
const snmpDetailData = ref({})

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
      body: JSON.stringify({
        target: snmpForm.target,
        community: snmpForm.community,
        snmp_version: snmpForm.version
      })
    })

    if (!res.ok) throw new Error(`扫描失败 HTTP ${res.status}`)
    const data = await res.json()

    snmpProgress.value = 100
    snmpDevices.value = data.devices || [data] || []
    snmpStatus.value = `扫描完成，发现 ${snmpDevices.value.length} 台 SNMP 设备`
    ElMessage.success(snmpStatus.value)
  } catch (e) {
    snmpProgress.value = 0
    snmpStatus.value = `扫描失败: ${e.message}`
    ElMessage.error(`扫描失败: ${e.message}`)
  } finally {
    snmpScanning.value = false
  }
}

function showSnmpDetail(row) {
  snmpDetailData.value = row
  snmpDetailVisible.value = true
}

async function importSnmpDevice(row) {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/v1/discovery/devices/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ ips: [row.ip], device_type: 'server' })
    })
    if (res.ok) {
      ElMessage.success('设备导入成功')
      snmpDevices.value = snmpDevices.value.filter(d => d.ip !== row.ip)
      if (snmpDetailVisible.value) snmpDetailVisible.value = false
    } else {
      const err = await res.json().catch(() => ({}))
      ElMessage.error(`导入失败: ${err.message || res.status}`)
    }
  } catch (e) {
    ElMessage.error(`导入失败: ${e.message}`)
  }
}

function formatUptime(seconds) {
  if (!seconds) return '-'
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (days > 0) return `${days}天 ${hours}小时`
  if (hours > 0) return `${hours}小时 ${minutes}分钟`
  return `${minutes}分钟`
}

// ── 扫描配置管理 ────────────────────────────────────────────
const scanConfigs = ref([])
const showAddDialog = ref(false)
const editingConfig = ref(null)
const editForm = ref({ name: '', cidr: '', scan_type: 'ip', auto_scan: false, description: '' })

const configPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
  layout: 'prev, pager, next',
  onCurrentChange: (page) => {
    configPagination.page = page
    loadConfigs()
  }
})

async function loadConfigs() {
  loadingConfig.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/discovery/networks', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      scanConfigs.value = data.items || data || []
      configPagination.total = scanConfigs.value.length
    } else {
      scanConfigs.value = []
    }
    updateStats()
  } catch (e) {
    scanConfigs.value = []
  } finally {
    loadingConfig.value = false
  }
}

function updateStats() {
  stats.total = scanConfigs.value.length
  stats.running = scanConfigs.value.filter(c => c.status === 'running').length
  stats.completed = scanConfigs.value.filter(c => c.status === 'done').length
  stats.scheduled = scanConfigs.value.filter(c => c.auto_scan).length
}

function openAddDialog() {
  editingConfig.value = null
  editForm.value = { name: '', cidr: '', scan_type: 'ip', auto_scan: false, description: '' }
  showAddDialog.value = true
}

function openEditDialog(row) {
  editingConfig.value = row
  editForm.value = {
    name: row.name || '',
    cidr: row.cidr || '',
    scan_type: row.scan_type || 'ip',
    auto_scan: row.auto_scan || false,
    description: row.description || ''
  }
  showAddDialog.value = true
}

async function saveConfig() {
  if (!editForm.value.cidr) {
    ElMessage.warning('请输入网段')
    return
  }

  const token = localStorage.getItem('token')
  try {
    if (editingConfig.value) {
      const res = await fetch(`/api/v1/discovery/networks/${editingConfig.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(editForm.value)
      })
      if (res.ok) {
        const updated = await res.json()
        const idx = scanConfigs.value.findIndex(c => c.id === editingConfig.value.id)
        if (idx !== -1) scanConfigs.value[idx] = updated
        ElMessage.success('任务已更新')
      } else {
        ElMessage.error('更新失败')
      }
    } else {
      const res = await fetch('/api/v1/discovery/networks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(editForm.value)
      })
      if (res.ok) {
        const newConfig = await res.json()
        scanConfigs.value.push(newConfig)
        ElMessage.success('任务已保存')
        updateStats()
      } else {
        scanConfigs.value.push({ id: Date.now(), ...editForm.value })
        ElMessage.success('任务已保存（本地存储）')
      }
    }
    showAddDialog.value = false
  } catch (e) {
    ElMessage.error(`保存失败: ${e.message}`)
  }
}

async function deleteConfig(row) {
  await ElMessageBox.confirm(`确定删除该网络配置吗？`, '删除确认', { type: 'warning' })
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/discovery/networks/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      scanConfigs.value = scanConfigs.value.filter(c => c.id !== row.id)
      ElMessage.success('任务已删除')
      updateStats()
    } else {
      scanConfigs.value = scanConfigs.value.filter(c => c.id !== row.id)
      ElMessage.success('任务已删除（本地）')
    }
  } catch (e) {
    scanConfigs.value = scanConfigs.value.filter(c => c.id !== row.id)
    ElMessage.success('任务已删除（本地）')
  }
}

async function runScanTask(row) {
  if (row.scan_type === 'ip') {
    ipForm.cidr = row.cidr
    activeTab.value = 'ip'
    await startIpScan()
  } else if (row.scan_type === 'arp') {
    arpForm.cidr = row.cidr
    activeTab.value = 'arp'
    await startArpScan()
  } else if (row.scan_type === 'snmp') {
    snmpForm.target = row.cidr
    activeTab.value = 'snmp'
    await startSnmpScan()
  }
}

// ── 辅助函数 ───────────────────────────────────────────────
function scanTypeText(type) {
  const map = { ip: 'IP扫描', arp: 'ARP扫描', snmp: 'SNMP扫描' }
  return map[type] || type
}

function statusText(status) {
  const map = { pending: '待执行', running: '进行中', done: '已完成', error: '失败' }
  return map[status] || status
}

function statusType(status) {
  const map = { pending: 'info', running: 'warning', done: 'success', error: 'danger' }
  return map[status] || 'info'
}

// ── 初始化 ─────────────────────────────────────────────────
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.page-subtitle {
  margin: 4px 0 0;
  color: #909399;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  margin-top: 4px;
  font-size: 14px;
  color: #909399;
}

.mt-4 {
  margin-top: 16px;
}

.scan-tabs .tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.scan-panel {
  padding: 20px 0;
}

.form-help {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.progress-card {
  margin-top: 16px;
}

.scan-status {
  margin-top: 8px;
  font-size: 14px;
  color: #303133;
}

.scan-current-ip {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.results-section {
  margin-top: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.results-title {
  font-size: 16px;
  font-weight: 500;
}

.result-count {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
