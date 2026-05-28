<template>
  <div class="system-health-page">
    <el-row :gutter="16" class="stats-grid">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
              <el-icon :size="28"><Cpu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ healthInfo.cpu || 0 }}%</div>
              <div class="stat-label">CPU 使用率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)' }">
              <el-icon :size="28"><Histogram /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ healthInfo.memory || 0 }}%</div>
              <div class="stat-label">内存使用率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: 'linear-gradient(135deg, #1890ff 0%, #69c0ff 100%)' }">
              <el-icon :size="28"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ healthInfo.disk || 0 }}%</div>
              <div class="stat-label">磁盘使用率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: 'linear-gradient(135deg, #faad14 0%, #ffc53d 100%)' }">
              <el-icon :size="28"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ healthInfo.uptime || '-' }}</div>
              <div class="stat-label">运行时间</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="mb-4">
      <template #header>
        <div class="card-header">
          <span>系统健康状态</span>
          <el-button type="primary" @click="loadHealth" :loading="loading">
            <el-icon><RefreshRight /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="系统状态">
          <el-tag :type="healthInfo.status === 'healthy' ? 'success' : 'danger'" size="small">
            {{ healthInfo.status === 'healthy' ? '正常运行' : '异常' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">{{ healthInfo.version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="数据库连接">
          <el-tag :type="healthInfo.db_connected !== false ? 'success' : 'danger'" size="small">
            {{ healthInfo.db_connected !== false ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后检查时间">{{ healthInfo.last_check || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>性能指标</span>
        </div>
      </template>
      <el-table :data="metricsList" v-loading="metricsLoading" style="width: 100%" size="small">
        <el-table-column prop="name" label="指标名称" width="200" />
        <el-table-column prop="value" label="当前值" width="150">
          <template #default="{ row }">
            <span :class="getValueClass(row.value, row.threshold)">{{ row.value }}{{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="150">
          <template #default="{ row }">{{ row.threshold }}{{ row.unit }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>
      <el-empty v-if="!metricsLoading && metricsList.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { RefreshRight, Cpu, Histogram, Coin, Timer } from '@element-plus/icons-vue'
import { system } from '@/api'

const loading = ref(false)
const metricsLoading = ref(false)
const healthInfo = ref({})
const metricsList = ref([])

async function loadHealth() {
  loading.value = true
  try {
    const data = await system.getHealth()
    healthInfo.value = data || {}
    ElMessage.success('刷新成功')
  } catch (e) {
    healthInfo.value = { status: 'unknown', version: '-' }
  } finally {
    loading.value = false
  }
}

async function loadMetrics() {
  metricsLoading.value = true
  try {
    const data = await system.getMetrics()
    metricsList.value = data.items || data || []
  } catch (e) {
    metricsList.value = []
  } finally {
    metricsLoading.value = false
  }
}

function getValueClass(value, threshold) {
  if (!threshold) return ''
  const num = parseFloat(value)
  const th = parseFloat(threshold)
  if (num >= th) return 'value-danger'
  if (num >= th * 0.8) return 'value-warning'
  return ''
}

onMounted(() => {
  loadHealth()
  loadMetrics()
})
</script>

<style scoped>
.system-health-page { padding: 16px; }
.mb-4 { margin-bottom: 16px; }
.stats-grid { margin-bottom: 16px; }
.stat-card { cursor: default; }
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 48px; height: 48px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; color: white;
}
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: #1a1a1a; line-height: 1.2; }
.stat-label { font-size: 13px; color: #8c8c8c; margin-top: 4px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.value-danger { color: #ff4d4f; font-weight: bold; }
.value-warning { color: #faad14; font-weight: bold; }
</style>
