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
  }
}

export default discovery
