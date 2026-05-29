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

  // 事件
  events: {
    getList: (params) => request.get('/events', { params }),
    getById: (id) => request.get(`/events/${id}`),
    create: (data) => request.post('/events', data),
    getStats: () => request.get('/events/stats'),
  },

  // 设备指标
  metrics: {
    getLatest: (deviceName) => request.get(`/devices/${deviceName}/metrics`),
    getHistory: (deviceName, params) => request.get(`/metrics/history`, { params: { device_name: deviceName, ...params } }),
    getTop: (type, params) => request.get(`/metrics/top/${type}`, { params }),
  },

  // 设备
  devices: {
    getList: (params) => request.get('/assets/device', { params }),
    getStats: () => request.get('/devices/stats'),
  },
}
