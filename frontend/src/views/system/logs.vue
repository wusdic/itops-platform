<template>
  <div class="logs-container">
    <!-- 顶部：统计卡片 + 配置按钮 -->
    <n-space vertical :size="12" style="margin-bottom: 16px">
      <!-- 统计卡片行 -->
      <n-space v-if="logStats">
        <n-card
          v-for="cat in categories" :key="cat.key"
          size="small" style="min-width: 140px; cursor: pointer"
          :class="{ 'stat-active': activeCategory === cat.key }"
          :bordered="activeCategory === cat.key"
          @click="switchCategory(cat.key)"
        >
          <n-space vertical :size="4" align="center">
            <n-tag :type="cat.color" size="small">{{ cat.label }}</n-tag>
            <span style="font-size: 22px; font-weight: 600">{{ logStats[cat.key]?.total_items || 0 }}</span>
            <span style="font-size: 11px; color: #999">{{ logStats[cat.key]?.total_groups || 0 }} 归集组</span>
          </n-space>
        </n-card>
      </n-space>

      <!-- 操作栏：刷新 + 配置 -->
      <n-space align="center">
        <n-button size="small" @click="showConfig = !showConfig">
                <template #icon><n-icon><RefreshOutline /></n-icon></template>
          {{ showConfig ? '收起配置' : '日志配置' }}
        </n-button>
        <n-button size="small" type="warning" @click="handleCleanup" :loading="cleaning">
          清理过期日志
        </n-button>
      </n-space>

      <!-- 配置面板 -->
      <n-card v-if="showConfig" size="small" title="日志记录配置" :bordered="true" style="background: #fafafa">
        <n-alert type="info" style="margin-bottom: 12px" :show-icon="true">
          开启的日志才会被记录。默认配置已按推荐设置，适当减少日志量。
        </n-alert>
        <n-table size="small" :bordered="false" style="font-size: 13px">
          <thead>
            <tr>
              <th style="width: 120px">分类</th>
              <th>日志类型</th>
              <th style="width: 70px; text-align: center">记录</th>
              <th style="width: 100px">最低级别</th>
              <th style="width: 70px; text-align: center">归集</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="cat in configCategories" :key="cat.key">
              <tr v-for="sub in cat.items" :key="sub.sub_category">
                <td><n-tag size="tiny" :type="cat.color">{{ cat.label }}</n-tag></td>
                <td>
                  {{ sub.description }}
                  <span style="color: #bbb; font-size: 11px; margin-left: 4px">{{ sub.sub_category }}</span>
                </td>
                <td style="text-align: center">
                  <n-switch
                    :value="sub.enabled"
                    size="small"
                    @update:value="(v) => toggleEnabled(cat.key, sub.sub_category, v)"
                  />
                </td>
                <td>
                  <n-select
                    v-if="sub.enabled"
                    :value="sub.min_level"
                    :options="levelOptions"
                    size="tiny"
                    style="width: 90px"
                    @update:value="(v) => updateLevel(cat.key, sub.sub_category, v)"
                  />
                  <span v-else style="color: #ccc">-</span>
                </td>
                <td style="text-align: center">
                  <n-switch
                    :value="sub.aggregation_enabled"
                    size="small"
                    :disabled="!sub.enabled"
                    @update:value="(v) => toggleAggregation(cat.key, sub.sub_category, v)"
                  />
                </td>
              </tr>
            </template>
          </tbody>
        </n-table>
        <n-space style="margin-top: 10px">
          <n-button size="small" type="primary" @click="saveConfigs" :loading="saving">保存配置</n-button>
          <n-button size="small" @click="resetConfigs">重置默认</n-button>
        </n-space>
      </n-card>
    </n-space>

    <!-- 主内容区：归集组列表 / 归集明细 -->
    <n-card :title="currentTitle" :bordered="false">
      <template #header-extra>
        <n-space v-if="viewMode === 'detail'" align="center">
          <n-button size="tiny" @click="viewMode = 'group'; expandedGroup = null">
            ← 返回列表
          </n-button>
          <span style="color: #888; font-size: 12px">共 {{ itemTotal }} 条明细</span>
        </n-space>
        <n-space v-else align="center">
          <n-date-picker
            v-model:value="filterDateRange" type="daterange" clearable
            size="small" style="width: 240px" placeholder="日期范围"
            @update:value="loadGroups"
          />
          <n-input
            v-model:value="filterKeyword" placeholder="搜索关键词" clearable
            size="small" style="width: 160px" @keydown.enter="loadGroups"
          />
        </n-space>
      </template>

      <!-- 归集组列表（一级视图） -->
      <template v-if="viewMode === 'group'">
        <n-alert v-if="groups.length === 0 && !loadingGroup" type="info" :show-icon="true" style="margin: 20px 0">
          当前分类暂无日志记录，或已被配置关闭。
        </n-alert>

        <n-data-table
          v-if="groups.length > 0"
          :columns="groupColumns"
          :data="groups"
          :loading="loadingGroup"
          :pagination="false"
          :row-key="row => row.id"
          @row-click="(row) => openGroup(row)"
          size="small"
          :row-props="() => ({ style: 'cursor: pointer' })"
        />
      </template>

      <!-- 归集明细列表（二级视图） -->
      <template v-else>
        <n-alert v-if="groupItems.length === 0 && !loadingItems" type="info" :show-icon="true">
          该归集组暂无明细记录。
        </n-alert>

        <n-data-table
          v-if="groupItems.length > 0"
          :columns="itemColumns"
          :data="groupItems"
          :loading="loadingItems"
          :pagination="itemPaginationConfig"
          :remote="true"
          :row-key="row => row.id"
          size="small"
          :scroll-x="Math.max(800, itemColumns.reduce((s, c) => s + (c.width || 150), 0))"
        />
      </template>
    </n-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, h, onMounted, watch, nextTick } from 'vue'
