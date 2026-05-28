import request from './request'

/**
 * 厂商账密 API
 */
const vendorCredentials = {
  // ========== 厂商管理 ==========
  vendors: {
    getList: (params) => request.get('/credentials/vendors', { params }),
    getByName: (vendorName) => request.get(`/credentials/vendors/${vendorName}`),
    create: (data) => request.post('/credentials/vendors', data),
    update: (vendorName, data) => request.put(`/credentials/vendors/${vendorName}`, data),
    delete: (vendorName) => request.delete(`/credentials/vendors/${vendorName}`),
    getCategories: () => request.get('/credentials/vendors/categories'),
    getCommonCreds: () => request.get('/credentials/vendors/common-creds')
  },

  // ========== 版本管理 ==========
  versions: {
    getList: (params) => request.get('/credentials/versions', { params }),
    create: (data) => request.post('/credentials/versions', data),
    getByVersion: (version) => request.get(`/credentials/versions/${version}`),
    rollback: (version, data) => request.post(`/credentials/versions/${version}/rollback`, data)
  },

  // ========== 探测匹配 ==========
  probe: {
    matchByBanner: (params) => request.get('/credentials/probe/banner', { params }),
    matchByMac: (params) => request.get('/credentials/probe/mac', { params }),
    matchByOid: (params) => request.get('/credentials/probe/oid', { params })
  }
}

export default vendorCredentials
