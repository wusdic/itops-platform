import request from './request'

/**
 * 水印 API
 */
const watermark = {
  generate: (data) => request.post('/watermark/generate', data),
  list: (params) => request.get('/watermark/list', { params }),
  log: (params) => request.post('/watermark/log', { params }),
  track: (watermarkId, params) => request.get(`/watermark/track/${watermarkId}`, { params }),
  verify: (data) => request.post('/watermark/verify', data)
}

export default watermark
