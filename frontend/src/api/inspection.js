import request from './request'

/**
 * 巡检 API
 */
const inspection = {
  // ========== 巡检任务 ==========
  tasks: {
    getList: (params) => request.get('/inspection/tasks', { params }),
    getById: (id) => request.get(`/inspection/tasks/${id}`),
    create: (data) => request.post('/inspection/tasks', data),
    update: (id, data) => request.put(`/inspection/tasks/${id}`, data),
    delete: (id) => request.delete(`/inspection/tasks/${id}`)
  },

  // ========== 巡检结果 ==========
  results: {
    getByTaskId: (taskId, params) => request.get(`/inspection/tasks/${taskId}/results`, { params })
  },

  // ========== 巡检报告 ==========
  reports: {
    getByTaskId: (taskId, params) => request.get(`/inspection/tasks/${taskId}/reports`, { params }),
    getTemplate: (params) => request.get('/inspection/reports/template', { params }),
    export: (taskId, params) => request.get(`/inspection/tasks/${taskId}/reports/export`, { params, responseType: 'blob' })
  },

  // ========== 统计 ==========
  statistics: {
    getSummary: (params) => request.get('/inspection/statistics/summary', { params })
  }
}

export default inspection
