import request from './request'

/**
 * 知识库 API
 */
const knowledge = {
  // 搜索
  search: (params) => request.get('/knowledge/search', { params }),

  // ========== SOP ==========
  sop: {
    getList: (params) => request.get('/knowledge/sop', { params }),
    getById: (id) => request.get(`/knowledge/sop/${id}`),
    create: (data) => request.post('/knowledge/sop', data),
    update: (id, data) => request.put(`/knowledge/sop/${id}`, data),
    delete: (id) => request.delete(`/knowledge/sop/${id}`),
    submitReview: (id) => request.post(`/knowledge/sop/${id}/review`),
    approve: (id) => request.post(`/knowledge/sop/${id}/approve`)
  },

  // ========== 故障案例 ==========
  faultCase: {
    getList: (params) => request.get('/knowledge/fault-case', { params }),
    getById: (id) => request.get(`/knowledge/fault-case/${id}`),
    create: (data) => request.post('/knowledge/fault-case', data),
    update: (id, data) => request.put(`/knowledge/fault-case/${id}`, data),
    delete: (id) => request.delete(`/knowledge/fault-case/${id}`),
    recommendSimilar: (id, data) => request.post(`/knowledge/fault-case/${id}/recommend-similar`, data)
  },

  // ========== 分类 ==========
  category: {
    getList: (params) => request.get('/knowledge/category', { params }),
    create: (data) => request.post('/knowledge/category', data),
    update: (id, data) => request.put(`/knowledge/category/${id}`, data),
    delete: (id) => request.delete(`/knowledge/category/${id}`)
  },

  // ========== 标签 ==========
  tag: {
    getList: (params) => request.get('/knowledge/tag', { params }),
    create: (data) => request.post('/knowledge/tag', data)
  },

  // ========== 统计 ==========
  getStats: () => request.get('/knowledge/stats'),

  // ========== 审核流程 ==========
  reviewFlows: {
    getList: (params) => request.get('/knowledge/review-flows', { params }),
    getById: (id) => request.get(`/knowledge/review-flows/${id}`),
    create: (data) => request.post('/knowledge/review-flows', data),
    update: (id, data) => request.put(`/knowledge/review-flows/${id}`, data),
    delete: (id) => request.delete(`/knowledge/review-flows/${id}`)
  },

  // ========== 审核记录 ==========
  reviews: {
    getList: (params) => request.get('/knowledge/reviews', { params }),
    getById: (id) => request.get(`/knowledge/reviews/${id}`),
    submit: (data) => request.post('/knowledge/reviews/submit', data),
    approve: (id) => request.post(`/knowledge/reviews/${id}/approve`),
    reject: (id) => request.post(`/knowledge/reviews/${id}/reject`),
    requestRevision: (id, data) => request.post(`/knowledge/reviews/${id}/request-revision`, data),
    withdraw: (id) => request.post(`/knowledge/reviews/${id}/withdraw`),
    resubmit: (id) => request.post(`/knowledge/reviews/${id}/resubmit`),
    getPending: () => request.get('/knowledge/reviews/pending')
  }
}

export default knowledge
