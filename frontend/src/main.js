import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 全局样式（SCSS）
import './styles/variables.scss'
import './styles/common.scss'
import './styles/element-plus-overrides.css'
import './styles/global.scss'

// Element Plus 中文语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 全局提供 Element Plus locale
app.provide('el-locale', zhCn)

app.mount('#app')
