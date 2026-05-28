<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-title">
          <el-icon :size="32" color="#409eff"><Monitor /></el-icon>
          <span>ITOps 智能运维平台</span>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model.trim="form.username" placeholder="请输入用户名" clearable>
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password clearable>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="default" style="width: 100%" @click="handleSSOLogin">
            企业微信 / SSO 登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { auth } from '@/api'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
    try {
      await formRef.value?.validate()
    } catch {
      return
    }

    loading.value = true
    try {
      const res = await auth.login({
        username: form.username,
        password: form.password
      })

      const token = res.access_token
      localStorage.setItem('token', token)
      appStore.setToken(token)

      const userInfo = res.user || {}
      localStorage.setItem('user', JSON.stringify(userInfo))

      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error(error.response?.data?.message || error.message || '登录失败')
    } finally {
      loading.value = false
    }
  }

  const handleSSOLogin = async () => {
    loading.value = true
    try {
      const res = await auth.ldapLogin({
        username: form.username,
        password: form.password
      })
      if (res.success) {
        const token = res.access_token
        localStorage.setItem('token', token)
        appStore.setToken(token)
        const userInfo = res.user || {}
        localStorage.setItem('user', JSON.stringify(userInfo))
        ElMessage.success('SSO登录成功')
        router.push('/dashboard')
      } else {
        ElMessage.error(res.message || 'SSO登录失败')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || error.message || 'SSO登录失败')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-card {
  width: 400px;
}

.login-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}
</style>
