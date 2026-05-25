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
    scanAndImport: (data) => request.post('/discovery/scan/import', data),
    scanAndImportStream: (data) => request.post('/discovery/scan/import/stream', data),
    getHistory: (params) => request.get('/discovery/scan/history', { params }),

    // IP 扫描
    scanIp: (data) => request.post('/discovery/scan/ip', data),
    // SNMP 扫描
    scanSnmp: (data) => request.post('/discovery/scan/snmp', data),
    // ARP 扫描
    scanArp: (data) => request.post('/discovery/scan/arp', data)
  },

  // ========== 导入 ==========
  import: {
    importHosts: (data) => request.post('/discovery/import/hosts', data)
  }
}

export default discovery
