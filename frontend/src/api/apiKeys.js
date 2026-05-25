import request from './request'

/**
 * API Key API
 */
const apiKeys = {
  getList: (params) => request.get('/api-keys', { params }),
  getById: (id) => request.get(`/api-keys/${id}`),
  create: (data) => request.post('/api-keys', data),
  update: (id, data) => request.put(`/api-keys/${id}`, data),
  delete: (id) => request.delete(`/api-keys/${id}`),

  // 状态管理
  activate: (id) => request.post(`/api-keys/${id}/activate`),
  revoke: (id) => request.post(`/api-keys/${id}/revoke`),
  rotate: (id) => request.post(`/api-keys/${id}/rotate`)
}

export default apiKeys
