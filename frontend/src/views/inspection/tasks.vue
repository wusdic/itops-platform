<template>
  <div class="page-container">
    <el-card :bordered="false">
      <template #header>
        <div class="card-header">
          <span>巡检任务</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>

      <el-space style="margin-bottom: 12px" align="center">
        <el-input v-model.trim="searchKeyword" placeholder="搜索任务名称" clearable style="width: 200px" @input="handleSearchInput">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="任务状态" clearable style="width: 120px" @change="debouncedSearch">
          <el-option label="待执行" value="pending" />
          <el-option label="执行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="已超时" value="timeout" />
        </el-select>
      </el-space>

      <el-table :data="taskList" :loading="loading" :row-key="row => row.id" style="width: 100%">
        <el-table-column v-for="col in columns" :key="col.key" v-bind="col" />
      </el-table>

      <el-empty v-if="!loading && taskList.length === 0" description="暂无数据" />

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

    <!-- 新建/编辑任务 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-position="top" label-width="100">
        <el-form-item label="任务名称" required>
          <el-input v-model.trim="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="巡检类型">
          <el-select v-model="form.type" placeholder="请选择巡检类型" style="width: 100%">
            <el-option label="设备巡检" value="device" />
            <el-option label="安全巡检" value="security" />
            <el-option label="性能巡检" value="performance" />
            <el-option label="全量巡检" value="full" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标设备">
          <el-select v-model="form.targets" multiple placeholder="请选择目标设备" style="width: 100%">
            <el-option label="路由器-核心-01" value="device_1" />
            <el-option label="交换机-接入-01" value="device_2" />
            <el-option label="防火墙-FW-01" value="device_3" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行时间">
          <el-date-picker v-model="form.scheduled_at" type="datetime" placeholder="选择执行时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="超时时间">
          <el-input-number v-model.trim="form.timeout" :min="1" :max="1440" placeholder="分钟" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { ElMessage, ElPopconfirm } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { CONFIG } from '@/config/constants'
import { useRouter } from 'vue-router'
import inspection from '@/api/inspection'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const taskList = ref([])
const searchKeyword = ref('')
const filterStatus = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('创建任务')

let searchTimer = null
function handleSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, CONFIG.SEARCH_DEBOUNCE)
}

function debouncedSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, CONFIG.SEARCH_DEBOUNCE)
}

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  name: '',
  type: 'device',
  targets: [],
  scheduled_at: null,
  timeout: 60,
  remark: ''
})

const statusMap = {
  pending: { label: '待执行', type: 'info' },
  running: { label: '执行中', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
  timeout: { label: '已超时', type: 'danger' }
}

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '任务名称', key: 'name', width: 200 },
  { title: '巡检类型', key: 'type', width: 120,
    render: ({ row }) => {
      const typeMap = { device: '设备巡检', security: '安全巡检', performance: '性能巡检', full: '全量巡检' }
      return h(ElTag, { size: 'small', type: 'info' }, () => typeMap[row.type] || row.type || '-')
    }
  },
  { title: '状态', key: 'status', width: 100,
    render: ({ row }) => {
      const s = statusMap[row.status] || { label: row.status, type: 'info' }
      return h(ElTag, { size: 'small', type: s.type }, () => s.label)
    }
  },
  { title: '执行进度', key: 'progress', width: 160,
    render: ({ row }) => {
      const progress = row.progress || 0
      return h(ElProgress, { percentage: progress, size: 'small', strokeWidth: 6 })
    }
  },
  { title: '执行时间', key: 'scheduled_at', width: 180 },
  { title: '完成时间', key: 'completed_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 280, fixed: 'right',
    render({ row }) {
      const buttons = [
        h(ElButton, { size: 'small', text: true, type: 'primary', onClick: () => handleViewReport(row) }, () => '查看报告')
      ]
      if (row.status === 'pending') {
        buttons.push(h(ElButton, { size: 'small', text: true, type: 'warning', onClick: () => handleEdit(row) }, () => '编辑'))
        buttons.push(h(ElPopconfirm, {
          title: '确定删除此巡检任务？',
          onConfirm: () => handleDelete(row)
        }, () => h(ElButton, { size: 'small', text: true, type: 'danger' }, () => '删除')))
      }
      return h(ElSpace, { size: 12 }, () => buttons)
    }
  }
]

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchKeyword.value) params.search = searchKeyword.value

    const res = await inspection.tasks.getList(params)
    const data = res?.data || res || {}
    taskList.value = data.items || data.data?.items || []
    pagination.total = data.total || data.data?.total || 0
  } catch (e) {
    ElMessage.error(`加载任务失败: ${e.message}`)
    taskList.value = []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '创建任务'
  Object.assign(form, { id: null, name: '', type: 'device', targets: [], scheduled_at: null, timeout: 60, remark: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑任务'
  Object.assign(form, {
    id: row.id,
    name: row.name,
    type: row.type || 'device',
    targets: row.targets || [],
    scheduled_at: row.scheduled_at,
    timeout: row.timeout || 60,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await inspection.tasks.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    ElMessage.error(`删除失败: ${e.message}`)
  }
}

function handleViewReport(row) {
  router.push(`/inspection/report/${row.id}`)
}

async function submitForm() {
  if (!form.name) {
    ElMessage.warning('请填写任务名称')
    return
  }
  if (submitting.value) return
  submitting.value = true
  try {
    const data = { ...form }
    if (data.id) {
      await inspection.tasks.update(data.id, data)
      ElMessage.success('更新成功')
    } else {
      await inspection.tasks.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(`操作失败: ${e.message}`)
  } finally {
    submitting.value = false
  }
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

function handlePageChange(page) {
  pagination.page = page
  loadData()
}

onMounted(() => { loadData() })
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
