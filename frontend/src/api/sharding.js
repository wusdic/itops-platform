import request from './request'

/**
 * 分片 API
 */
const sharding = {
  getStats: (params) => request.get('/sharding/stats', { params }),
  getRoutes: (logicalTable, params) => request.get(`/sharding/routes/${logicalTable}`, { params }),
  createShard: (logicalTable, data) => request.post(`/sharding/routes/${logicalTable}/create`, data),
  deleteRoute: (logicalTable, routeId) => request.delete(`/sharding/routes/${logicalTable}/${routeId}`)
}

export default sharding
