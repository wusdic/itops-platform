<template>
  <div class="copilot-page">
    <div class="copilot-layout">
      <!-- 左侧：知识库分类选择 -->
      <div class="category-sider">
        <div class="sider-header">
          <el-button type="primary" plain @click="createCategory" size="small">
            <el-icon><Plus /></el-icon>
            新建分类
          </el-button>
          <el-input v-model.trim="searchText" placeholder="搜索分类" size="small" clearable style="margin-top: 8px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="category-list">
          <div
            v-for="cat in filteredCategories"
            :key="cat.id"
            class="category-item"
            :class="{ active: selectedCategory?.id === cat.id }"
            @click="selectCategory(cat)"
          >
            <el-icon size="16" color="#18a058"><Document /></el-icon>
            <div class="cat-info">
              <div class="cat-name">{{ cat.name }}</div>
              <div class="cat-meta">{{ cat.description || '暂无描述' }}</div>
            </div>
          </div>
          <el-empty v-if="filteredCategories.length === 0" description="暂无分类" :image-size="60" style="padding: 20px" />
        </div>
      </div>

      <!-- 右侧：问答界面 -->
      <div class="qa-content">
        <template v-if="selectedCategory">
          <div class="qa-header">
            <div class="header-left">
              <el-icon size="20" color="#18a058"><MagicStick /></el-icon>
              <span style="font-weight: 600; font-size: 15px">{{ selectedCategory.name }} 智能问答</span>
            </div>
            <el-tag type="success" size="small">{{ filteredKnowledgeCount }} 条知识</el-tag>
          </div>

          <!-- 知识片段列表（可折叠）-->
          <el-collapse class="knowledge-collapse" v-if="knowledgeItems.length > 0">
            <el-collapse-item title="查看知识库内容" name="kb">
              <div class="knowledge-chips">
                <el-tag v-for="item in knowledgeItems.slice(0, 20)" :key="item.id" size="small" style="margin: 4px">
                  {{ item.title || item.content?.slice(0, 30) || '条目' + item.id }}
                </el-tag>
                <el-tag v-if="knowledgeItems.length > 20" size="small" type="info" style="margin: 4px">
                  还有 {{ knowledgeItems.length - 20 }} 条...
                </el-tag>
              </div>
            </el-collapse-item>
          </el-collapse>

          <!-- 问答历史 -->
          <div class="messages" ref="messagesRef">
            <template v-for="msg in qaHistory" :key="msg.id">
              <div class="message message-user">
                <el-avatar :style="{ background: '#2080f0' }" size="small">{{ userInitial }}</el-avatar>
                <div class="bubble bubble-user">{{ msg.question }}</div>
              </div>
              <div class="message message-ai">
                <el-avatar :style="{ background: '#18a058' }" size="small">AI</el-avatar>
                <div class="bubble bubble-ai" v-html="renderMarkdown(msg.answer)"></div>
              </div>
            </template>
            <div v-if="loading" class="message message-ai">
              <el-avatar :style="{ background: '#18a058' }" size="small">AI</el-avatar>
              <div class="bubble bubble-ai">
                <span style="color:#999">正在检索知识库并生成回答<span class="typing-cursor"></span></span>
              </div>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="chat-input">
            <el-input
              v-model.trim="inputText"
              type="textarea"
              placeholder="基于当前分类的知识库提问，按 Enter 发送"
              :autosize="{ minRows: 1, maxRows: 4 }"
              @keydown.enter="handleKeydown"
            />
            <el-button type="primary" :disabled="!inputText.trim() || loading" :loading="loading" @click="askQuestion" circle class="send-btn">
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </template>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-icon size="80" color="#ddd"><MagicStick /></el-icon>
          <p style="color: #999; margin-top: 16px; text-align: center">
            选择左侧分类，基于知识库进行智能问答
          </p>
          <div style="margin-top: 20px; font-size: 13px; color: #666; text-align: center; max-width: 360px; line-height: 1.6;">
            <p style="margin: 0 0 8px 0; font-weight: 600;">📚 知识库问答说明</p>
            <ul style="margin: 0; padding-left: 20px; text-align: left;">
              <li>先在左侧选择或新建知识分类</li>
              <li>向AI提问，系统将检索该分类下的知识库内容</li>
              <li>AI基于知识库内容生成准确回答</li>
              <li>适用于故障排查、标准操作等场景</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑分类弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="480px" :close-on-click-modal="false">
      <el-form :model="form" label-position="left" label-width="90">
        <el-form-item label="分类名称" required>
          <el-input v-model.trim="form.name" placeholder="如：服务器故障、数据库运维" />
        </el-form-item>
        <el-form-item label="分类编码" required>
          <el-input v-model="form.code" placeholder="如：server_fault, db_ops" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="form.description" type="textarea" :rows="2" placeholder="描述该知识分类的用途" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCategory" :loading="submitting">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Document, MagicStick, Promotion } from '@element-plus/icons-vue'
import { CONFIG } from '@/config/constants'

const message = ElMessage

const userInitial = computed(() => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) return JSON.parse(userStr).username?.charAt(0)?.toUpperCase() || 'U'
  } catch {}
  return 'U'
})

// 分类
const categories = ref([])
const searchText = ref('')
const selectedCategory = ref(null)
const knowledgeItems = ref([])
const qaHistory = ref([])
const inputText = ref('')
const loading = ref(false)
const messagesRef = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('新建分类')
const submitting = ref(false)
const form = reactive({ id: null, name: '', code: '', description: '' })

