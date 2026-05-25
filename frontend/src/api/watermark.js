import request from './request'

/**
 * 水印 API
 */
const watermark = {
  generate: (data) => request.post('/watermark/generate', data),
  list: (params) => request.get('/watermark/list', { params }),
  log: (params) => request.get('/watermark/log', { params }),
  track: (params) => request.get('/watermark/track', { params }),
  verify: (data) => request.post('/watermark/verify', data)
}

export default watermark
