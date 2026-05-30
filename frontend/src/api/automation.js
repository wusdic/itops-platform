import request from './request'

/**
 * 自动化 API
 */
const automation = {
  // ========== 脚本 ==========
  scripts: {
    getList: (params) => request.get('/automation/scripts', { params }),
    getById: (id) => request.get(`/automation/scripts/${id}`),
    create: (data) => request.post('/automation/scripts', data),
    update: (id, data) => request.put(`/automation/scripts/${id}`, data),
    delete: (id) => request.delete(`/automation/scripts/${id}`),
    execute: (id, data) => request.post(`/automation/scripts/${id}/execute`, data),
    getVersions: (id) => request.get(`/automation/scripts/${id}/versions`)
  },

  // ========== 任务 ==========
  tasks: {
    getList: (params) => request.get('/automation/tasks', { params }),
    getById: (id) => request.get(`/automation/tasks/${id}`),
    create: (data) => request.post('/automation/tasks', data),
    update: (id, data) => request.put(`/automation/tasks/${id}`, data),
    delete: (id) => request.delete(`/automation/tasks/${id}`),
    run: (id, data) => request.post(`/automation/tasks/${id}/run`, data)
  },

  // ========== 执行记录 ==========
  executions: {
    getList: (params) => request.get('/automation/executions', { params }),
    getById: (id) => request.get(`/automation/executions/${id}`),
    create: (data) => request.post('/automation/executions', data),
    getLogs: (id, params) => request.get(`/automation/executions/${id}/logs`, { params }),
    getSnapshot: (id) => request.get(`/automation/executions/${id}/snapshot`),
    rollback: (id) => request.post(`/automation/executions/${id}/rollback`)
  },

  // ========== 触发规则 ==========
  triggerRules: {
    getList: (params) => request.get('/automation/trigger-rules', { params }),
    getById: (id) => request.get(`/automation/trigger-rules/${id}`),
    create: (data) => request.post('/automation/trigger-rules', data),
    update: (id, data) => request.put(`/automation/trigger-rules/${id}`, data),
    delete: (id) => request.delete(`/automation/trigger-rules/${id}`),
    test: (id) => request.post(`/automation/trigger-rules/${id}/test`)
  },

  // ========== 审批请求 ==========
  approvals: {
    getList: (params) => request.get('/automation/approvals', { params }),
    getPending: (params) => request.get('/automation/approvals/pending', { params }),
    getById: (id) => request.get(`/automation/approvals/${id}`),
    approve: (id, data) => request.post(`/automation/approvals/${id}/approve`, data),
    reject: (id, data) => request.post(`/automation/approvals/${id}/reject`, data),
    cancel: (id) => request.post(`/automation/approvals/${id}/cancel`),
    getExecutionApproval: (executionId) => request.get(`/automation/executions/${executionId}/approval`)
  },

  // ========== 回滚历史 ==========
  rollbackHistory: {
    getList: (params) => request.get('/automation/rollback-history', { params })
  },

  // ========== 其他 ==========
  evaluate: (data) => request.post('/automation/evaluate', null, { params: data })
}

export default automation
