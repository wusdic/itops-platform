import request from './request'

/**
 * 报表管理 API
 */
export default {
  // ========== 报表模板 ==========
  /**
   * 获取报表模板列表
   * @param {Object} params - 查询参数
   * @param {string} [params.report_type] - 报表类型
   * @param {string} [params.keyword] - 关键词搜索
   * @param {number} [params.page] - 页码
   * @param {number} [params.page_size] - 每页数量
   */
  getTemplates: (params) => request.get('/report/template', { params }),
  
  /**
   * 获取报表模板详情
   * @param {number} templateId - 模板ID
   */
  getTemplateById: (templateId) => request.get(`/report/template/${templateId}`),
  
  /**
   * 创建报表模板
   * @param {Object} data - 模板数据
   */
  createTemplate: (data) => request.post('/report/template', data),
  
  /**
   * 更新报表模板
   * @param {number} templateId - 模板ID
   * @param {Object} data - 模板数据
   */
  updateTemplate: (templateId, data) => request.put(`/report/template/${templateId}`, data),
  
  /**
   * 删除报表模板
   * @param {number} templateId - 模板ID
   */
  deleteTemplate: (templateId) => request.delete(`/report/template/${templateId}`),

  // ========== 报表生成 ==========
  /**
   * 生成报表
   * @param {Object} data - 生成参数
   * @param {number} [data.template_id] - 模板ID
   * @param {string} data.report_type - 报表类型
   * @param {string} data.name - 报表名称
   * @param {string} data.start_date - 开始日期
   * @param {string} data.end_date - 结束日期
   * @param {string} [data.format='pdf'] - 输出格式
   * @param {Object} [data.filters] - 筛选条件
   * @param {Object} [data.params] - 额外参数
   */
  generate: (data) => request.post('/report/generate', data),
  
  /**
   * 异步生成报表
   * @param {Object} data - 生成参数
   */
  generateAsync: (data) => request.post('/report/generate/async', data),
  
  /**
   * 预览报表内容
   * @param {Object} data - 预览参数
   */
  preview: (data) => request.post('/report/preview', data),

  // ========== 报表列表 ==========
  /**
   * 获取报表列表
   * @param {Object} params - 查询参数
   * @param {string} [params.report_type] - 报表类型
   * @param {string} [params.status] - 状态
   * @param {string} [params.start_date] - 开始日期
   * @param {string} [params.end_date] - 结束日期
   * @param {number} [params.page] - 页码
   * @param {number} [params.page_size] - 每页数量
   */
  getList: (params) => request.get('/report/', { params }),
  
  /**
   * 获取报表列表（备用路径）
   */
  getReports: (params) => request.get('/report/list', { params }),
  
  /**
   * 获取报表详情
   * @param {number} reportId - 报表ID
   */
  getById: (reportId) => request.get(`/report/${reportId}`),
  
  /**
   * 删除报表
   * @param {number} reportId - 报表ID
   */
  delete: (reportId) => request.delete(`/report/${reportId}`),
  
  /**
   * 下载报表
   * @param {number} reportId - 报表ID
   * @param {string} [format] - 下载格式
   */
  download: (reportId, format) => request.get(`/report/${reportId}/download`, { 
    params: format ? { format } : {},
    responseType: 'blob'
  }),
  
  /**
   * 获取报表文件
   * @param {string} filename - 文件名
   */
  getFile: (filename) => request.get(`/report/files/${filename}`, {
    responseType: 'blob'
  }),

  // ========== 报表统计 ==========
  /**
   * 获取报表统计信息
   */
  getStats: () => request.get('/report/stats'),

  // ========== 定时报表 ==========
  /**
   * 获取定时报表列表
   * @param {Object} params - 查询参数
   */
  getSchedules: (params) => request.get('/report/schedule', { params }),
  
  /**
   * 创建定时报表
   * @param {Object} data - 调度数据
   */
  createSchedule: (data) => request.post('/report/schedule', data),
  
  /**
   * 更新定时报表
   * @param {number} scheduleId - 调度ID
   * @param {Object} data - 调度数据
   */
  updateSchedule: (scheduleId, data) => request.put(`/report/schedule/${scheduleId}`, data),
  
  /**
   * 删除定时报表
   * @param {number} scheduleId - 调度ID
   */
  deleteSchedule: (scheduleId) => request.delete(`/report/schedule/${scheduleId}`),
  
  /**
   * 触发定时报表
   * @param {number} scheduleId - 调度ID
   */
  triggerSchedule: (scheduleId) => request.post(`/report/schedule/${scheduleId}/trigger`),
}
