import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { CONFIG } from '../config/constants'
import { useAppStore } from '@/stores/app'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: CONFIG.REQUEST_TIMEOUT
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const appStore = useAppStore()
    const token = appStore.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    // 兼容 access_token 和 token 两种字段名
    if (res.access_token && !res.token) {
      res.token = res.access_token
    }
    // 兼容无 code 字段的响应（如登录 API 直接返回 token）
    if (res.access_token || res.token) {
      return res
    }
    // 兼容直接返回 {items, total} 格式（如 /assets/device）
    // 和 {code, data} 包装格式
    if (res.items !== undefined && res.total !== undefined) {
      return { data: res }  // 保持 {data: {items, total}} 结构，兼容 .data 取值
    }
    // 如果是数组（某些列表接口直接返回数组）
    if (Array.isArray(res)) {
      return { data: { items: res, total: res.length } }
    }
    // 有 msg 或 detail 字段通常是后端错误响应
    if (res.msg) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    // 兜底：直接返回原始数据
    return res
  },
  error => {
    if (error.response) {
      const data = error.response.data
      if (error.response.status === 401) {
        // 登录页的 401 不弹提示（避免刷新登录页时显示"登录已过期"）
        if (window.location.pathname !== '/login') {
          ElMessage.error('登录已过期，请重新登录')
        }
        localStorage.removeItem('token')
        if (window.location.pathname !== '/login') {
          router.push('/login')
        }
      } else if (error.response.status === 403) {
        ElMessage.error('没有权限访问')
      } else if (error.response.status === 404 && data?.detail?.includes('无指标数据')) {
        // 设备指标暂无数据，是正常状态，不弹错误提示，静默返回空数据
        return Promise.reject(new Error('NO_DATA'))
      } else if (data?.msg || data?.detail) {
        ElMessage.error(data.msg || data.detail)
        return Promise.reject(new Error(data.msg || data.detail))
      } else {
        ElMessage.error('请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