import {
  NCard, NDataTable, NButton, NInput, NSelect, NDatePicker,
  NSpace, NTag, NIcon, NEmpty, NTooltip, NBadge, NAlert,
  NTable, NSwitch, useMessage, useDialog
} from 'naive-ui'
import { RefreshOutline, CogOutline } from '@vicons/ionicons5'
import { formatDate } from '@/utils/date'

const message = useMessage()
const dialog = useDialog()

// ==================== 常量 ====================
const categories = [
  { key: 'operation', label: '操作日志', color: 'success' },
  { key: 'system',   label: '系统日志',  color: 'error'    },
  { key: 'collection', label: '采集日志', color: 'warning' },
  { key: 'audit',    label: '告警审计',  color: 'info'    },
]
const configCategories = [
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
    key: 'system', label: '系统日志', color: 'error',
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
  const map = { DEBUG: 'default', INFO: 'info', WARNING: 'warning', ERROR: 'error', CRITICAL: 'error' }
  return map[lvl?.toUpperCase()] || 'default'
}

// paginationConfig 纯对象（二级视图）
const itemPaginationConfig = {
  page: 1,
  pageSize: 20,
  pageCount: 1,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (p) => {
    itemPage.value = p
    itemPaginationConfig.page = p
    loadGroupItems(expandedGroup.value?.id)
  },
  onUpdatePageSize: (s) => {
    itemPageSize.value = s
    itemPage.value = 1
    itemPaginationConfig.pageSize = s
    itemPaginationConfig.page = 1
    loadGroupItems(expandedGroup.value?.id)
  },
}

const currentTitle = computed(() => {
  if (viewMode.value === 'detail') {
    const dim = expandedGroup.value?.dimension || {}
    const parts = Object.entries(dim).filter(([k]) => k !== 'bucket').map(([k, v]) => `${k}=${v}`)
    return `归集明细 — ${parts.join(' | ') || '组 #' + expandedGroup.value?.id}`
  }
  const cat = categories.find(c => c.key === activeCategory.value)
  return `${cat?.label || ''} — 归集列表`
})

// ==================== 归集组列定义（一级视图） ====================
const groupColumns = [
  {
    title: '聚合维度',
    key: 'dimension',
    ellipsis: { tooltip: true },
    render: (row) => {
      const dim = row.dimension || {}
      return h('div', { style: 'font-size:12px; color:#555; line-height: 1.6' }, [
        ...Object.entries(dim).filter(([k]) => k !== 'bucket').map(([k, v]) =>
          h('span', { style: 'margin-right: 10px' }, `${k}: ${v}`)
        ),
        h('div', { style: 'color:#aaa; font-size:11px; margin-top: 2px' }, `首次: ${formatDate(row.first_seen)}`)
      ])
    }
  },
  {
    title: '次数',
    key: 'total_count',
    width: 90,
    align: 'center',
    render: (row) => h('span', { style: 'font-size:14px; font-weight:600; color:#18a058' }, row.total_count)
  },
  {
    title: '级别分布',
    key: 'level_distribution',
    width: 180,
    render: (row) => h('n-space', { size: 4 }, Object.entries(row.level_distribution || {}).map(([lvl, cnt]) =>
      h('n-tag', { size: 'tiny', type: levelTagType(lvl), style: 'margin:1px' }, () => `${lvl} ${cnt}`)
    ))
  },
  {
    title: '最新出现',
    key: 'last_seen',
    width: 160,
    render: (row) => formatDate(row.last_seen)
  },
  {
    title: '代表性日志',
    key: 'sample_log',
    ellipsis: { tooltip: true },
  },
]