const filteredCategories = computed(() => {
  if (!searchText.value) return categories.value
  const kw = searchText.value.toLowerCase()
  return categories.value.filter(c =>
    (c.name || '').toLowerCase().includes(kw) ||
    (c.code || '').toLowerCase().includes(kw)
  )
})

const filteredKnowledgeCount = computed(() => knowledgeItems.value.length)

function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) =>
    `<pre data-lang="${lang}"><code class="language-${lang}">${code.trim()}</code></pre>`)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  html = html.replace(/\n/g, '<br>')
  return html
}

async function loadCategories() {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/knowledge/category', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    categories.value = data.items || data.data?.items || []
  } catch (e) {
    categories.value = []
  }
}

async function loadKnowledge(categoryId) {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/knowledge/sop?category_id=${categoryId}&page_size=${CONFIG.MAX_PAGE_SIZE}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    knowledgeItems.value = data.items || data.data?.items || []
  } catch {
    knowledgeItems.value = []
  }
}

async function selectCategory(cat) {
  selectedCategory.value = cat
  qaHistory.value = []
  inputText.value = ''
  await loadKnowledge(cat.id)
}

async function askQuestion() {
  const text = inputText.value.trim()
  if (!text || loading.value || !selectedCategory.value) return

  const questionId = Date.now()
  qaHistory.value.push({ id: questionId, question: text, answer: '' })
  inputText.value = ''
  loading.value = true
  await nextTick()
  scrollToBottom()

  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/ai/knowledge-qa', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        question: text,
        category_id: selectedCategory.value.id,
        knowledge_items: knowledgeItems.value.slice(0, 50)
      })
    })
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()
    const answer = data.answer || data.result || data.response || '抱歉，暂未找到相关知识库内容，请尝试其他问题。'
    const msg = qaHistory.value.find(m => m.id === questionId)
    if (msg) msg.answer = answer
  } catch (e) {
    const msg = qaHistory.value.find(m => m.id === questionId)
    if (msg) msg.answer = `查询失败: ${e.message}。知识库中有 ${knowledgeItems.value.length} 条相关知识，可尝试在AI聊天中直接提问。`
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    askQuestion()
  }
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

function createCategory() {
  dialogTitle.value = '新建分类'
  Object.assign(form, { id: null, name: '', code: '', description: '' })
  dialogVisible.value = true
}

function submitCategory() {
  if (!form.name || !form.code) {
    message.warning('请填写必填项')
    return
  }
  const existing = categories.value.find(c => c.code === form.code && c.id !== form.id)
  if (existing) {
    message.warning('分类编码已存在')
    return
  }
  const method = form.id ? 'PUT' : 'POST'
  const url = form.id ? `/api/v1/knowledge/category/${form.id}` : '/api/v1/knowledge/category'
  const token = localStorage.getItem('token') || ''
  submitting.value = true
  fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(form)
  }).then(res => {
    if (!res.ok) throw new Error()
    message.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    return loadCategories()
  }).catch(() => {
    message.error('操作失败')
  }).finally(() => {
    submitting.value = false
  })
}

function handleEditCategory(cat) {
  dialogTitle.value = '编辑分类'
  Object.assign(form, { id: cat.id, name: cat.name, code: cat.code, description: cat.description || '' })
  dialogVisible.value = true
}

onMounted(loadCategories)
</script>

<style scoped>
.copilot-page { height: 100%; }
.copilot-layout {
  display: flex;
  height: calc(100vh - 140px);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.category-sider {
  width: 260px;
  border-right: 1px solid #eee;
  background: #fafafa;
  display: flex;
  flex-direction: column;
}
.sider-header { padding: 12px; background: #fff; border-bottom: 1px solid #eee; }
.category-list { flex: 1; overflow-y: auto; }
.category-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f5f5f5;
}
.category-item:hover { background: #f0f0f0; }
.category-item.active { background: #e8f4ff; }
.cat-info { flex: 1; min-width: 0; }
.cat-name { font-size: 14px; font-weight: 500; color: #333; }
.cat-meta { font-size: 12px; color: #999; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.qa-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.qa-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  background: #fff;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.knowledge-collapse { margin: 8px 16px; }
.knowledge-chips { display: flex; flex-wrap: wrap; gap: 4px; padding: 4px 0; }

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.message { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 16px; }
.message-user { flex-direction: row-reverse; }
.message-ai { flex-direction: row; }
.bubble { max-width: 70%; padding: 10px 14px; border-radius: 12px; word-break: break-word; line-height: 1.5; }
.bubble-user { background: #18a058; color: #fff; }
.bubble-ai { background: #f0f0f0; color: #333; }
.bubble-ai :deep(pre) { background: #282c34; border-radius: 6px; padding: 12px; overflow-x: auto; margin: 8px 0; font-size: 13px; }
.bubble-ai :deep(code) { background: rgba(0,0,0,0.08); border-radius: 3px; padding: 1px 4px; font-size: 13px; font-family: monospace; }
.bubble-ai :deep(.typing-cursor)::after { content: '▊'; animation: blink 1s infinite; color: #18a058; }
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  background: #fff;
}
.chat-input .el-textarea { flex: 1; }
.send-btn { flex-shrink: 0; }

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
