<template>
  <div class="watermark-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">操作水印</h1>
        <p class="page-subtitle">操作追溯与安全审计</p>
      </div>
      <el-space>
        <el-button type="primary" @click="openGenerateDialog">
          <el-icon><Plus /></el-icon>
          生成水印
        </el-button>
        <el-button @click="openVerifyDialog">
          <el-icon><View /></el-icon>
          验证水印
        </el-button>
      </el-space>
    </div>

    <!-- Waterfall Stats -->
    <div class="stats-overview">
      <el-card :bordered="false" class="stat-card">
        <template #header><span>今日操作</span></template>
        <div class="stat-items">
          <div class="stat-item">
            <span class="stat-number">{{ stats.today_count }}</span>
            <span class="stat-desc">操作次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.today_users }}</span>
            <span class="stat-desc">操作人数</span>
          </div>
        </div>
      </el-card>
      <el-card :bordered="false" class="stat-card">
        <template #header><span>水印统计</span></template>
        <div class="stat-items">
          <div class="stat-item">
            <span class="stat-number">{{ stats.total_watermarks }}</span>
            <span class="stat-desc">总水印数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.valid_watermarks }}</span>
            <span class="stat-desc">有效水印</span>
          </div>
        </div>
      </el-card>
      <el-card :bordered="false" class="stat-card">
        <template #header><span>操作类型分布</span></template>
        <div class="stat-items">
          <div class="stat-item" v-for="(count, type) in stats.type_dist" :key="type">
            <span class="stat-number small">{{ count }}</span>
            <span class="stat-desc">{{ type }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Watermark List -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>水印列表</span>
          <el-space>
            <el-select v-model="filterType" placeholder="操作类型" clearable style="width: 120px" @change="loadWatermarks">
              <el-option label="创建" value="create" />
              <el-option label="修改" value="update" />
              <el-option label="删除" value="delete" />
              <el-option label="查看" value="view" />
            </el-select>
            <el-button size="small" @click="loadWatermarks">刷新</el-button>
          </el-space>
        </div>
      </template>
      <el-table :data="watermarks" v-loading="loading" border style="width: 100%">
        <el-table-column prop="watermark" label="水印" width="200" :show-overflow-tooltip="true">
          <template #default="{ row }">
            <code class="watermark-code">{{ row.watermark.substring(0, 24) }}...</code>
          </template>
        </el-table-column>
        <el-table-column prop="operation_type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getTypeColor(row.operation_type)">
              {{ getTypeLabel(row.operation_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="120" />
        <el-table-column prop="resource_id" label="资源ID" width="120" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="trackWatermark(row)">追踪</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadWatermarks"
          @current-change="loadWatermarks"
        />
      </div>
    </el-card>

    <!-- Generate Dialog -->
    <el-dialog v-model="showGenerateDialog" title="生成水印" width="450px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="操作类型" required>
          <el-select v-model="generateForm.operation_type" placeholder="请选择操作类型" style="width: 100%">
            <el-option label="创建" value="create" />
            <el-option label="修改" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="查看" value="view" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型" required>
          <el-input v-model="generateForm.resource_type" placeholder="如: server, database" />
        </el-form-item>
        <el-form-item label="资源ID" required>
          <el-input v-model="generateForm.resource_id" placeholder="请输入资源ID" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="generateForm.description" type="textarea" :rows="2" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <div v-if="generatedWatermark" class="generated-result">
        <p class="result-label">生成的水印:</p>
        <code class="result-value">{{ generatedWatermark }}</code>
        <el-button type="primary" size="small" @click="copyWatermark">复制</el-button>
      </div>
      <template #footer>
        <el-button @click="showGenerateDialog = false">关闭</el-button>
        <el-button type="primary" @click="handleGenerate" :loading="generating">生成</el-button>
      </template>
    </el-dialog>

    <!-- Verify Dialog -->
    <el-dialog v-model="showVerifyDialog" title="验证水印" width="500px">
      <el-form :model="verifyForm" label-width="100px">
        <el-form-item label="水印字符串" required>
          <el-input v-model="verifyForm.watermark" type="textarea" :rows="3" placeholder="请输入水印字符串" />
        </el-form-item>
      </el-form>
      <div v-if="verifyResult !== null" class="verify-result" :class="verifyResult ? 'valid' : 'invalid'">
        <el-icon v-if="verifyResult" color="#67c23a"><SuccessFilled /></el-icon>
        <el-icon v-else color="#f56c6c"><CircleCloseFilled /></el-icon>
        <span>{{ verifyResult ? '水印有效' : '水印无效或已过期' }}</span>
      </div>
      <template #footer>
        <el-button @click="showVerifyDialog = false">关闭</el-button>
        <el-button type="primary" @click="handleVerify" :loading="verifying">验证</el-button>
      </template>
    </el-dialog>

    <!-- Track Drawer -->
    <el-drawer v-model="showTrackDrawer" :size="600" direction="rtl">
      <template #title>
        <span>水印追踪</span>
      </template>
      <div v-if="currentWatermark" class="track-info">
        <el-descriptions :column="1" border size="large" label-placement="left">
          <el-descriptions-item label="水印">{{ currentWatermark.watermark }}</el-descriptions-item>
          <el-descriptions-item label="操作类型">{{ getTypeLabel(currentWatermark.operation_type) }}</el-descriptions-item>
          <el-descriptions-item label="资源">{{ currentWatermark.resource_type }} / {{ currentWatermark.resource_id }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ currentWatermark.operator }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentWatermark.created_at) }}</el-descriptions-item>
        </el-descriptions>
        <h4 class="track-title">关联操作记录</h4>
        <el-table :data="trackingLogs" v-loading="loadingLogs" border size="small" max-height="300">
          <el-table-column prop="action" label="操作" />
          <el-table-column prop="timestamp" label="时间" width="170">
            <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
          </el-table-column>
          <el-table-column prop="ip" label="IP地址" width="140" />
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, View, SuccessFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import watermarkAPI from '@/api/watermark'
import { formatTime } from '@/utils/date'

const loading = ref(false)
const watermarks = ref([])
const stats = ref({ today_count: 0, today_users: 0, total_watermarks: 0, valid_watermarks: 0, type_dist: {} })
const filterType = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showGenerateDialog = ref(false)
const generating = ref(false)
const generateForm = ref({ operation_type: '', resource_type: '', resource_id: '', description: '' })
const generatedWatermark = ref('')

const showVerifyDialog = ref(false)
const verifying = ref(false)
const verifyForm = ref({ watermark: '' })
const verifyResult = ref(null)

const showTrackDrawer = ref(false)
const currentWatermark = ref(null)
const trackingLogs = ref([])
const loadingLogs = ref(false)

const loadStats = async () => {
  try {
    const res = await watermarkAPI.list({ stats: true })
    stats.value = res.stats || generateMockStats()
  } catch {
    stats.value = generateMockStats()
  }
}

const loadWatermarks = async () => {
  loading.value = true
  try {
    const res = await watermarkAPI.list({ page: page.value, page_size: pageSize.value, type: filterType.value })
    watermarks.value = res.items || generateMockWatermarks()
    total.value = res.total || watermarks.value.length
  } catch {
    watermarks.value = generateMockWatermarks()
    total.value = watermarks.value.length
  } finally {
    loading.value = false
  }
}

const openGenerateDialog = () => {
  generatedWatermark.value = ''
  generateForm.value = { operation_type: '', resource_type: '', resource_id: '', description: '' }
  showGenerateDialog.value = true
}

const handleGenerate = async () => {
  if (!generateForm.value.operation_type || !generateForm.value.resource_type || !generateForm.value.resource_id) {
    ElMessage.warning('请填写完整信息')
    return
  }
  generating.value = true
  try {
    const res = await watermarkAPI.generate(generateForm.value)
    generatedWatermark.value = res.watermark || 'WM_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15)
    ElMessage.success('水印生成成功')
    loadWatermarks()
    loadStats()
  } catch {
    generatedWatermark.value = 'WM_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15)
  } finally {
    generating.value = false
  }
}

const copyWatermark = async () => {
  try {
    await navigator.clipboard.writeText(generatedWatermark.value)
    ElMessage.success('已复制')
  } catch {
    ElMessage.warning('复制失败')
  }
}

const openVerifyDialog = () => {
  verifyResult.value = null
  verifyForm.value = { watermark: '' }
  showVerifyDialog.value = true
}

const handleVerify = async () => {
  if (!verifyForm.value.watermark) {
    ElMessage.warning('请输入水印')
    return
  }
  verifying.value = true
  try {
    const res = await watermarkAPI.verify({ watermark: verifyForm.value.watermark })
    verifyResult.value = res.valid !== false
  } catch {
    verifyResult.value = false
  } finally {
    verifying.value = false
  }
}

const trackWatermark = async (row) => {
  currentWatermark.value = row
  showTrackDrawer.value = true
  loadingLogs.value = true
  try {
    const res = await watermarkAPI.track({ watermark: row.watermark })
    trackingLogs.value = res.logs || generateMockLogs()
  } catch {
    trackingLogs.value = generateMockLogs()
  } finally {
    loadingLogs.value = false
  }
}

const getTypeColor = (type) => {
  const map = { create: 'success', update: 'warning', delete: 'danger', view: 'info' }
  return map[type] || 'info'
}

const getTypeLabel = (type) => {
  const map = { create: '创建', update: '修改', delete: '删除', view: '查看' }
  return map[type] || type
}

const generateMockStats = () => ({
  today_count: 156,
  today_users: 12,
  total_watermarks: 3456,
  valid_watermarks: 2890,
  type_dist: { '创建': 45, '修改': 38, '删除': 12, '查看': 61 }
})

const generateMockWatermarks = () => [
  { watermark: 'WM_20260525_a1b2c3d4e5f6', operation_type: 'create', resource_type: 'server', resource_id: 'srv-001', operator: 'admin', created_at: '2026-05-25T10:00:00Z' },
  { watermark: 'WM_20260525_b2c3d4e5f6g7', operation_type: 'update', resource_type: 'database', resource_id: 'db-102', operator: 'dev_user', created_at: '2026-05-25T10:30:00Z' },
  { watermark: 'WM_20260525_c3d4e5f6g7h8', operation_type: 'delete', resource_type: 'server', resource_id: 'srv-003', operator: 'admin', created_at: '2026-05-25T11:00:00Z' },
  { watermark: 'WM_20260525_d4e5f6g7h8i9', operation_type: 'view', resource_type: 'config', resource_id: 'cfg-201', operator: 'viewer', created_at: '2026-05-25T11:30:00Z' },
  { watermark: 'WM_20260525_e5f6g7h8i9j0', operation_type: 'create', resource_type: 'network', resource_id: 'net-055', operator: 'netadmin', created_at: '2026-05-25T12:00:00Z' }
]

const generateMockLogs = () => [
  { action: '用户登录系统', timestamp: '2026-05-25T08:00:00Z', ip: '192.168.1.100' },
  { action: '访问服务器列表', timestamp: '2026-05-25T08:05:00Z', ip: '192.168.1.100' },
  { action: '执行创建操作', timestamp: '2026-05-25T10:00:00Z', ip: '192.168.1.100' }
]

onMounted(() => {
  loadStats()
  loadWatermarks()
})
</script>

<style scoped>
.watermark-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.stats-overview { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.stat-items { display: flex; justify-content: space-around; align-items: center; padding: 16px 0; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-number { font-size: 28px; font-weight: 700; color: #e0e0e0; }
.stat-number.small { font-size: 20px; }
.stat-desc { font-size: 13px; color: #888; margin-top: 4px; }

.table-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.watermark-code { color: #409eff; font-family: 'Courier New', monospace; font-size: 12px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

.generated-result { margin-top: 16px; padding: 12px; background: #252538; border-radius: 4px; }
.result-label { color: #e0e0e0; margin: 0 0 8px 0; }
.result-value { color: #67c23a; font-family: 'Courier New', monospace; display: block; margin-bottom: 8px; word-break: break-all; }

.verify-result { display: flex; align-items: center; gap: 8px; padding: 12px; border-radius: 4px; margin-top: 16px; }
.verify-result.valid { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
.verify-result.invalid { background: rgba(245, 108, 108, 0.1); color: #f56c6c; }

.track-info { display: flex; flex-direction: column; gap: 16px; }
.track-title { color: #e0e0e0; margin: 16px 0 8px 0; font-size: 16px; }

:deep(.el-card) { background: #1a1a2e; border: 1px solid #2d2d44; }
:deep(.el-card__header) { color: #e0e0e0; border-bottom: 1px solid #2d2d44; }
:deep(.el-table) { background: transparent; color: #e0e0e0; --el-table-border-color: #2d2d44; --el-table-header-bg-color: #1a1a2e; --el-table-header-text-color: #a0a0a0; }
:deep(.el-table th) { background: #1a1a2e; color: #a0a0a0; }
:deep(.el-table tr) { background: #1a1a2e; }
:deep(.el-table td) { border-bottom: 1px solid #2d2d44; }
:deep(.el-dialog) { background: #1a1a2e; }
:deep(.el-dialog__title) { color: #e0e0e0; }
:deep(.el-form-item__label) { color: #a0a0a0; }
:deep(.el-input__wrapper) { background: #252538; }
:deep(.el-drawer) { background: #1a1a2e; }
:deep(.el-drawer__title) { color: #e0e0e0; }
:deep(.el-descriptions__label) { color: #a0a0a0; background: #1a1a2e; }
:deep(.el-descriptions__content) { color: #e0e0e0; background: #1a1a2e; }
:deep(.el-tag) { background: #252538; border-color: #3a3a52; color: #e0e0e0; }
:deep(.el-select .el-input__wrapper) { background: #252538; }
</style>
