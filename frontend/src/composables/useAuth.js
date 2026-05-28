import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// App 级状态：定时器 + 防抖
const tokenCheckTimer = ref(null)
const lastWarningTime = ref(0)

export function useAuth() {
  const router = useRouter()

  const token = computed(() => localStorage.getItem('token') || '')

  function doLogout(reason) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    if (reason) {
      ElMessage.warning(reason)
    }
    window.location.href = '/login'
  }

  function checkTokenExpiry() {
    const tk = token.value
    if (!tk) return

    try {
      const payload = JSON.parse(atob(tk.split('.')[1]))
      const exp = payload.exp * 1000
      const now = Date.now()
      const remaining = exp - now

      if (remaining <= 5 * 60 * 1000 && remaining > 0) {
        const nowMinute = Math.floor(Date.now() / 60000)
        if (nowMinute !== lastWarningTime.value) {
          lastWarningTime.value = nowMinute
          ElMessage.warning('登录即将过期，请保存工作内容')
        }
      }

      if (remaining <= 0) {
        doLogout('登录已过期，请重新登录')
      }
    } catch (_) {}
  }

  function startTokenMonitor() {
    if (tokenCheckTimer.value) return
    checkTokenExpiry()
    tokenCheckTimer.value = setInterval(checkTokenExpiry, 60000)
  }

  function stopTokenMonitor() {
    if (tokenCheckTimer.value) {
      clearInterval(tokenCheckTimer.value)
      tokenCheckTimer.value = null
    }
  }

  async function loadTimezone() {
    try {
      const data = await request.get('/admin/info')
      if (data?.timezone) {
        const { setTimezone } = await import('@/utils/date')
        setTimezone(data.timezone)
      }
    } catch (_) {}
  }

  return {
    token,
    doLogout,
    checkTokenExpiry,
    startTokenMonitor,
    stopTokenMonitor,
    loadTimezone
  }
}
