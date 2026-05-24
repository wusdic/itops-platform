import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.css'

// Element Plus 中文语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 全局提供 Element Plus locale
app.provide('el-locale', zhCn)

app.mount('#app')
