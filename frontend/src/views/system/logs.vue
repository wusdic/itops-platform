<template>
  <div class="logs-container">
    <!-- 顶部：统计卡片 + 配置按钮 -->
    <el-space direction="vertical" :size="12" style="margin-bottom: 16px; width: 100%">
      <!-- 统计卡片行 -->
      <el-space v-if="logStats">
        <el-card
          v-for="cat in categories" :key="cat.key"
          size="small" class="stat-card"
          :class="{ 'stat-active': activeCategory === cat.key }"
          :body-style="{ padding: '12px', textAlign: 'center' }"
          @click="switchCategory(cat.key)"
        >
          <el-space direction="vertical" :size="4" align="center">
            <el-tag :type="cat.color" size="small">{{ cat.label }}</el-tag>
            <span style="font-size: 22px; font-weight: 600">{{ logStats[cat.key]?.total_items || 0 }}</span>
            <span style="font-size: 11px; color: #999">{{ logStats[cat.key]?.total_groups || 0 }} 归集组</span>
          </el-space>
        </el-card>
      </el-space>

      <!-- 操作栏：刷新 + 配置 -->
      <el-space align="center">
        <el-button size="small" @click="showConfig = !showConfig">
          <el-icon><Refresh /></el-icon>
          {{ showConfig ? '收起配置' : '日志配置' }}
        </el-button>
        <el-button size="small" type="warning" @click="handleCleanup" :loading="cleaning">
          清理过期日志
        </el-button>
      </el-space>

      <!-- 配置面板 -->
      <el-card v-if="showConfig" size="small" title="日志记录配置" class="config-card">
        <el-alert type="info" :show-icon="true" style="margin-bottom: 12px">
          开启的日志才会被记录。默认配置已按推荐设置，适当减少日志量。
        </el-alert>
        <el-table :data="configTableData" size="small" style="font-size: 13px" max-height="400">
          <el-table-column label="分类" width="120">
            <template #default="{ row }">
              <el-tag :type="row.color" size="small">{{ row.label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="日志类型" prop="description">
            <template #default="{ row }">
              {{ row.description }}
              <span style="color: #bbb; font-size: 11px; margin-left: 4px">{{ row.sub_category }}</span>
            </template>
          </el-table-column>
          <el-table-column label="记录" width="70" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="row.enabled"
                size="small"
                @update:model-value="(v) => toggleEnabled(row.catKey, row.sub_category, v)"
              />
            </template>
          </el-table-column>
          <el-table-column label="最低级别" width="100">
            <template #default="{ row }">
              <el-select
                v-if="row.enabled"
                v-model="row.min_level"
                :options="levelOptions"
                size="small"
                style="width: 90px"
                @change="(v) => updateLevel(row.catKey, row.sub_category, v)"
              />
              <span v-else style="color: #ccc">-</span>
            </template>
          </el-table-column>
          <el-table-column label="归集" width="70" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="row.aggregation_enabled"
                size="small"
                :disabled="!row.enabled"
                @update:model-value="(v) => toggleAggregation(row.catKey, row.sub_category, v)"
              />
            </template>
          </el-table-column>
        </el-table>
        <el-space style="margin-top: 10px">
          <el-button size="small" type="primary" @click="saveConfigs" :loading="saving">保存配置</el-button>
          <el-button size="small" @click="resetConfigs">重置默认</el-button>
        </el-space>
      </el-card>
    </el-space>

    <!-- 主内容区：归集组列表 / 归集明细 -->
    <el-card :title="currentTitle">
      <template #header>
        <el-space>
          <span>{{ currentTitle }}</span>
        </el-space>
        <template v-if="viewMode === 'detail'">
          <el-space>
            <el-button size="small" @click="viewMode = 'group'; expandedGroup = null">
              ← 返回列表
            </el-button>
            <span style="color: #888; font-size: 12px">共 {{ itemTotal }} 条明细</span>
          </el-space>
        </template>
        <template v-else>
          <el-space>
            <el-date-picker
              v-model="filterDateRange"
              type="daterange"
              clearable
              size="small"
              style="width: 240px"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="loadGroups"
            />
            <el-input
              v-model="filterKeyword"
              placeholder="搜索关键词"
              clearable
              size="small"
              style="width: 160px"
              @keydown.enter="loadGroups"
            />
          </el-space>
        </template>
      </template>

      <!-- 归集组列表（一级视图） -->
      <template v-if="viewMode === 'group'">
        <el-alert v-if="groups.length === 0 && !loadingGroup" type="info" :show-icon="true" style="margin: 20px 0">
          当前分类暂无日志记录，或已被配置关闭。
        </el-alert>

        <el-table
          v-if="groups.length > 0"
          :data="groups"
          v-loading="loadingGroup"
          :pagination="false"
          row-key="id"
          size="small"
          @row-click="(row) => openGroup(row)"
          class="clickable-table"
        >
          <el-table-column label="聚合维度" prop="dimension" show-overflow-tooltip>
            <template #default="{ row }">
              <div style="font-size:12px; color:#555; line-height: 1.6">
                <span v-for="([k, v]) in Object.entries(row.dimension || {}).filter(([k]) => k !== 'bucket')" :key="k" style="margin-right: 10px">
                  {{ k }}: {{ v }}
                </span>
                <div style="color:#aaa; font-size:11px; margin-top: 2px">首次: {{ formatDate(row.first_seen) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="次数" prop="total_count" width="90" align="center">
            <template #default="{ row }">
              <span style="font-size:14px; font-weight:600; color:#18a058">{{ row.total_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="级别分布" width="180">
            <template #default="{ row }">
              <el-tag v-for="([lvl, cnt]) in Object.entries(row.level_distribution || {})" :key="lvl" :type="levelTagType(lvl)" size="small" style="margin: 1px">
                {{ lvl }} {{ cnt }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最新出现" prop="last_seen" width="160">
            <template #default="{ row }">{{ formatDate(row.last_seen) }}</template>
          </el-table-column>
          <el-table-column label="代表性日志" prop="sample_log" show-overflow-tooltip />
        </el-table>
      </template>

      <!-- 归集明细列表（二级视图） -->
      <template v-else>
        <el-alert v-if="groupItems.length === 0 && !loadingItems" type="info" :show-icon="true">
          该归集组暂无明细记录。
        </el-alert>

        <el-table
          v-if="groupItems.length > 0"
          :data="groupItems"
          v-loading="loadingItems"
          :pagination="itemPaginationConfig"
          row-key="id"
          size="small"
          :scroll-x="Math.max(800, itemColumns.reduce((s, c) => s + (c.width || 150), 0))"
        >
          <template v-for="col in itemColumns" :key="col.key">
            <el-table-column v-if="col.key === 'level'" :label="col.title" :width="col.width" :prop="col.key">
              <template #default="{ row }">
                <el-tag :type="levelTagType(row.level)" size="small">{{ row.level || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column v-else-if="col.key === 'detail'" :label="col.title" :prop="col.key" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="!row.detail">-</span>
                <pre v-else style="font-size:11px;margin:0;white-space:pre-wrap;max-width:300px">{{ typeof row.detail === 'string' ? (() => { try { return JSON.stringify(JSON.parse(row.detail), null, 2) } catch { return row.detail } })() : JSON.stringify(row.detail, null, 2) }}</pre>
              </template>
            </el-table-column>
            <el-table-column v-else-if="col.key === 'duration_ms'" :label="col.title" :width="col.width" :prop="col.key">
              <template #default="{ row }">{{ row.duration_ms != null ? `${row.duration_ms}ms` : '-' }}</template>
            </el-table-column>
            <el-table-column v-else :label="col.title" :prop="col.key" :width="col.width" show-overflow-tooltip />
          </template>
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'

// ==================== 常量 ====================
const categories = [
  { key: 'operation', label: '操作日志', color: 'success' },
  { key: 'system',   label: '系统日志',  color: 'danger'    },
  { key: 'collection', label: '采集日志', color: 'warning' },
  { key: 'audit',    label: '告警审计',  color: 'info'    },
]

const configCategoriesRaw = [
  {
    key: 'operation', label: '操作日志', color: 'success',
    items: [
      { sub_category: 'login', description: '登录/登出', enabled: true, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'device_crud', description: '设备增删改查', enabled: true, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'alert_action', description: '告警状态变更', enabled: true, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'workorder_crud', description: '工单增删改', enabled: true, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'adapter_credential', description: '适配器/凭证变更', enabled: false, min_level: 'INFO', aggregation_enabled: true },
    ]
  },
  {
    key: 'system', label: '系统日志', color: 'danger',
    items: [
      { sub_category: 'error', description: 'ERROR 及以上', enabled: true, min_level: 'ERROR', aggregation_enabled: true },
      { sub_category: 'warning', description: 'WARNING 及以上', enabled: true, min_level: 'WARNING', aggregation_enabled: true },
      { sub_category: 'info', description: 'INFO（量大，默认关闭）', enabled: false, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'debug', description: 'DEBUG（最大量，默认关闭）', enabled: false, min_level: 'DEBUG', aggregation_enabled: true },
    ]
  },
  {
    key: 'collection', label: '采集日志', color: 'warning',
    items: [
      { sub_category: 'success', description: '采集成功（量大，默认关闭）', enabled: false, min_level: 'INFO', aggregation_enabled: true },
      { sub_category: 'failed', description: '采集失败', enabled: true, min_level: 'ERROR', aggregation_enabled: true },
      { sub_category: 'offline', description: '设备离线', enabled: true, min_level: 'WARNING', aggregation_enabled: true },
    ]
  },
  {
    key: 'audit', label: '告警审计', color: 'info',
    items: [
      { sub_category: 'all', description: '全部告警操作', enabled: true, min_level: 'INFO', aggregation_enabled: true },
    ]
  },
]

// Flatten for el-table display
const configTableData = computed(() => {
  const result = []
  for (const cat of configCategoriesRaw) {
    for (const sub of cat.items) {
      result.push({ ...sub, catKey: cat.key, label: cat.label, color: cat.color })
    }
  }
  return result
})

const configCategories = configCategoriesRaw

const levelOptions = [
  { label: 'DEBUG',   value: 'DEBUG'    },
  { label: 'INFO',    value: 'INFO'     },
  { label: 'WARNING', value: 'WARNING'  },
  { label: 'ERROR',   value: 'ERROR'    },
  { label: 'CRITICAL', value: 'CRITICAL' },
]

// ==================== 状态 ====================
const activeCategory = ref('operation')
const viewMode = ref('group')    // 'group' | 'detail'
const expandedGroup = ref(null)

const showConfig = ref(false)
const saving = ref(false)
const cleaning = ref(false)
const logStats = ref(null)
const loadingGroup = ref(false)
const loadingItems = ref(false)
const groups = ref([])
const groupItems = ref([])

// 过滤器
const filterKeyword = ref('')
const filterDateRange = ref(null)

// 分页 refs（用于一级列表的 itemPaginationConfig）
const itemPage = ref(1)
const itemPageSize = ref(20)
const itemTotal = ref(0)

const levelTagType = (lvl) => {
  const map = { DEBUG: 'info', INFO: 'info', WARNING: 'warning', ERROR: 'danger', CRITICAL: 'danger' }
  return map[lvl?.toUpperCase()] || 'info'
}

// paginationConfig 纯对象（二级视图）
const itemPaginationConfig = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0,
  pageSizes: [10, 20, 50, 100],
  layout: 'sizes, prev, pager, next',
  onCurrentChange: (p) => {
    itemPage.value = p
    itemPaginationConfig.currentPage = p
    loadGroupItems(expandedGroup.value?.id)
  },
  onSizeChange: (s) => {
    itemPageSize.value = s
    itemPage.value = 1
    itemPaginationConfig.pageSize = s
    itemPaginationConfig.currentPage = 1
    loadGroupItems(expandedGroup.value?.id)
  },
})

const currentTitle = computed(() => {
  if (viewMode.value === 'detail') {
    const dim = expandedGroup.value?.dimension || {}
    const parts = Object.entries(dim).filter(([k]) => k !== 'bucket').map(([k, v]) => `${k}=${v}`)
    return `归集明细 — ${parts.join(' | ') || '组 #' + expandedGroup.value?.id}`
  }
  const cat = categories.find(c => c.key === activeCategory.value)
  return `${cat?.label || ''} — 归集列表`
})

// ==================== 明细列定义（二级视图） ====================
const itemColumns = computed(() => {
  if (activeCategory.value === 'operation') {
    return [
      { title: '时间',     key: 'created_at',  width: 170 },
      { title: '用户',     key: 'username',    width: 100 },
      { title: '级别',     key: 'level',       width: 80  },
      { title: '操作',     key: 'message' },
      { title: 'IP',       key: 'ip_address',  width: 130 },
      { title: '耗时',     key: 'duration_ms',width: 80  },
      { title: '资源',     key: 'resource_type', width: 100 },
      { title: '资源ID',   key: 'resource_id', width: 100 },
      { title: '详情',     key: 'detail' },
    ]
  }
  if (activeCategory.value === 'system') {
    return [
      { title: '时间',   key: 'created_at', width: 170 },
      { title: '级别',  key: 'level',      width: 80  },
      { title: '来源',  key: 'source',     width: 120 },
      { title: '消息',  key: 'message' },
      { title: '原始',  key: 'raw_content' },
    ]
  }
  if (activeCategory.value === 'collection') {
    return [
      { title: '时间',     key: 'created_at',  width: 170 },
      { title: '级别',    key: 'level',        width: 80  },
      { title: '设备',    key: 'resource_id',  width: 130 },
      { title: '消息',    key: 'message' },
      { title: '耗时',    key: 'duration_ms',  width: 80  },
    ]
  }
  return [
    { title: '时间',   key: 'created_at', width: 170 },
    { title: '级别',  key: 'level',      width: 80  },
    { title: '消息',  key: 'message' },
  ]
})

// ==================== API ====================
const apiBase = '/api/v1/admin'

async function fetchApi(path, opts = {}) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${apiBase}${path}`, {
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  return res.json()
}

// 加载统计数据
async function loadStats() {
  try {
    logStats.value = await fetchApi('/log-stats')
  } catch (e) {
    logStats.value = { operation: { total_items: 0, total_groups: 0 }, system: { total_items: 0, total_groups: 0 }, collection: { total_items: 0, total_groups: 0 }, audit: { total_items: 0, total_groups: 0 } }
  }
}

// 加载配置
async function loadConfigs() {
  try {
    const data = await fetchApi('/log-configs')
    const items = data.items || []
    // 回填 configCategories
    for (const cat of configCategories) {
      for (const sub of cat.items) {
        const remote = items.find(i => i.category === cat.key && i.sub_category === sub.sub_category)
        if (remote) {
          sub.enabled = remote.enabled
          sub.min_level = remote.min_level
          sub.aggregation_enabled = remote.aggregation_enabled
        }
      }
    }
  } catch (e) {
    // log-configs failed silently
  }
}

// 保存配置
async function saveConfigs() {
  saving.value = true
  try {
    const payload = configCategories.flatMap(cat =>
      cat.items.map(sub => ({
        category: cat.key,
        sub_category: sub.sub_category,
        enabled: sub.enabled,
        min_level: sub.min_level,
        aggregation_enabled: sub.aggregation_enabled,
      }))
    )
    await fetchApi('/log-configs', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    ElMessage.success('配置已保存')
    await loadStats()
  } catch (e) {
    ElMessage.error(`保存失败: ${e.message}`)
  } finally {
    saving.value = false
  }
}

function resetConfigs() {
  ElMessageBox.confirm('确定将所有日志配置恢复为默认值？', '重置默认配置', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    const defaults = [
      { cat: 'operation', sub: 'login',         enabled: true,  min_level: 'INFO'     },
      { cat: 'operation', sub: 'device_crud',   enabled: true,  min_level: 'INFO'     },
      { cat: 'operation', sub: 'alert_action',  enabled: true,  min_level: 'INFO'     },
      { cat: 'operation', sub: 'workorder_crud',enabled: true,  min_level: 'INFO'     },
      { cat: 'operation', sub: 'adapter_credential', enabled: false, min_level: 'INFO' },
      { cat: 'system',    sub: 'error',          enabled: true,  min_level: 'ERROR'    },
      { cat: 'system',    sub: 'warning',        enabled: true,  min_level: 'WARNING'  },
      { cat: 'system',    sub: 'info',          enabled: false, min_level: 'INFO'     },
      { cat: 'system',    sub: 'debug',         enabled: false, min_level: 'DEBUG'    },
      { cat: 'collection',sub: 'success',        enabled: false, min_level: 'INFO'     },
      { cat: 'collection',sub: 'failed',         enabled: true,  min_level: 'ERROR'    },
      { cat: 'collection',sub: 'offline',        enabled: true,  min_level: 'WARNING'  },
      { cat: 'audit',     sub: 'all',            enabled: true,  min_level: 'INFO'     },
    ]
    for (const cat of configCategories) {
      for (const sub of cat.items) {
        const def = defaults.find(d => d.cat === cat.key && d.sub === sub.sub_category)
        if (def) {
          sub.enabled = def.enabled
          sub.min_level = def.min_level
          sub.aggregation_enabled = true
        }
      }
    }
    ElMessage.info('已恢复默认值，请点击保存')
  }).catch(e => ElMessage.error('操作失败: ' + (e.message || e)))
}

async function handleCleanup() {
  cleaning.value = true
  try {
    await fetchApi('/admin/logs/cleanup', { method: 'POST' })
    ElMessage.success('过期日志已清理')
    await loadStats()
  } catch (e) {
    ElMessage.error(`清理失败: ${e.message}`)
  } finally {
    cleaning.value = false
  }
}

// 切换分类
function switchCategory(cat) {
  activeCategory.value = cat
  viewMode.value = 'group'
  expandedGroup.value = null
  itemPage.value = 1
  itemPageSize.value = 20
  filterKeyword.value = ''
  filterDateRange.value = null
  loadGroups()
}

// 加载归集组
async function loadGroups() {
  loadingGroup.value = true
  try {
    const params = new URLSearchParams({
      category: activeCategory.value,
      page: 1,
      page_size: 50,
    })
    if (filterKeyword.value) params.set('keyword', filterKeyword.value)
    if (filterDateRange.value && filterDateRange.value[0]) {
      params.set('start_date', new Date(filterDateRange.value[0]).toISOString())
      params.set('end_date',   new Date(filterDateRange.value[1]).toISOString())
    }
    const data = await fetchApi(`/logs/groups?${params}`)
    groups.value = data.items || []
    itemTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error(`加载归集列表失败: ${e.message}`)
    groups.value = []
  } finally {
    loadingGroup.value = false
  }
}

// 点击归集组 → 进入明细
async function openGroup(row) {
  expandedGroup.value = row
  viewMode.value = 'detail'
  itemPage.value = 1
  itemPageSize.value = 20
  itemPaginationConfig.currentPage = 1
  itemPaginationConfig.pageSize = 20
  itemTotal.value = row.total_count || 0
  await loadGroupItems(row.id)
}

// 加载归集明细
async function loadGroupItems(groupId) {
  loadingItems.value = true
  try {
    const params = new URLSearchParams({
      page: itemPage.value,
      page_size: itemPageSize.value,
    })
    const data = await fetchApi(`/logs/groups/${groupId}/items?${params}`)
    groupItems.value = data.items || []
    itemTotal.value = data.total || 0
    itemPaginationConfig.total = itemTotal.value
  } catch (e) {
    ElMessage.error(`加载明细失败: ${e.message}`)
    groupItems.value = []
  } finally {
    loadingItems.value = false
  }
}

// ==================== 配置面板操作 ====================
function toggleEnabled(cat, sub, val) {
  const item = configCategories.find(c => c.key === cat)?.items.find(i => i.sub_category === sub)
  if (item) item.enabled = val
}

function updateLevel(cat, sub, val) {
  const item = configCategories.find(c => c.key === cat)?.items.find(i => i.sub_category === sub)
  if (item) item.min_level = val
}

function toggleAggregation(cat, sub, val) {
  const item = configCategories.find(c => c.key === cat)?.items.find(i => i.sub_category === sub)
  if (item) item.aggregation_enabled = val
}

// ==================== 生命周期 ====================
onMounted(async () => {
  await Promise.all([loadStats(), loadConfigs(), loadGroups()])
})
</script>

<style scoped>
.logs-container { padding: 16px; }
.stat-active { border-color: var(--el-color-primary); }
.stat-card { cursor: pointer; min-width: 140px; }
.stat-card:hover { border-color: var(--el-color-primary); }
.clickable-table { cursor: pointer; }
.clickable-table:hover >>> tr:hover td { background: #f0fdf4; }
.config-card >>> .el-card__header { padding: 12px 16px; }
</style>
