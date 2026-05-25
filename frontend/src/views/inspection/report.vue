<template>
  <div class="page-container">
    <el-card :bordered="false">
      <template #header>
        <div class="card-header">
          <span>巡检报告 - {{ taskName }}</span>
          <el-space>
            <el-button @click="handleBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-button type="primary" @click="handleExport" :loading="exporting">
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 任务概览 -->
      <el-row :gutter="16" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-statistic title="任务状态" :value="taskInfo.status">
            <template #prefix>
              <el-tag :type="statusType">{{ statusLabel }}</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="巡检类型" :value="taskInfo.type" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="开始时间" :value="taskInfo.started_at || '-'" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="完成时间" :value="taskInfo.completed_at || '-'" />
        </el-col>
      </el-row>

      <!-- 统计图表 -->
      <el-row :gutter="16" style="margin-bottom: 20px">
        <el-col :span="12">
          <div ref="pieChartRef" style="height: 300px"></div>
        </el-col>
        <el-col :span="12">
          <div ref="barChartRef" style="height: 300px"></div>
        </el-col>
      </el-row>

      <!-- 巡检结果表格 -->
      <el-table :data="resultList" :loading="loading" style="width: 100%" row-key="id">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="target" label="巡检对象" min-width="150" />
        <el-table-column prop="check_item" label="检查项" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pass' ? 'success' : row.status === 'fail' ? 'danger' : 'warning'" size="small">
              {{ row.status === 'pass' ? '通过' : row.status === 'fail' ? '失败' : '警告' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="checked_at" label="检查时间" width="180" />
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Back } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import inspection from '@/api/inspection'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const exporting = ref(false)
const taskList = ref([])
const resultList = ref([])
const taskName = ref('')
const taskInfo = ref({})
const pieChartRef = ref(null)
const barChartRef = ref(null)
let pieChart = null
let barChart = null

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const statusMap = {
  pending: { label: '待执行', type: 'info' },
  running: { label: '执行中', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
  timeout: { label: '已超时', type: 'danger' }
}

const statusLabel = computed(() => statusMap[taskInfo.value.status]?.label || '-')
const statusType = computed(() => statusMap[taskInfo.value.status]?.type || 'info')

async function loadTaskInfo(taskId) {
  try {
    const res = await inspection.tasks.getById(taskId)
    const data = res?.data || res || {}
    taskInfo.value = data
    taskName.value = data.name || `任务 #${taskId}`
  } catch (e) {
    taskName.value = `任务 #${taskId}`
  }
}

async function loadResults(taskId) {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const res = await inspection.results.getByTaskId(taskId, params)
    const data = res?.data || res || {}
    resultList.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
    updateCharts()
  } catch (e) {
    ElMessage.error(`加载结果失败: ${e.message}`)
    resultList.value = []
  } finally {
    loading.value = false
  }
}

function updateCharts() {
  const passCount = resultList.value.filter(r => r.status === 'pass').length
  const failCount = resultList.value.filter(r => r.status === 'fail').length
  const warnCount = resultList.value.filter(r => r.status === 'warn').length

  if (pieChart) {
    pieChart.setOption({
      title: { text: '巡检结果分布', left: 'center', textStyle: { color: '#fff' } },
      tooltip: { trigger: 'item' },
      legend: { bottom: 10, textStyle: { color: '#aaa' } },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: passCount, name: '通过', itemStyle: { color: '#67c23a' } },
          { value: failCount, name: '失败', itemStyle: { color: '#f56c6c' } },
          { value: warnCount, name: '警告', itemStyle: { color: '#e6a23c' } }
        ]
      }]
    })
  }

  if (barChart) {
    barChart.setOption({
      title: { text: '检查项状态统计', left: 'center', textStyle: { color: '#fff' } },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['通过', '失败', '警告'],
        axisLine: { lineStyle: { color: '#666' } },
        axisLabel: { color: '#aaa' }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#666' } },
        axisLabel: { color: '#aaa' }
      },
      series: [{
        type: 'bar',
        data: [
          { value: passCount, itemStyle: { color: '#67c23a' } },
          { value: failCount, itemStyle: { color: '#f56c6c' } },
          { value: warnCount, itemStyle: { color: '#e6a23c' } }
        ]
      }]
    })
  }
}

function initCharts() {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
  }
}

async function handleExport() {
  const taskId = route.params.taskId
  exporting.value = true
  try {
    const res = await inspection.reports.export(taskId)
    const blob = res?.data || res
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `巡检报告_${taskName.value}_${Date.now()}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error(`导出失败: ${e.message}`)
  } finally {
    exporting.value = false
  }
}

function handleBack() {
  router.push('/inspection/tasks')
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  loadResults(route.params.taskId)
}

function handlePageChange(page) {
  pagination.page = page
  loadResults(route.params.taskId)
}

function handleResize() {
  pieChart?.resize()
  barChart?.resize()
}

onMounted(() => {
  const taskId = route.params.taskId
  loadTaskInfo(taskId)
  loadResults(taskId)
  initCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.page-container { padding: 16px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
