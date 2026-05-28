import { ref, onUnmounted } from 'vue'
import { CONFIG } from '@/config/constants'

/**
 * 轮询 composable
 * @param {Function} callback - 轮询回调函数
 * @param {Object} options - 配置选项
 */
export function usePolling(callback, options = {}) {
  const {
    interval = CONFIG.POLL_INTERVAL_SHORT,
    immediate = false,
    retryOnError = true
  } = options

  const isPolling = ref(false)
  const timer = ref(null)
  const lastError = ref(null)
  let retryCount = 0
  const maxRetries = 3

  const start = () => {
    if (isPolling.value) return
    
    isPolling.value = true
    retryCount = 0

    if (immediate) {
      executeCallback()
    }

    timer.value = setInterval(() => {
      executeCallback()
    }, interval)
  }

  const stop = () => {
    isPolling.value = false
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  const executeCallback = async () => {
    try {
      await callback()
      retryCount = 0
      lastError.value = null
    } catch (err) {
      lastError.value = err
      console.error('Polling callback error:', err)
      
      if (retryOnError && retryCount < maxRetries) {
        retryCount++
        console.warn(`Polling retry ${retryCount}/${maxRetries}`)
      }
    }
  }

  const restart = () => {
    stop()
    start()
  }

  const setInterval = (newInterval) => {
    if (typeof newInterval === 'number' && newInterval > 0) {
      interval = newInterval
      if (isPolling.value) {
        restart()
      }
    }
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isPolling,
    lastError,
    start,
    stop,
    restart,
    setInterval
  }
}
