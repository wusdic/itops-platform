<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">设备监控</h1>
        <p class="page-subtitle">查看已接入监控的设备列表及状态</p>
      </div>
      <el-button @click="loadHosts" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">监控设备</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #18a058">{{ stats.online }}</div>
            <div class="stat-label">在线</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #909399">{{ stats.offline }}</div>
            <div class="stat-label">离线</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value" style="color: #f54a45">{{ stats.error }}</div>
            <div class="stat-label">异常</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 设备列表 -->
    <el-card class="mt-4">
      <template #header>
        <span>监控主机列表</span>
      </template>
      <el-table :data="hosts" v-loading="loading" stripe>
        <el-table-column prop="name" label="设备名称" min-width="180">
          <template #default="{ row }">
            <div class="device-name">{{ row.name || row.ip }}</div>
            <div class="device-ip">{{ row.ip }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ deviceTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_collect" label="最后采集" width="180">
          <template #default="{ row }">
            {{ formatTime(row.last_collect) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewPerformance(row)">
              性能详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && hosts.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { performance } from '@/api/monitoring'

const router = useRouter()
const loading = ref(false)
const hosts = ref([])

const stats = reactive({ total: 0, online: 0, offline: 0, error: 0 })

const deviceTypeLabel = (type) => {
  const map = {
    server: '服务器',
    server_linux: 'Linux服务器',
    server_windows: 'Windows服务器',
    network: '网络设备',
    security: '安全设备',
    storage: '存储设备',
    cloud: '云资源',
    other: '其他',
  }
  return map[type] || type || '未知'
}

const formatTime = (ts) => {
  if (!ts) return '-'
  const d = new Date(ts)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

async function loadHosts() {
  loading.value = true
  try {
    const res = await performance.getHosts()
    hosts.value = res.hosts || []
    stats.total = hosts.value.length
    // 在线判断：最后采集时间在10分钟内的视为在线
    const tenMinAgo = Date.now() - 10 * 60 * 1000
    stats.online = hosts.value.filter(h => h.last_collect && new Date(h.last_collect).getTime() > tenMinAgo).length
    stats.offline = stats.total - stats.online
    stats.error = 0
  } catch (e) {
    ElMessage.error('加载监控设备失败')
  } finally {
    loading.value = false
  }
}

function viewPerformance(row) {
  router.push({ path: '/monitoring/performance', query: { host: row.ip, name: row.name } })
}

onMounted(() => {
  loadHosts()
})
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 4px 0 0; }
.stats-row { margin-bottom: 16px; }
.stat-item { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.mt-4 { margin-top: 16px; }
.device-name { font-weight: 500; }
.device-ip { font-size: 12px; color: #909399; }
</style>
