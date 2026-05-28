import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { devices, alerts, workorder } from '@/api'
import { performance as monitorApi } from '@/api/monitoring'
import { ElMessage } from 'element-plus'

/**
 * 仪表盘 Store
 * 统一管理仪表盘数据、布局状态、加载状态
 */
export const useDashboardStore = defineStore('dashboard', () => {
  // ========== 状态 ==========
  
  // 加载状态
  const loading = ref(false)
  const alertsLoading = ref(false)
  const workordersLoading = ref(false)
  const saving = ref(false)

  // 错误状态
  const error = ref(null)

  // 布局状态
  const showCustomize = ref(false)
  const layoutModified = ref(false)
  const currentLayout = ref(null)
  const layoutId = ref(null)
  
  // 所有部件
  const allItems = ref([])

  // 统计数据
  const statCardValues = ref([0, 0, 0, 0])
  
  // 告警/设备/健康状态
  const alertStats = ref({ critical: 0, warning: 0, info: 0 })
  const deviceStats = ref({ online: 0, offline: 0, warning: 0 })
  const systemHealth = ref({ cpu: 0, memory: 0, disk: 0 })

  // 表格数据
  const recentAlerts = ref([])
  const pendingOrders = ref([])

  // ========== 计算属性 ==========

  const statWidgets = computed(() => 
    allItems.value.filter(i => i.widget?.widget_type?.startsWith('stat_'))
  )

  const healthWidget = computed(() => 
    allItems.value.find(i => i.widget?.widget_type === 'health_status')
  )

  const chartWidgets = computed(() => 
    allItems.value.filter(i => ['alert_chart', 'device_status_chart'].includes(i.widget?.widget_type))
  )

  const tableWidgets = computed(() => 
    allItems.value.filter(i => ['recent_alerts_table', 'pending_workorders_table'].includes(i.widget?.widget_type))
  )

  // ========== 工具方法 ==========

  /**
   * 三级错误处理 + 静默降级
   * @param {Function} apiCall - API 调用
   * @param {*} fallback - 降级默认值
   * @param {boolean} showError - 是否显示错误提示
   */
  const fetchWithErrorHandling = async (apiCall, fallback = null, showError = true) => {
    try {
      return await apiCall()
    } catch (err) {
      if (err.response) {
        const status = err.response.status
        if (status === 401) {
          ElMessage.warning('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          return fallback
        }
        if (status === 403) {
          ElMessage.warning('没有权限访问')
          return fallback
        }
        if (showError && err.response.data?.msg) {
          ElMessage.error(err.response.data.msg)
        }
      } else if (err.request) {
        if (showError) ElMessage.error('网络连接失败，请检查网络')
      }
      return fallback
    }
  }

  /**
   * 生成趋势数据（7天）
   */
  const generateTrendData = (items, dateField) => {
    const now = new Date()
    const dates = []
    const values = []

    for (let i = 6; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

      const dayStart = new Date(date)
      dayStart.setHours(0, 0, 0, 0)
      const dayEnd = new Date(date)
      dayEnd.setHours(23, 59, 59, 999)

      const count = items.filter(item => {
        if (!item[dateField]) return false
        const itemDate = new Date(item[dateField])
        return itemDate >= dayStart && itemDate <= dayEnd
      }).length

      values.push(count)
    }

    return { dates, values }
  }

  // ========== Actions ==========

  /**
   * 加载完整仪表盘数据
   */
  const loadDashboard = async () => {
    loading.value = true
    error.value = null

    try {
      // Step 1: 加载布局
      try {
        const layoutRes = await monitorApi.getDashboardLayout()
        const layout = layoutRes?.data || layoutRes
        if (layout && layout.items) {
          currentLayout.value = layout
          layoutId.value = layout.layout_id
          allItems.value = (layout.items || []).map(item => ({
            ...item,
            collapsed: item.collapsed || false,
            visibility: item.visibility !== false
          }))
        }
      } catch (e) {
        console.warn('Failed to load layout, using defaults:', e)
        allItems.value = []
      }

      // Step 2: 并行加载业务数据
      const [statsRes, alertRes, workorderRes, healthRes] = await Promise.allSettled([
        fetchWithErrorHandling(() => devices.getStats(), { total: 0, online: 0, offline: 0, warning: 0 }),
        fetchWithErrorHandling(() => alerts.getList({ page: 1, page_size: 10 }), { items: [], total: 0 }),
        fetchWithErrorHandling(() => workorder.getList({ page: 1, page_size: 10, status: 'pending' }), { items: [], total: 0 }),
        fetchWithErrorHandling(() => devices.getStats(), null, false)
      ])

      // 处理设备统计
      if (statsRes.status === 'fulfilled' && statsRes.value) {
        const data = statsRes.value
        if (typeof data.total === 'number') {
          statCardValues.value = [
            data.total,
            data.online || 0,
            statCardValues.value[2],
            data.pending_orders || 0
          ]
          deviceStats.value.online = data.online || 0
          deviceStats.value.offline = data.offline || 0
        }
      }

      // 处理告警
      if (alertRes.status === 'fulfilled' && alertRes.value) {
        const data = alertRes.value
        const items = Array.isArray(data) ? data : (data.items || [])
        recentAlerts.value = items.slice(0, 10)
        alertStats.value.critical = items.filter(a => ['critical', 'high'].includes(a.level)).length
        alertStats.value.warning = items.filter(a => ['medium', 'warning'].includes(a.level)).length
        alertStats.value.info = items.filter(a => ['low', 'info'].includes(a.level)).length
        statCardValues.value[2] = items.length
        deviceStats.value.warning = items.length
      } else {
        recentAlerts.value = []
      }

      // 处理工单
      if (workorderRes.status === 'fulfilled' && workorderRes.value) {
        const data = workorderRes.value
        const items = Array.isArray(data) ? data : (data.items || [])
        pendingOrders.value = items.slice(0, 10)
        statCardValues.value[3] = data.total || items.length
      } else {
        pendingOrders.value = []
      }

      // 处理健康状态
      if (healthRes.status === 'fulfilled' && healthRes.value) {
        const data = healthRes.value
        if (data && typeof data === 'object') {
          if (data.cpu !== undefined) {
            systemHealth.value = { cpu: data.cpu || 0, memory: data.memory || 0, disk: data.disk || 0 }
          } else if (data.metrics) {
            systemHealth.value = { cpu: data.metrics.cpu || 0, memory: data.metrics.memory || 0, disk: data.metrics.disk || 0 }
          }
        }
      }

      layoutModified.value = false

    } catch (err) {
      console.error('Dashboard load error:', err)
      error.value = err.message || '加载仪表盘数据失败，请稍后重试'
      ElMessage.error('加载仪表盘数据失败')
    } finally {
      loading.value = false
    }
  }

  /**
   * 保存布局
   */
  const saveLayout = async () => {
    if (!currentLayout.value) return
    saving.value = true
    try {
      const layoutData = {
        layout_id: layoutId.value,
        name: currentLayout.value.name || '默认布局',
        description: currentLayout.value.description || '',
        grid_size: currentLayout.value.grid_size || 'medium',
        columns: currentLayout.value.columns || 12,
        row_height: currentLayout.value.row_height || 80,
        items: allItems.value.map(item => ({
          item_id: item.item_id,
          widget: item.widget,
          position: item.position,
          visibility: item.visibility,
          collapsed: item.collapsed,
          locked: item.locked || false
        })),
        column_config: currentLayout.value.column_config || [],
        theme: currentLayout.value.theme || 'default',
        is_default: currentLayout.value.is_default || false,
        is_shared: currentLayout.value.is_shared || false,
        tags: currentLayout.value.tags || []
      }
      await monitorApi.saveDashboardLayout(layoutData)
      layoutModified.value = false
      ElMessage.success('布局保存成功')
      showCustomize.value = false
    } catch (err) {
      ElMessage.error('保存布局失败')
    } finally {
      saving.value = false
    }
  }

  /**
   * 重置布局
   */
  const resetLayout = () => {
    allItems.value.forEach(item => {
      item.visibility = true
      item.collapsed = false
    })
    layoutModified.value = true
  }

  /**
   * 切换部件可见性
   */
  const toggleVisibility = (item) => {
    item.visibility = item.visibility === false ? true : false
    layoutModified.value = true
  }

  /**
   * 切换部件折叠状态
   */
  const toggleCollapse = (item) => {
    item.collapsed = !item.collapsed
    layoutModified.value = true
  }

  /**
   * 刷新单个模块数据
   */
  const refreshAlerts = async () => {
    alertsLoading.value = true
    try {
      const data = await alerts.getList({ page: 1, page_size: 10 })
      const items = Array.isArray(data) ? data : (data.items || [])
      recentAlerts.value = items.slice(0, 10)
      alertStats.value.critical = items.filter(a => ['critical', 'high'].includes(a.level)).length
      alertStats.value.warning = items.filter(a => ['medium', 'warning'].includes(a.level)).length
      alertStats.value.info = items.filter(a => ['low', 'info'].includes(a.level)).length
    } finally {
      alertsLoading.value = false
    }
  }

  const refreshWorkorders = async () => {
    workordersLoading.value = true
    try {
      const data = await workorder.getList({ page: 1, page_size: 10, status: 'pending' })
      const items = Array.isArray(data) ? data : (data.items || [])
      pendingOrders.value = items.slice(0, 10)
      statCardValues.value[3] = data.total || items.length
    } finally {
      workordersLoading.value = false
    }
  }

  return {
    // 状态
    loading,
    alertsLoading,
    workordersLoading,
    saving,
    error,
    showCustomize,
    layoutModified,
    currentLayout,
    layoutId,
    allItems,
    statCardValues,
    alertStats,
    deviceStats,
    systemHealth,
    recentAlerts,
    pendingOrders,

    // 计算属性
    statWidgets,
    healthWidget,
    chartWidgets,
    tableWidgets,

    // 工具方法
    fetchWithErrorHandling,
    generateTrendData,

    // Actions
    loadDashboard,
    saveLayout,
    resetLayout,
    toggleVisibility,
    toggleCollapse,
    refreshAlerts,
    refreshWorkorders
  }
})
