<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>故障案例库</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加案例
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-space style="margin-bottom: 16px">
        <el-input v-model="searchKeyword" placeholder="搜索标题/关键词" clearable style="width: 200px" @keyup.enter="loadData" />
        <el-select v-model="filterSeverity" :options="severityOptions" placeholder="严重程度" clearable style="width: 140px" @change="loadData" />
        <el-select v-model="filterStatus" :options="statusOptions" placeholder="处理状态" clearable style="width: 140px" @change="loadData" />
      </el-space>

      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="标题" show-overflow-tooltip>
          <template #default="{ row }">
            <a href="javascript:void(0)" style="color:#18a058; cursor: pointer" @click="showDetail(row)">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column label="严重程度" width="90">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" width="160" show-overflow-tooltip />
        <el-table-column prop="occurred_at" label="发生时间" width="170" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" quaternary type="info" @click="showDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailDrawer" :size="640" direction="rtl">
      <template #title>
        <span>{{ currentCase?.title || '案例详情' }}</span>
      </template>
      <el-descriptions v-if="currentCase" :column="1" border>
        <el-descriptions-item label="案例ID">{{ currentCase.id }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :type="getSeverityType(currentCase.severity)" size="small">{{ currentCase.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(currentCase.status)" size="small">{{ currentCase.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="关键词">{{ currentCase.keywords || '-' }}</el-descriptions-item>
        <el-descriptions-item label="影响范围">{{ currentCase.impact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发生时间">{{ currentCase.occurred_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="解决时间">{{ currentCase.resolved_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <el-tabs type="line">
        <el-tab-pane label="问题描述" name="desc">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.description || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="根因分析" name="root">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.root_cause || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="解决方案" name="solution">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.solution || '暂无' }}</div>
        </el-tab-pane>
        <el-tab-pane label="经验教训" name="lessons">
          <div style="white-space: pre-wrap; line-height: 1.8">{{ currentCase?.lessons_learned || '暂无' }}</div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailDrawer = false">关闭</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const message = ElMessage
const loading = ref(false)
const list = ref([])
const searchKeyword = ref('')
const filterSeverity = ref(null)
const filterStatus = ref(null)
const detailDrawer = ref(false)
const currentCase = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const severityOptions = [
  { label: '严重', value: 'critical' },
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' },
]

const statusOptions = [
  { label: '未解决', value: 'open' },
  { label: '处理中', value: 'in_progress' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' },
]

function getSeverityType(s) {
  return { critical: 'danger', high: 'warning', medium: 'primary', low: 'info' }[s] || 'info'
}

function getStatusType(s) {
  return { open: 'danger', in_progress: 'warning', resolved: 'success', closed: 'info' }[s] || 'info'
}

function showDetail(row) {
  currentCase.value = row
  detailDrawer.value = true
}

onMounted(() => { loadData() })

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const params = new URLSearchParams({ page: pagination.page, page_size: pagination.pageSize })
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    if (filterSeverity.value) params.append('severity', filterSeverity.value)
    if (filterStatus.value) params.append('status', filterStatus.value)
    const res = await fetch(`/api/v1/knowledge/fault-case?${params}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (!data || typeof data !== 'object') throw new Error('响应格式异常')
    list.value = data.items || []
    pagination.total = data.total || 0
  } catch (e) {
    message.error(`加载失败: ${e.message}`)
    list.value = []
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  pagination.page = page
  loadData()
}

function handlePageSizeChange(pageSize) {
  pagination.pageSize = pageSize
  pagination.page = 1
  loadData()
}

function handleAdd() {
  message.warning('故障案例创建功能需后端支持故障案例数据模型和 API')
}
</script>