import request from './request'

/**
 * 分片 API
 */
const sharding = {
  getStats: (params) => request.get('/sharding/stats', { params }),
  getRoutes: (params) => request.get('/sharding/routes', { params }),
  createShard: (data) => request.post('/sharding/shards', data)
}

export default sharding
