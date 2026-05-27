<template>
  <el-container class="layout">
    <!-- Mobile Header -->
    <el-header class="mobile-header">
      <el-space>
        <el-button quaternary circle size="small" @click="toggleSidebar">
          <el-icon><Menu /></el-icon>
        </el-button>
        <span class="mobile-title">ITOps</span>
      </el-space>
      <el-space>
        <el-badge :value="notificationCount" :max="99" :hidden="notificationCount === 0">
          <el-button quaternary circle size="small" @click="$router.push('/notification/message')">
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
        <el-dropdown @command="onUserAction" trigger="click">
          <el-space align="center" style="cursor:pointer;padding:0 8px">
            <el-avatar :size="28" style="background:#18a058">
              {{ username.charAt(0).toUpperCase() }}
            </el-avatar>
            <span style="font-size:13px" class="mobile-username">{{ username }}</span>
          </el-space>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-space>
    </el-header>

    <!-- Sidebar -->
    <el-aside
      :width="collapsed ? '64px' : '220px'"
      class="sider"
      :class="{ 'mobile-sider': isMobile }"
    >
      <!-- Overlay for mobile -->
      <div v-if="isMobile && !collapsed" class="sidebar-overlay" @click="collapsed = true"></div>

      <div class="logo" @click="goHome">
        <el-icon :size="26" color="#18a058"><Monitor /></el-icon>
        <span v-show="!collapsed" class="logo-text">ITOps</span>
      </div>

      <el-menu
        :default-active="activeKey"
        :collapse="collapsed"
        :collapse-transition="false"
        class="sidebar-menu"
        @select="onMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-sub-menu index="monitoring">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>监控中心</span>
          </template>
          <el-menu-item index="/monitoring/devices">设备监控</el-menu-item>
          <el-menu-item index="/discovery/scan">设备扫描</el-menu-item>
          <el-menu-item index="/monitoring/alerts">告警管理</el-menu-item>
          <el-menu-item index="/monitoring/performance">性能监控</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="workorder">
          <template #title>
            <el-icon><Ticket /></el-icon>
            <span>工单管理</span>
          </template>
          <el-menu-item index="/workorder/list">工单列表</el-menu-item>
          <el-menu-item index="/workorder/create">创建工单</el-menu-item>
          <el-menu-item index="/workorder/my">我的工单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="knowledge">
          <template #title>
            <el-icon><Reading /></el-icon>
            <span>知识库</span>
          </template>
          <el-menu-item index="/knowledge/list">知识文档</el-menu-item>
          <el-menu-item index="/knowledge/category">分类管理</el-menu-item>
          <el-menu-item index="/knowledge/cases">故障案例</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="ai">
          <template #title>
            <el-icon><MagicStick /></el-icon>
            <span>AI助手</span>
          </template>
          <el-menu-item index="/ai/chat">AI 聊天</el-menu-item>
          <el-menu-item index="/ai/copilot">知识库问答</el-menu-item>
          <el-menu-item index="/ai/analyze">智能分析</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="automation">
          <template #title>
            <el-icon><Lightning /></el-icon>
            <span>自动化</span>
          </template>
          <el-menu-item index="/automation/script">脚本管理</el-menu-item>
          <el-menu-item index="/automation/task">任务调度</el-menu-item>
          <el-menu-item index="/automation/evaluate">指标评估</el-menu-item>
          <el-menu-item index="/automation/execute">执行记录</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="backup">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>备份管理</span>
          </template>
          <el-menu-item index="/backup/list">备份记录</el-menu-item>
          <el-menu-item index="/backup/restore">恢复管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="report">
          <template #title>
            <el-icon><DataBoard /></el-icon>
            <span>报表管理</span>
          </template>
          <el-menu-item index="/report/list">报表管理</el-menu-item>
          <el-menu-item index="/report/create">生成报表</el-menu-item>
          <el-menu-item index="/report/template">模板管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="notification">
          <template #title>
            <el-icon><Bell /></el-icon>
            <span>消息中心</span>
          </template>
          <el-menu-item index="/notification/message">我的消息</el-menu-item>
          <el-menu-item index="/notification/history">消息历史</el-menu-item>
          <el-menu-item index="/notification/config">通知配置</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/user">用户管理</el-menu-item>
          <el-menu-item index="/system/role">角色管理</el-menu-item>
          <el-menu-item index="/system/menu">菜单管理</el-menu-item>
          <el-menu-item index="/system/dict">字典管理</el-menu-item>
          <el-menu-item index="/system/config">参数配置</el-menu-item>
          <el-menu-item index="/system/logs">日志查看</el-menu-item>
          <el-menu-item index="/system/adapters">适配器管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- Main Content Area -->
    <el-container class="main">
      <el-header class="header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item v-for="b in breadcrumbs" :key="b">{{ b }}</el-breadcrumb-item>
        </el-breadcrumb>
        <el-space align="center" class="desktop-only">
          <el-badge :value="notificationCount" :max="99" :hidden="notificationCount === 0">
            <el-button quaternary circle size="small" @click="$router.push('/notification/message')">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown @command="onUserAction" trigger="click">
            <el-space align="center" style="cursor:pointer;padding:0 8px">
              <el-avatar :size="28" style="background:#18a058">
                {{ username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span style="font-size:13px">{{ username }}</span>
            </el-space>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </el-header>

      <el-main class="content">
        <div class="page">
          <router-view />
        </div>
      </el-main>

      <!-- 修改密码弹窗 -->
      <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px" :close-on-click-modal="false">
        <el-form :model="passwordForm" label-width="90px" label-position="top" @submit.prevent="handleChangePassword">
          <el-form-item label="旧密码" required>
            <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" show-password />
          </el-form-item>
          <el-form-item label="新密码" required>
            <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item label="确认密码" required>
            <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">确认修改</el-button>
        </template>
      </el-dialog>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  Menu, Bell, Monitor, Odometer, Ticket, Reading,
  MagicStick, Lightning, Document, DataBoard, Setting
} from '@element-plus/icons-vue'
import { notification, auth } from '@/api'
import { CONFIG } from '@/config/constants'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const isMobile = ref(false)
const notificationCount = ref(0)
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordForm = ref({ old_password: "", new_password: "", confirm_password: "" })
const activeKey = computed(() => route.path)

const username = computed(() => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) return JSON.parse(userStr).username || 'admin'
  } catch {}
  return 'admin'
})

