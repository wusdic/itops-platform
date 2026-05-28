<template>
  <el-config-provider :locale="zhCn" :size="defaultSize">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const defaultSize = ref('default')

onMounted(async () => {
  // 全局初始化：加载平台时区配置（登录页也需要时区）
  try {
    const data = await fetch('/api/v1/admin/info').then(r => r.json()).catch(() => null)
    if (data?.timezone) {
      const { setTimezone } = await import('./utils/date')
      setTimezone(data.timezone)
    }
  } catch (_) {}
})
</script>

<style>
#app {
  height: 100%;
}
</style>
