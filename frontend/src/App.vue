<template>
  <el-config-provider :locale="zhCn" :size="defaultSize">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import request from '@/api/request'

const defaultSize = ref('default')
const router = useRouter()

// Token 过期检查
let tokenCheckTimer = null
let lastWarningTime = 0

function doLogout(reason) {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  if (reason) {
    ElMessage.warning(reason)
  }
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
      const nowMinute = Math.floor(Date.now() / 60000)
      if (nowMinute !== lastWarningTime) {
        lastWarningTime = nowMinute
        ElMessage.warning('登录即将过期，请保存工作内容')
      }
    }

    // 已过期
    if (remaining <= 0) {
      doLogout('登录已过期，请重新登录')
    }
  } catch (_) {}
}

onMounted(async () => {
  // 加载平台时区配置
  loadTimezone()

  // 立即检查 token 过期
  checkTokenExpiry()
  // 每分钟检查一次
  tokenCheckTimer = setInterval(checkTokenExpiry, 60000)
})

onUnmounted(() => {
  if (tokenCheckTimer) clearInterval(tokenCheckTimer)
})

async function loadTimezone() {
  try {
    const data = await request.get('/admin/info')
    if (data?.timezone) {
      const { setTimezone } = await import('./utils/date')
      setTimezone(data.timezone)
    }
  } catch (_) {}
}
</script>

<style>
#app {
  height: 100%;
}
</style>
