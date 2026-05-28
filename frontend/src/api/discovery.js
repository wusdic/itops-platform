import request from './request'

/**
 * 设备发现 API
 */
const discovery = {
  // ========== 网络 ==========
  networks: {
    getList: (params) => request.get('/discovery/networks', { params }),
    getById: (id) => request.get(`/discovery/networks/${id}`),
    create: (data) => request.post('/discovery/networks', data),
    update: (id, data) => request.put(`/discovery/networks/${id}`, data),
    delete: (id) => request.delete(`/discovery/networks/${id}`)
  },

  // ========== 扫描 ==========
  scan: {
    scan: (data) => request.post('/discovery/scan', data),
    scanAndImport: (data) => request.post('/discovery/scan-and-import', data),
    scanAndImportStream: (data) => request.post('/discovery/scan-and-import-stream', data),
    getStreamProgress: (scanId) => request.get(`/discovery/scan-and-import-stream/${scanId}`),
    getHistory: (params) => request.get('/discovery/scan-history', { params }),

    scanIp: (data) => request.post('/discovery/ip/scan', data),
    // SNMP 扫描
    scanSnmp: (data) => request.post('/discovery/snmp/scan', data),
    // ARP 扫描
    scanArp: (data) => request.post('/discovery/arp/scan', data)
  },

  // ========== 导入 ==========
  import: {
    importHosts: (data) => request.post('/discovery/devices/import', data)
  },

  // ========== 发现目标 ==========
  targets: {
    getList: (params) => request.get('/discovery/targets', { params }),
    getById: (id) => request.get(`/discovery/targets/${id}`),
    create: (data) => request.post('/discovery/targets', data),
    update: (id, data) => request.put(`/discovery/targets/${id}`, data),
    delete: (id) => request.delete(`/discovery/targets/${id}`),
    batchDelete: (ids) => request.post('/discovery/targets/batch-delete', { ids }),
    importTargets: (data) => request.post('/discovery/targets/import', data),
    exportTargets: (params) => request.get('/discovery/targets/export', { params, responseType: 'blob' })
  }
}

export default discovery