const breadcrumbs = computed(() => {
  const result = []
  route.matched.forEach(r => { if (r.meta.title) result.push(r.meta.title) })
  return result.length ? result : ['仪表盘']
})

function goHome() {
  router.push('/dashboard')
}

function toggleSidebar() {
  collapsed.value = !collapsed.value
}

function onMenuSelect(index) {
  router.push(index)
}

async function onUserAction(key) {
  if (key === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    } catch {}
  } else if (key === 'password') {
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }; passwordDialogVisible.value = true
  } else if (key === 'profile') {
    ElMessage.info('个人中心功能开发中')
  }


const handleChangePassword = async () => {
  if (!passwordForm.value.old_password) {
    ElMessage.warning('请输入旧密码')
    return
  }
  if (!passwordForm.value.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (passwordForm.value.new_password.length < 8) {
    ElMessage.warning('新密码长度不能少于8位')
    return
  }
  passwordLoading.value = true
  try {
    await auth.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}
}

const fetchNotificationCount = async () => {
  try {
    const res = await notification.getMessages({ page: 1, page_size: 1 })
    notificationCount.value = res?.total || (Array.isArray(res) ? res.length : 0)
  } catch {}
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    collapsed.value = true
  }
}

let notifInterval = null

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchNotificationCount()
  notifInterval = setInterval(fetchNotificationCount, CONFIG.POLL_INTERVAL_LONG)
})

watch(() => route.path, () => {
  // Auto-collapse sidebar on mobile when navigating
  if (isMobile.value) {
    collapsed.value = true
  }
}, { immediate: true })

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (notifInterval) clearInterval(notifInterval)
})
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: row;
}

.main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sider {
  background: #f8f9fa;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  gap: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: #18a058;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 48px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.content {
  background: #f0f2f5;
  padding: 0;
  overflow: auto;
  flex: 1;
}

.page {
  padding: 20px;
}

/* Mobile styles */
.mobile-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  padding: 0 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  z-index: 999;
}

.mobile-title {
  font-size: 16px;
  font-weight: 700;
  color: #18a058;
}

.mobile-sider {
  position: fixed !important;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
  transition: transform 0.3s, width 0.3s;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: -1;
}

.desktop-only {
  display: flex;
}

.mobile-username {
  display: none;
}

@media (max-width: 768px) {
  .mobile-header {
    display: flex;
    justify-content: space-between;
  }

  .header {
    display: none;
  }

  .sider:not(.mobile-sider) {
    display: none;
  }

  .main {
    margin-top: 48px;
  }

  .page {
    padding: 12px;
  }

  .desktop-only {
    display: none;
  }

  .mobile-username {
    display: inline;
  }
}
</style>
