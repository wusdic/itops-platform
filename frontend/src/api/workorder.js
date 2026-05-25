import request from './request'

/**
 * 工单管理 API
 */
export const workorder = {
  // 基础 CRUD
  getList: (params) => request.get('/workorders/', { params }),
  getById: (id) => request.get(`/workorders/${id}`),
  create: (data) => request.post('/workorders/', data),
  update: (id, data) => request.put(`/workorders/${id}`, data),
  delete: (id) => request.delete(`/workorders/${id}`),

  // 工单操作
  assign: (id, data) => request.post(`/workorders/${id}/assign`, data),
  approve: (id, data) => request.post(`/workorders/${id}/approve`, data),
  resolve: (id, data) => request.put(`/workorders/${id}/resolve`, data),
  close: (id, data) => request.post(`/workorders/${id}/close`, data),
  cancel: (id, data) => request.post(`/workorders/${id}/cancel`, data),

  // 分类与优先级
  getCategories: () => request.get('/workorders/categories'),
  getPriorities: () => request.get('/workorders/priorities'),

  // 统计
  getStats: () => request.get('/workorders/stats/summary'),
  getTrend: () => request.get('/workorders/stats/trend'),
  getFlows: (id) => request.get(`/workorders/${id}/flows`),
  addFlow: (id, data) => request.post(`/workorders/${id}/flows`, data),
  getApprovalFlow: (id) => request.get(`/workorders/${id}/approval-flow`),

  // 草稿
  getDraftList: () => request.get('/workorders/draft/list'),
  getDraft: (id) => request.get(`/workorders/draft/${id}`),
  saveDraft: (data) => request.post('/workorders/draft/save', data),
  deleteDraft: (id) => request.delete(`/workorders/draft/${id}`),

  // SLA
  getSla: (id) => request.get(`/workorders/${id}/sla`),
  refreshSla: (id) => request.post(`/workorders/${id}/sla/refresh`),
  startSlaTimer: (id) => request.post(`/workorders/${id}/sla/timer/start`),

  // AI 分析
  analyzeRootCause: (data) => request.post('/workorders/analyze/root-cause', null, { params: data }),
  analyzeRemediation: (data) => request.post('/workorders/analyze/remediation', null, { params: data })
}

export default workorder
