<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <n-loading-bar-provider>
            <router-view />
          </n-loading-bar-provider>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  NConfigProvider, NMessageProvider, NDialogProvider,
  NNotificationProvider, NLoadingBarProvider,
  zhCN, dateZhCN
} from 'naive-ui'
import { CONFIG } from './config/constants'

const themeOverrides = {
  common: {
    primaryColor: '#18a058',
    primaryColorHover: '#36ad6a',
    primaryColorPressed: '#0c7a43',
    primaryColorSuppl: '#36ad6a',
    borderRadius: '6px'
  }
}

// 登录消息实例（延迟到 onMounted 后使用）
const messageRef = ref(null)

// 延迟获取 message 实例（必须在 n-message-provider 挂载后才能调用）
onMounted(async () => {
  // 动态 import 避免顶层调用 useMessage
  const { useMessage } = await import('naive-ui')
  messageRef.value = useMessage()

  // 加载平台时区配置
  loadTimezone()

  // 立即检查 token 过期
  checkTokenExpiry()
  // 每分钟检查一次
  tokenCheckTimer = setInterval(checkTokenExpiry, CONFIG.TOKEN_CHECK_INTERVAL)
})

// Token 过期自动退出
let tokenCheckTimer = null
let lastWarningTime = 0 // 防重复警告

function doLogout(reason) {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  if (reason && messageRef.value) messageRef.value.warning(reason)
  // 强跳登录页，不依赖 SPA 路由
  window.location.href = '/login'
}

function checkTokenExpiry() {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000
    const now = Date.now()
    const remaining = exp - now

    // 剩余5分钟时开始警告，每分钟最多提示一次
    if (remaining <= 5 * 60 * 1000 && remaining > 0) {
      const nowMinute = Math.floor(Date.now() / CONFIG.TOKEN_CHECK_INTERVAL)
      if (nowMinute !== lastWarningTime) {
        lastWarningTime = nowMinute
        if (messageRef.value) messageRef.value.warning('登录即将过期，请保存工作内容')
      }
    }

    // 已过期
    if (remaining <= 0) {
      doLogout('登录已过期，请重新登录')
    }
  } catch (_) {}
}

onUnmounted(() => {
  if (tokenCheckTimer) clearInterval(tokenCheckTimer)
})

async function loadTimezone() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/admin/info', {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (res.ok) {
      const data = await res.json()
      if (data.timezone) {
        const { setTimezone } = await import('./utils/date')
        setTimezone(data.timezone)
      }
    }
  } catch (_) {}
}
</script>