// ==================== 明细列定义（二级视图） ====================
const itemColumns = computed(() => {
  if (activeCategory.value === 'operation') {
    return [
      { title: '时间',     key: 'created_at',  width: 170, render: (r) => formatDate(r.created_at) },
      { title: '用户',     key: 'username',    width: 100 },
      { title: '级别',     key: 'level',       width: 80,  render: (r) => h(NTag, { size: 'small', type: levelTagType(r.level) }, () => r.level || '-') },
      { title: '操作',     key: 'message',     ellipsis: { tooltip: true } },
      { title: 'IP',       key: 'ip_address',  width: 130 },
      { title: '耗时',     key: 'duration_ms',width: 80,  render: (r) => r.duration_ms != null ? `${r.duration_ms}ms` : '-' },
      { title: '资源',     key: 'resource_type', width: 100 },
      { title: '资源ID',   key: 'resource_id', width: 100, ellipsis: { tooltip: true } },
      { title: '详情',     key: 'detail',      ellipsis: { tooltip: true }, render: (r) => {
        if (!r.detail) return '-'
        try {
          const d = typeof r.detail === 'string' ? JSON.parse(r.detail) : r.detail
          return h('pre', { style: 'font-size:11px;margin:0;white-space:pre-wrap;max-width:300px' }, JSON.stringify(d, null, 2))
        } catch { return r.detail }
      }},
    ]
  }
  if (activeCategory.value === 'system') {
    return [
      { title: '时间',   key: 'created_at', width: 170, render: (r) => formatDate(r.created_at) },
      { title: '级别',  key: 'level',      width: 80,  render: (r) => h(NTag, { size: 'small', type: levelTagType(r.level) }, () => r.level || '-') },
      { title: '来源',  key: 'source',     width: 120, ellipsis: { tooltip: true } },
      { title: '消息',  key: 'message',    ellipsis: { tooltip: true } },
      { title: '原始',  key: 'raw_content', ellipsis: { tooltip: true }, render: (r) => r.raw_content ? r.raw_content.slice(0, 80) : '-' },
    ]
  }
  if (activeCategory.value === 'collection') {
    return [
      { title: '时间',     key: 'created_at',  width: 170, render: (r) => formatDate(r.created_at) },
      { title: '级别',    key: 'level',        width: 80,  render: (r) => h(NTag, { size: 'small', type: levelTagType(r.level) }, () => r.level || '-') },
      { title: '设备',    key: 'resource_id',  width: 130, ellipsis: { tooltip: true } },
      { title: '消息',    key: 'message',      ellipsis: { tooltip: true } },
      { title: '耗时',    key: 'duration_ms',  width: 80,  render: (r) => r.duration_ms != null ? `${r.duration_ms}ms` : '-' },
    ]
  }
  return [
    { title: '时间',   key: 'created_at', width: 170, render: (r) => formatDate(r.created_at) },
    { title: '级别',  key: 'level',      width: 80,  render: (r) => h(NTag, { size: 'small', type: levelTagType(r.level) }, () => r.level || '-') },
    { title: '消息',  key: 'message',     ellipsis: { tooltip: true } },
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
    message.success('配置已保存')
    await loadStats()
  } catch (e) {
    message.error(`保存失败: ${e.message}`)
  } finally {
    saving.value = false
  }
}

function resetConfigs() {
  dialog.warning({
    title: '重置默认配置',
    content: '确定将所有日志配置恢复为默认值？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
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
      message.info('已恢复默认值，请点击保存')
    }
  })
}

async function handleCleanup() {
  cleaning.value = true
  try {
    await fetchApi('/logs/cleanup', { method: 'POST' })
    message.success('过期日志已清理')
    await loadStats()
  } catch (e) {
    message.error(`清理失败: ${e.message}`)
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
      page_size: 50,  // 一级列表一次加载多组
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
    message.error(`加载归集列表失败: ${e.message}`)
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
  itemPaginationConfig.page = 1
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
    itemPaginationConfig.itemCount = itemTotal.value
    itemPaginationConfig.pageCount = Math.max(1, Math.ceil(itemTotal.value / (itemPageSize.value || 1)))
  } catch (e) {
    message.error(`加载明细失败: ${e.message}`)
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
.stat-active { border-color: var(--primary-color, #18a058); }
.clickable-row { cursor: pointer; }
.clickable-row:hover td { background: #f0fdf4; }
.group-tbody { cursor: pointer; }
.group-tbody:hover td { background: #f0fdf4; }
</style>
