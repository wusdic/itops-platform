import request from './request'

export const auth = {
  login: (data) => request.post('/auth/login', data),
  logout: () => request.post('/auth/logout'),
  getUserInfo: () => request.get('/auth/userinfo'),
  register: (data) => request.post('/auth/register', data),
  changePassword: (data) => request.put('/auth/password', data),
  refreshToken: () => request.post('/auth/refresh'),
  // LDAP SSO
  ldapLogin: (data) => request.post('/auth/ldap-login', data),
  ldapStatus: () => request.get('/auth/ldap/status')
}

export const user = {
  getList: (params) => request.get('/admin/users', { params }),
  getById: (id) => request.get(`/admin/users/${id}`),
  create: (data) => request.post('/admin/users', data),
  update: (id, data) => request.put(`/admin/users/${id}`, data),
  delete: (id) => request.delete(`/admin/users/${id}`),
  resetPassword: (id) => request.post(`/admin/users/${id}/reset-password`),
  changeStatus: (id, status) => request.post(`/admin/users/${id}/status`, { status })
}

export const role = {
  getList: (params) => request.get('/admin/roles', { params }),
  getById: (id) => request.get(`/admin/roles/${id}`),
  create: (data) => request.post('/admin/roles', data),
  update: (id, data) => request.put(`/admin/roles/${id}`, data),  // 后端已实现 PUT /api/v1/roles/{role_id}
  delete: (id) => request.delete(`/admin/roles/${id}`),
  getPermissions: (id) => request.get(`/admin/permissions`)
}

export const menu = {
  getList: () => request.get('/admin/menu'),
  getById: (id) => request.get(`/admin/menu/${id}`),
  create: (data) => request.post('/admin/menu', data),
  update: (id, data) => request.put(`/admin/menu/${id}`, data),
  delete: (id) => request.delete(`/admin/menu/${id}`)
}

export const dict = {
  getList: (params) => request.get('/admin/dict', { params }),
  getById: (id) => request.get(`/admin/dict/${id}`),
  create: (data) => request.post('/admin/dict', data),
  update: (id, data) => request.put(`/admin/dict/${id}`, data),
  delete: (id) => request.delete(`/admin/dict/${id}`),
  getItems: (typeId, params) => request.get(`/admin/dict/${typeId}/items`, { params }),
  deleteItem: (itemId) => request.delete(`/admin/dict/items/${itemId}`),
  createItem: (data) => request.post('/admin/dict/items', data),
  updateItem: (itemId, data) => request.put(`/admin/dict/items/${itemId}`, data)
}

export const config = {
  getList: () => request.get('/admin/config'),
  getByKey: (key) => request.get(`/admin/config/${key}`),  // 后端无此路由，已记录为架构缺陷
  update: (key, data) => request.put(`/admin/config/${key}`, data)
}

export const system = {
  getInfo: () => request.get('/admin/info'),
  getMetrics: () => request.get('/admin/metrics'),
  getLogs: (params) => request.get('/admin/logs', { params }),
  getHealth: () => request.get('/admin/health'),
  clearCache: () => request.post('/admin/cache/clear'),
  getApiKeys: (params) => request.get('/admin/api-keys', { params }),
  createApiKey: (data) => request.post('/admin/api-keys', data),
  getApiKeyById: (id) => request.get(`/admin/api-keys/${id}`),
  updateApiKey: (id, data) => request.put(`/admin/api-keys/${id}`, data),
  deleteApiKey: (id) => request.delete(`/admin/api-keys/${id}`),
  revokeApiKey: (id) => request.post(`/admin/api-keys/${id}/revoke`),
  activateApiKey: (id) => request.post(`/admin/api-keys/${id}/activate`),
  rotateApiKey: (id) => request.post(`/admin/api-keys/${id}/rotate`)
}

/**
 * 协议适配器 API
 */
export const adapters = {
  // ========== 适配器模板 ==========
  /**
   * 获取协议适配器模板列表
   * @param {Object} params - 查询参数
   * @param {number} [params.page=1] - 页码
   * @param {number} [params.page_size=20] - 每页数量
   * @param {string} [params.protocol_type] - 协议类型过滤
   */
  getTemplates: (params) => request.get('/adapters', { params }),
  
  /**
   * 创建协议适配器模板
   * @param {Object} data - 模板数据
   * @param {string} data.name - 模板名称
   * @param {string} data.protocol_type - 协议类型
   * @param {string} [data.description] - 描述
   * @param {Object} [data.default_config] - 默认配置
   * @param {boolean} [data.enabled=true] - 是否启用
   */
  createTemplate: (data) => request.post('/adapters', data),
  
  /**
   * 更新协议适配器模板
   * @param {number} adapterId - 适配器ID
   * @param {Object} data - 更新数据
   */
  updateTemplate: (adapterId, data) => request.put(`/adapters/${adapterId}`, data),
  
  /**
   * 删除协议适配器模板
   * @param {number} adapterId - 适配器ID
   */
  deleteTemplate: (adapterId) => request.delete(`/adapters/${adapterId}`),

  // ========== 设备协议配置 ==========
  /**
   * 获取设备的所有协议配置
   * @param {number} deviceId - 设备ID
   */
  getDeviceProtocols: (deviceId) => request.get(`/adapters/device/${deviceId}/protocols`),
  
  /**
   * 批量保存设备协议配置
   * @param {number} deviceId - 设备ID
   * @param {Array} data - 协议配置列表
   */
  saveDeviceProtocols: (deviceId, data) => request.put(`/adapters/device/${deviceId}/protocols`, data),
  
  /**
   * 测试设备指定协议的连通性
   * @param {number} deviceId - 设备ID
   * @param {string} protocolType - 协议类型
   */
  testDeviceProtocol: (deviceId, protocolType) => request.post(`/adapters/device/${deviceId}/protocols/${protocolType}/test`),
}
