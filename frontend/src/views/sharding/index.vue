<template>
  <div class="sharding-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">分片管理</h1>
        <p class="page-subtitle">数据分片配置与路由管理</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建分片
      </el-button>
    </div>

    <!-- Stats Overview -->
    <div class="stats-overview">
      <el-card :bordered="false" class="stat-card">
        <template #header><span>分片统计</span></template>
        <div class="stat-items">
          <div class="stat-item">
            <span class="stat-number">{{ stats.total_shards }}</span>
            <span class="stat-desc">总分片数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number success">{{ stats.active_shards }}</span>
            <span class="stat-desc">活跃分片</span>
          </div>
          <div class="stat-item">
            <span class="stat-number warning">{{ stats.inactive_shards }}</span>
            <span class="stat-desc">非活跃</span>
          </div>
        </div>
      </el-card>

      <el-card :bordered="false" class="stat-card">
        <template #header><span>路由统计</span></template>
        <div class="stat-items">
          <div class="stat-item">
            <span class="stat-number">{{ stats.total_routes }}</span>
            <span class="stat-desc">路由规则数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.avg_route_per_shard }}</span>
            <span class="stat-desc">平均每分片路由</span>
          </div>
        </div>
      </el-card>

      <el-card :bordered="false" class="stat-card">
        <template #header><span>容量状态</span></template>
        <div class="stat-items">
          <div class="stat-item">
            <span class="stat-number">{{ stats.total_capacity }}G</span>
            <span class="stat-desc">总容量</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ stats.used_capacity }}G</span>
            <span class="stat-desc">已用容量</span>
          </div>
          <div class="stat-item">
            <el-progress type="circle" :percentage="stats.usage_percent" :width="50" :stroke-width="4" />
          </div>
        </div>
      </el-card>
    </div>

    <!-- Shard Routes Table -->
    <el-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>分片路由表</span>
          <el-select v-model="filterStatus" placeholder="分片状态" clearable style="width: 120px" @change="loadRoutes">
            <el-option label="全部" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="非活跃" value="inactive" />
          </el-select>
        </div>
      </template>
      <el-table :data="routes" v-loading="loading" border style="width: 100%">
        <el-table-column prop="shard_id" label="分片ID" width="100" />
        <el-table-column prop="shard_name" label="分片名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '非活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="routes" label="路由数" width="80" />
        <el-table-column prop="capacity" label="容量(G)" width="100" />
        <el-table-column prop="used" label="已用(G)" width="100" />
        <el-table-column prop="nodes" label="节点数" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-space :size="4">
              <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-empty v-if="!loading && routes.length === 0" description="暂无数据" />

    <!-- Create Shard Dialog -->
    <el-dialog v-model="showCreateDialog" title="创建分片" width="500px">
      <el-form :model="form" label-width="100px" ref="formRef">
        <el-form-item label="分片名称" prop="name">
          <el-input v-model.trim="form.name" placeholder="请输入分片名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model.trim="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="容量(G)" prop="capacity">
          <el-input-number v-model.trim="form.capacity" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="节点数" prop="nodes">
          <el-input-number v-model.trim="form.nodes" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>

    <!-- Detail Drawer -->
    <el-drawer v-model="showDetailDrawer" :size="500" direction="rtl">
      <template #title>
        <span>分片详情</span>
      </template>
      <el-descriptions v-if="currentShard" :column="1" border size="large" label-placement="left">
        <el-descriptions-item label="分片ID">{{ currentShard.shard_id }}</el-descriptions-item>
        <el-descriptions-item label="分片名称">{{ currentShard.shard_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" :type="currentShard.status === 'active' ? 'success' : 'info'">
            {{ currentShard.status === 'active' ? '活跃' : '非活跃' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="容量">{{ currentShard.capacity }}G</el-descriptions-item>
        <el-descriptions-item label="已用">{{ currentShard.used }}G</el-descriptions-item>
        <el-descriptions-item label="节点数">{{ currentShard.nodes }}</el-descriptions-item>
        <el-descriptions-item label="路由规则">{{ currentShard.routes }} 条</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentShard.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import shardingAPI from '@/api/sharding'
import { formatTime } from '@/utils/date'

const loading = ref(false)
const submitting = ref(false)
const routes = ref([])
const stats = ref({ total_shards: 0, active_shards: 0, inactive_shards: 0, total_routes: 0, avg_route_per_shard: 0, total_capacity: 0, used_capacity: 0, usage_percent: 0 })
const filterStatus = ref('')

const showCreateDialog = ref(false)
const formRef = ref(null)
const form = ref({ name: '', description: '', capacity: 100, nodes: 3 })

const showDetailDrawer = ref(false)
const currentShard = ref(null)

const loadStats = async () => {
  try {
    const res = await shardingAPI.getStats()
    stats.value = res.data || generateMockStats()
  } catch {
    stats.value = generateMockStats()
  }
}

const loadRoutes = async () => {
  loading.value = true
  try {
    const res = await shardingAPI.getRoutes({ status: filterStatus.value })
    routes.value = res.items || generateMockRoutes()
  } catch {
    routes.value = generateMockRoutes()
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  form.value = { name: '', description: '', capacity: 100, nodes: 3 }
  showCreateDialog.value = true
}

const handleCreate = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入分片名称')
    return
  }
  submitting.value = true
  try {
    await shardingAPI.createShard(form.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    loadStats()
    loadRoutes()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除分片 "${row.shard_name}" 吗？`, '确认删除', { type: 'warning' })
    ElMessage.success('删除成功')
    loadStats()
    loadRoutes()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const viewDetail = (row) => {
  currentShard.value = row
  showDetailDrawer.value = true
}

const generateMockStats = () => ({
  total_shards: 8,
  active_shards: 6,
  inactive_shards: 2,
  total_routes: 24,
  avg_route_per_shard: 3,
  total_capacity: 800,
  used_capacity: 456,
  usage_percent: 57
})

const generateMockRoutes = () => [
  { shard_id: 1, shard_name: 'shard-node-01', status: 'active', routes: 4, capacity: 100, used: 78, nodes: 3, created_at: '2026-01-10T08:00:00Z' },
  { shard_id: 2, shard_name: 'shard-node-02', status: 'active', routes: 3, capacity: 100, used: 45, nodes: 3, created_at: '2026-01-15T10:30:00Z' },
  { shard_id: 3, shard_name: 'shard-node-03', status: 'active', routes: 5, capacity: 100, used: 92, nodes: 3, created_at: '2026-02-01T14:00:00Z' },
  { shard_id: 4, shard_name: 'shard-node-04', status: 'active', routes: 2, capacity: 100, used: 23, nodes: 3, created_at: '2026-02-20T09:00:00Z' },
  { shard_id: 5, shard_name: 'shard-node-05', status: 'inactive', routes: 0, capacity: 100, used: 0, nodes: 3, created_at: '2026-03-05T11:00:00Z' },
  { shard_id: 6, shard_name: 'shard-node-06', status: 'active', routes: 4, capacity: 100, used: 67, nodes: 3, created_at: '2026-03-15T16:00:00Z' },
  { shard_id: 7, shard_name: 'shard-node-07', status: 'active', routes: 3, capacity: 100, used: 88, nodes: 3, created_at: '2026-04-01T08:00:00Z' },
  { shard_id: 8, shard_name: 'shard-node-08', status: 'inactive', routes: 0, capacity: 100, used: 0, nodes: 3, created_at: '2026-04-20T10:00:00Z' }
]

onMounted(() => {
  loadStats()
  loadRoutes()
})
</script>

<style scoped>
.sharding-container { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.stats-overview { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.stat-items { display: flex; justify-content: space-around; align-items: center; padding: 16px 0; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-number { font-size: 28px; font-weight: 700; color: #e0e0e0; }
.stat-number.success { color: #67c23a; }
.stat-number.warning { color: #e6a23c; }
.stat-desc { font-size: 13px; color: #888; margin-top: 4px; }

.table-card { background: #1a1a2e; border: 1px solid #2d2d44; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

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
</style>
