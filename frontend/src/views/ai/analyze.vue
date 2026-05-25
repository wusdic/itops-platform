<template>
  <div class="ai-analyze-container">
    <el-card>
      <template #header>
        <span>智能分析</span>
      </template>
      <el-alert type="info" :closable="false" show-icon>
        AI 智能分析功能 - 输入日志或错误信息，AI 将自动分析问题原因并提供解决方案
      </el-alert>

      <el-space direction="vertical" :size="16" class="analyze-form">
        <el-form-item label="分析类型">
          <el-select
            v-model="analyzeType"
            placeholder="选择分析类型"
            style="width: 200px"
          >
            <el-option label="日志分析" value="log" />
            <el-option label="错误分析" value="error" />
            <el-option label="性能分析" value="performance" />
            <el-option label="安全分析" value="security" />
          </el-select>
        </el-form-item>

        <el-form-item label="分析内容">
          <el-input
            v-model="content"
            type="textarea"
            placeholder="输入日志、错误信息或系统状态描述..."
            :rows="6"
            :maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-space>
          <el-button type="primary" :loading="analyzing" @click="handleAnalyze">开始分析</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-space>
      </el-space>

      <div v-if="result" class="result-container">
        <el-divider>分析结果</el-divider>
        <div v-loading="analyzing">
          <el-card class="result-card">
            <el-input
              v-model="result"
              type="textarea"
              :rows="12"
              readonly
              placeholder="分析结果将显示在这里..."
            />
            <div class="result-footer">
              <el-space>
                <el-button size="small" @click="handleCopy">复制结果</el-button>
              </el-space>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const analyzeType = ref('log')
const content = ref('')
const result = ref('')
const analyzing = ref(false)

const typeOptions = [
  { label: '日志分析', value: 'log' },
  { label: '错误分析', value: 'error' },
  { label: '性能分析', value: 'performance' },
  { label: '安全分析', value: 'security' }
]

const fetchApi = async (url, options = {}) => {
  const token = localStorage.getItem('token') || ''
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...(options.headers || {})
    }
  })
  if (!res.ok) throw new Error(`HTTP error ${res.status}`)
  return res.json()
}

const handleAnalyze = async () => {
  if (!content.value.trim()) {
    ElMessage.warning('请输入分析内容')
    return
  }

  analyzing.value = true
  try {
    const res = await fetchApi('/api/v1/ai/troubleshoot', {
      method: 'POST',
      body: JSON.stringify({ query: content.value })
    })
    if (res.data) {
      result.value = typeof res.data === 'string' ? res.data : JSON.stringify(res.data, null, 2)
    } else if (typeof res === 'string') {
      result.value = res
    } else {
      result.value = JSON.stringify(res, null, 2)
    }
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败，请重试')
    result.value = '分析失败: ' + error.message
  } finally {
    analyzing.value = false
  }
}

const handleReset = () => {
  content.value = ''
  result.value = ''
  analyzeType.value = 'log'
}

const handleCopy = () => {
  navigator.clipboard.writeText(result.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}</script>

<style scoped>
.ai-analyze-container {
  padding: 20px;
}
.analyze-form {
  margin-top: 20px;
}
.result-container {
  margin-top: 20px;
}
.result-card {
  margin-top: 12px;
}
.result-footer {
  margin-top: 12px;
  text-align: right;
}
</style>
