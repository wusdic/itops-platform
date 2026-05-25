<template>
  <div class="maintenance-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">维护时段</h1>
        <p class="page-subtitle">管理设备维护时间窗口</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 创建维护时段
        </el-button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 140px" @change="loadData">
        <el-option label="已启用" :value="true" />
        <el-option label="已禁用" :value="false" />
      </el-select>
      <el-button @click="loadData" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <!-- Maintenance Windows Table -->
    <el-card :bordered="false" class="table-card">
      <el-table :data="tableData" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" :show-overflow-tooltip="true" />
        <el-table-column prop="device_name" label="设备" :show-overflow-tooltip="true" width="150">
          <template #default="{ row }">{{ row.device_name || row.device_ip || '-' }}</template>
        </el-table-column>
        <el-table-column label="维护时间" width="300">
          <template #default="{ row }">
            <span v-if="row.start_time">{{ formatTime(row.start_time) }} ~ {{ formatTime(row.end_time) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="维护原因" :show-overflow-tooltip="true" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑维护时段' : '创建维护时段'" width="600px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入维护时段名称" />
        </el-form-item>
        <el-form-item label="设备" prop="device_id">
          <el-select v-model="form.device_id" placeholder="选择设备" filterable style="width: 100%">
            <el-option v-for="d in deviceOptions" :key="d.id" :label="`${d.name} (${d.ip_address})`" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="维护原因" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入维护原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { maintenanceWindows } from '@/api/monitoring'
import { formatTime } from '@/utils/date'

const loading = ref(false)
const saveLoading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStatus = ref(null)

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentId = ref(null)

const deviceOptions = ref([])
const form = reactive({
  name: '',
  device_id: null,
  start_time: '',
  end_time: '',
  reason: ''
})

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  device_id: [{ required: true, message: '请选择设备', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const statusMap = { scheduled: '计划中', active: '进行中', ended: '已结束' }
const getStatusType = (status) => {
  const map = { scheduled: 'info', active: 'warning', ended: 'success' }
  return map[status] || 'info'
}
const getStatusLabel = (status) => statusMap[status] || status || '-'

onMounted(() => {
  loadData()
  loadDevices()
})

const loadDevices = async () => {
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch('/api/v1/assets/device?page=1&page_size=100', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      deviceOptions.value = data.items || data.data?.items || []
    }
  } catch (e) {
    ElMessage.error('加载设备列表失败')
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value) params.is_active = filterStatus.value

    const res = await maintenanceWindows.getList(params)
    const data = res.data || {}

    if (Array.isArray(data)) {
      tableData.value = data
      total.value = data.length
    } else {
      tableData.value = data.items || data.data?.items || []
      total.value = data.total || tableData.value.length
    }
  } catch (e) {
    ElMessage.error('加载失败: ' + (e.message || '未知错误'))
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, { name: '', device_id: null, start_time: '', end_time: '', reason: '' })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    name: row.name,
    device_id: row.device_id,
    start_time: row.start_time,
    end_time: row.end_time,
    reason: row.reason
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saveLoading.value = true
  try {
    // 字段映射：前端 form 字段 → 后端 MaintenanceWindowCreate 字段
    const data = {
      name: form.name,
      description: form.reason,          // reason → description
      target_type: 'device',             // 必填，固定为 device
      target_id: String(form.device_id),  // device_id → target_id (string)
      start_time: form.start_time,
      end_time: form.end_time,
      is_active: true
    }
    if (isEdit.value) {
      await maintenanceWindows.update(currentId.value, data)
      ElMessage.success('更新成功')
    } else {
      await maintenanceWindows.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.message || '未知错误'))
  } finally {
    saveLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除维护时段"${row.name}"吗？`, '确认删除', { type: 'warning' })
    await maintenanceWindows.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败: ' + (e.message || '未知错误'))
  }
}
</script>

<style lang="scss" scoped>
.maintenance-container { padding: 16px; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-title { font-size: 20px; font-weight: 600; color: #e8e8e8; margin: 0; }
.page-subtitle { font-size: 14px; color: #888; margin: 4px 0 0 0; }

.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }

.table-card {
  background: #1e1e1e; border: 1px solid #333;
  :deep(.el-card__header) { background: #252525; border-color: #333; color: #e8e8e8; }
  :deep(.el-card__body) { background: #1e1e1e; }
}

.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

:deep(.el-dialog) {
  background: #1e1e1e; border: 1px solid #333;
  .el-dialog__header { background: #252525; border-color: #333; color: #e8e8e8; }
  .el-dialog__body { background: #1e1e1e; color: #e8e8e8; }
}
</style>
