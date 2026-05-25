import request from './request'

// 模块化 API
export { default as workorder } from './workorder'
export { default as knowledge } from './knowledge'
export { default as automation } from './automation'
export { default as discovery } from './discovery'
export { default as inspection } from './inspection'
export { default as deploy } from './deploy'
export { default as tenants } from './tenants'
export { default as apiKeys } from './apiKeys'
export { default as sharding } from './sharding'
export { default as watermark } from './watermark'

// 监控相关
export { devices, alerts, performance, dashboards, maintenanceWindows, triggerRules, metricConfigs } from './monitoring'

// 系统相关
import { auth, user, role, menu, dict, config, system } from './system'
export { auth, user, role, menu, dict, config, system }

// 资产
import { assets } from './assets'
export { assets }

// 调度
import { scheduler } from './scheduler'
export { scheduler }

// 通知
import { notification } from './notification'
export { notification }

// AI
export const ai = {
  chat: (data) => request.post('/ai/chat', data),
  getConversations: (params) => request.get('/ai/conversations', { params }),
  getConversation: (id) => request.get(`/ai/conversations/${id}`),
  deleteConversation: (id) => request.delete(`/ai/conversations/${id}`),
  pinConversation: (id) => request.put(`/ai/conversations/${id}/pin`),
  saveMessage: (id, data) => request.post(`/ai/conversations/${id}/messages`, data),
  troubleshoot: (data) => request.post('/ai/troubleshoot', data),
  troubleshootAuto: (data) => request.post('/ai/troubleshoot/auto', data),
  suggest: (data) => request.post('/ai/suggest', data),
  interpretReport: (data) => request.post('/ai/interpret/report', data),
  analyzeLogs: (data) => request.post('/ai/analyze/logs', data),
  qa: (data) => request.post('/ai/qa', data),
  getStats: () => request.get('/ai/stats')
}

// 备份（新 BackupManager API）
export const backup = {
  getList: (params) => request.get('/admin/backups', { params }),
  getById: (id) => request.get(`/admin/backups/${id}`),
  create: (data) => request.post('/admin/backups', data),
  restore: (id, data) => request.post(`/admin/backups/${id}/restore`, data),
  delete: (id) => request.delete(`/admin/backups/${id}`)
}

export { default as request } from './request'
