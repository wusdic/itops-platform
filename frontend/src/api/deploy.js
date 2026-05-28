import request from './request'

/**
 * 部署 API
 */
const deploy = {
  // ========== 版本 ==========
  versions: {
    getList: (params) => request.get('/deploy/versions', { params }),
    create: (data) => request.post('/deploy/versions', data),
    getByName: (name) => request.get(`/deploy/versions/${name}`),
    delete: (id) => request.delete(`/deploy/versions/${id}`)
  },

  // ========== 金丝雀发布 ==========
  canary: {
    getList: (params) => request.get('/deploy/canary', { params }),
    create: (data) => request.post('/deploy/canary', data),
    getById: (id) => request.get(`/deploy/canary/${id}`),
    delete: (id) => request.delete(`/deploy/canary/${id}`),
    promote: (id) => request.post(`/deploy/canary/${id}/promote`),
    rollback: (id) => request.post(`/deploy/canary/${id}/rollback`),
    updateWeight: (id, data) => request.put(`/deploy/canary/${id}/weight`, data),
    terminate: (id) => request.post(`/deploy/canary/${id}/terminate`)
  },

  // ========== 部署历史 ==========
  history: {
    getList: (params) => request.get('/deploy/history', { params })
  },

  // ========== 健康检查 ==========
  health: {
    getStatus: (params) => request.get('/deploy/health', { params }),
    restart: (id) => request.post(`/deploy/health/${id}/restart`)
  }
}

export default deploy
