/**
 * AI 分析 API
 */
import request from './request'

export const ai = {
  /**
   * 统一分析接口
   * @param {Object} data - { target_type, target_id, analysis_type }
   */
  analyze: (data) => request.post('/ai/analyze', data),

  /**
   * AI 分析历史
   * @param {Object} params - { page, page_size, source_type }
   */
  getAnalyzeHistory: (params) => request.get('/aiops/analysis/history', { params }),

  /**
   * AI 日志解读
   * @param {Object} data - { log_content, log_type, context }
   */
  interpretLog: (data) => request.post('/ai/interpret-log', data),

  /**
   * AI 问答
   * @param {Object} data - { question, context }
   */
  chat: (data) => request.post('/ai/chat', data),
}
