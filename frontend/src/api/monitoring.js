import request from './request'

/**
 * 设备管理 API
 */
export const devices = {
  getList: (params) => request.get('/assets/device', { params }),
  getById: (id) => request.get(`/assets/device/${id}`),
  create: (data) => request.post('/assets/device', data),
  update: (id, data) => request.put(`/assets/device/${id}`, data),
  delete: (id) => request.delete(`/assets/device/${id}`),
  getMetrics: (name) => request.get(`/devices/${name}/metrics`),
  getStatus: (name) => request.get(`/devices/${name}/status`),
  collect: (data) => request.post('/devices/collect', data),
  collectAll: () => request.post('/devices/collect/all'),
  getStats: () => request.get('/devices/stats'),
  batchOperate: (ids, action) => request.post('/assets/device/batch', { ids, action }),
  // 批量导入相关（backend实际路径: /api/v1/template, /api/v1/validate, /api/v1/simple）
  getImportTemplate: (format = 'xlsx') => request.get('/template', { params: { format }, responseType: 'blob' }),
  validateImport: (rows) => request.post('/validate', rows),
  importDevices: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  importDevicesSimple: (rows) => request.post('/simple', rows)
}

/**
 * 告警 API
 */
export const alerts = {
  getList: (params) => request.get('/monitoring/alerts', { params }),
  getById: (id) => request.get(`/monitoring/alerts/${id}`),
  create: (data) => request.post('/monitoring/alerts', data),
  update: (id, data) => request.put(`/monitoring/alerts/${id}`, data),
  delete: (id) => request.delete(`/monitoring/alerts/${id}`),
  acknowledge: (id, data) => request.put(`/monitoring/alerts/${id}/acknowledge`, data),
  resolve: (id, data) => request.put(`/monitoring/alerts/${id}/resolve`, data),
  handle: (id, data = {}) => {
    const action = data.action || 'acknowledge'
    if (action === 'resolve') {
      return request.put(`/monitoring/alerts/${id}/resolve`, { resolution: data.resolution || '' })
    }
    return request.put(`/monitoring/alerts/${id}/acknowledge`, {})
  },
  getAuditLogs: (id) => request.get(`/monitoring/alerts/${id}/audit-logs`),
  createAuditLog: (id, data) => request.post(`/monitoring/alerts/${id}/audit-logs`, data),
  getRules: () => request.get('/monitoring/rules'),
  getRule: (id) => request.get(`/monitoring/rules/${id}`),
  // 告警统计（新增）
  getStatistics: () => request.get('/monitoring/alerts/statistics'),
  // 告警转工单（新增）
  convertToWorkorder: (alertId, data) => request.post('/workorders/convert-to-workorder', { alert_id: alertId, ...data }),
}

/**
 * 性能指标 API
 */
export const performance = {
  getMetrics: (params) => request.get('/monitoring/metrics', { params }),
  collect: (data) => request.post('/monitoring/metrics/collect', data),
  getHosts: () => request.get('/monitoring/metrics/hosts'),
  getAvailable: () => request.get('/monitoring/metrics/available'),
  query: (data) => request.post('/monitoring/metrics/query', data),
  getDeviceMetricsHistory: (deviceName, metricType, hours = 24) =>
    request.get(`/devices/${deviceName}/metrics/history`, { params: { metric_type: metricType, hours } }),
  getDeviceMetrics: (deviceName) => request.get(`/devices/${deviceName}/metrics`),
  // 指标历史查询（新增）
  getMetricsHistory: (params) => request.get('/monitoring/metrics/history', { params }),
  // TopN 指标（新增）
  getMetricsTop: (metricType, limit = 10) => request.get(`/monitoring/metrics/top/${metricType}`, { params: { limit } }),
  // 仪表盘布局（供 dashboard/index.vue 调用）
  getDashboardLayout: (layoutId) => request.get('/monitoring/dashboard/layout', { params: layoutId ? { layout_id: layoutId } : {} }),
  saveDashboardLayout: (data) => request.put('/monitoring/dashboard/layout', data),
}

/**
 * 仪表盘 API
 */
export const dashboards = {
  getList: (params) => request.get('/monitoring/dashboards', { params }),
  getById: (id) => request.get(`/monitoring/dashboards/${id}`),
  getLayout: (layoutId) => request.get('/monitoring/dashboard/layout', { params: layoutId ? { layout_id: layoutId } : {} }),
  saveLayout: (data) => request.put('/monitoring/dashboard/layout', data),
  listLayouts: () => request.get('/monitoring/dashboard/layouts'),
  deleteLayout: (layoutId) => request.delete(`/monitoring/dashboard/layout/${layoutId}`),
  getStats: () => request.get('/monitoring/dashboard/stats')
}
/**
 * 维护窗口 API
 */
export const maintenanceWindows = {
  getList: (params) => request.get('/monitoring/maintenance-windows', { params }),
  getById: (id) => request.get(`/monitoring/maintenance-windows/${id}`),
  create: (data) => request.post('/monitoring/maintenance-windows', data),
  update: (id, data) => request.put(`/monitoring/maintenance-windows/${id}`, data),
  delete: (id) => request.delete(`/monitoring/maintenance-windows/${id}`)
}

/**
 * 触发规则 API
 */
export const triggerRules = {
  getList: (params) => request.get('/monitoring/trigger-rules', { params }),
  getById: (id) => request.get(`/monitoring/trigger-rules/${id}`),
  create: (data) => request.post('/monitoring/trigger-rules', data),
  update: (id, data) => request.put(`/monitoring/trigger-rules/${id}`, data),
  delete: (id) => request.delete(`/monitoring/trigger-rules/${id}`),
  test: (id) => request.post(`/monitoring/trigger-rules/${id}/test`),
  getEvents: () => request.get('/monitoring/trigger-events'),
  evaluate: (data) => request.post('/monitoring/trigger/evaluate', data)
}

/**
 * 指标配置 API
 */
export const metricConfigs = {
  getList: (params) => request.get('/monitoring/metric-configs', { params }),
  getById: (id) => request.get(`/monitoring/metric-configs/${id}`),
  create: (data) => request.post('/monitoring/metric-configs', data),
  update: (id, data) => request.patch(`/monitoring/metric-configs/${id}`, data),
  delete: (id) => request.delete(`/monitoring/metric-configs/${id}`),
  toggle: (id, data) => request.patch(`/monitoring/metric-configs/${id}/toggle`, data)
}
