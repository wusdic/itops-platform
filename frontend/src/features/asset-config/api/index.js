/**
 * Asset Config Feature API
 * 统一调用 /api/v1/assets/, /credentials/, /configs/ 等接口
 */
import request from '@/api/request'

export const assetConfig = {
  // ===== 资产 (Assets) =====
  assets: {
    getList: (params) => request.get('/assets/', { params }),
    getById: (id) => request.get(`/assets/${id}`),
    create: (data) => request.post('/assets/', data),
    update: (id, data) => request.put(`/assets/${id}`, data),
    delete: (id) => request.delete(`/assets/${id}`),
    getStats: () => request.get('/assets/stats'),
    batchDelete: (ids) => request.post('/assets/batch-delete', { ids }),
  },

  // ===== 凭证 (Credentials) =====
  credentials: {
    getList: (params) => request.get('/credentials', { params }),
    getById: (id) => request.get(`/credentials/${id}`),
    create: (data) => request.post('/credentials', data),
    update: (id, data) => request.put(`/credentials/${id}`, data),
    delete: (id) => request.delete(`/credentials/${id}`),
    test: (id) => request.post(`/credentials/${id}/test`),
  },

  // ===== 配置 (Configs) =====
  configs: {
    getList: (params) => request.get('/configs/', { params }),
    getById: (id) => request.get(`/configs/${id}`),
    create: (data) => request.post('/configs/', data),
    update: (id, data) => request.put(`/configs/${id}`, data),
    delete: (id) => request.delete(`/configs/${id}`),
  },

  // ===== 资产关联关系 =====
  relations: {
    getList: (params) => request.get('/asset-relations/', { params }),
    create: (data) => request.post('/asset-relations/', data),
    delete: (id) => request.delete(`/asset-relations/${id}`),
  },
}
