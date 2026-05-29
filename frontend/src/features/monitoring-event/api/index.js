/**
 * Monitoring Event Feature API
 */
import request from '@/api/request'

export const monitoringEvent = {
  // 告警
  alerts: {
    getList: (params) => request.get('/monitoring/alerts', { params }),
    getById: (id) => request.get(`/monitoring/alerts/${id}`),
    acknowledge: (id, data) => request.put(`/monitoring/alerts/${id}/acknowledge`, data),
    resolve: (id, data) => request.put(`/monitoring/alerts/${id}/resolve`, data),
    close: (id, data) => request.put(`/monitoring/alerts/${id}/close`, data),
    getStatistics: () => request.get('/monitoring/alerts/statistics'),
    getRules: () => request.get('/monitoring/rules'),
  },

  // 事件（来自 app/domains/event/router，路径 /api/v1/events）
  events: {
    getList: (params) => request.get('/events', { params }),
    getById: (id) => request.get(`/events/${id}`),
    create: (data) => request.post('/events', data),
  },

  // 设备指标（来自 app/domains/monitoring/router，路径 /api/v1/monitoring/metrics/*）
  metrics: {
    getLatest: (deviceName) => request.get(`/devices/${deviceName}/metrics`),
    getHistory: (deviceName, params) => request.get(`/monitoring/metrics/history`, { params: { device_name: deviceName, ...params } }),
    getTop: (type, params) => request.get(`/monitoring/metrics/top/${type}`, { params }),
  },

  // 设备
  devices: {
    getList: (params) => request.get('/assets/device', { params }),
    getStats: () => request.get('/devices/stats'),
  },
}
