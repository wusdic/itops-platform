import request from './request'

/**
 * 租户 API
 */
const tenants = {
  // 基础 CRUD
  getList: (params) => request.get('/tenants', { params }),
  getById: (id) => request.get(`/tenants/${id}`),
  create: (data) => request.post('/tenants', data),
  update: (id, data) => request.put(`/tenants/${id}`, data),
  delete: (id) => request.delete(`/tenants/${id}`),

  // 租户用户
  getUsers: (id, params) => request.get(`/tenants/${id}/users`, { params }),
  assignUser: (id, data) => request.post(`/tenants/${id}/users`, data),
  removeUser: (id, userId) => request.delete(`/tenants/${id}/users/${userId}`),

  // 配额
  getQuota: (id) => request.get(`/tenants/${id}/quota`)
}

export default tenants
