<template>
  <div class="page-container">
    <el-card :bordered="false">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>备份管理</span>
          <el-button type="primary" @click="handleCreate" :loading="creating">
            <el-icon><Upload /></el-icon>
            创建备份
          </el-button>
        </div>
      </template>

      <el-tabs v-model="filterType" @tab-change="loadData">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="全量备份" name="full" />
        <el-tab-pane label="增量备份" name="incremental" />
      </el-tabs>

      <el-input
        v-model.trim="searchKeyword"
        placeholder="搜索备份名称"
        clearable
        style="width: 200px; margin-bottom: 12px"
        @input="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>

      <el-table :data="filteredList" :loading="loading" row-key="id" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="备份名称" :show-overflow-tooltip="true" />
        <el-table-column prop="backup_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.backup_type === 'full' ? 'success' : 'info'" size="small">
              {{ typeText(row.backup_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">{{ row.size || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="备份时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-space :size="8">
              <el-button size="small" quaternary type="info" @click="handleView(row)">详情</el-button>
              <el-button
                size="small"
                quaternary
                type="danger"
                :disabled="row.status !== 'completed'"
                @click="handleDelete(row)"
              >删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredList.length === 0" description="暂无数据" />
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailDrawer" title="备份详情" size="480px" direction="rtl">
      <el-descriptions v-if="currentBackup" :column="1" border>
        <el-descriptions-item label="ID">{{ currentBackup.id }}</el-descriptions-item>
        <el-descriptions-item label="备份名称">{{ currentBackup.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ typeText(currentBackup.backup_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(currentBackup.status)" size="small">
            {{ statusText(currentBackup.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="大小">{{ currentBackup.size || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ currentBackup.created_by }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentBackup.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentBackup.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space justify="end">
          <el-button @click="detailDrawer = false">关闭</el-button>
          <el-button
            type="primary"
            :disabled="!currentBackup || currentBackup.status !== 'completed'"
            @click="handleRestore(currentBackup)"
          >恢复此备份</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search } from '@element-plus/icons-vue'
import { backup } from '@/api'

const loading = ref(false)
const creating = ref(false)
const backupList = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const detailDrawer = ref(false)
const currentBackup = ref(null)

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const filteredList = computed(() => {
  if (!searchKeyword.value) return backupList.value
  const kw = searchKeyword.value.toLowerCase()
  return backupList.value.filter(
    (b) => b.name?.toLowerCase().includes(kw) || b.created_by?.toLowerCase().includes(kw)
  )
})

const typeText = (t) => ({ full: '全量', incremental: '增量', differential: '差异' }[t] || t)
const statusTagType = (s) => ({ completed: 'success', failed: 'danger', running: 'warning' }[s] || 'info')
const statusText = (s) => ({ completed: '完成', failed: '失败', running: '进行中' }[s] || s)

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { limit: pagination.pageSize }
    if (filterType.value) params.backup_type = filterType.value
    const res = await backup.getList(params)
    backupList.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    ElMessage.error(`加载失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  // 前端过滤，搜索无后端支持
}

const handleCreate = async () => {
  creating.value = true
  try {
    await backup.create({
      name: `backup_${Date.now()}`,
      backup_type: 'full',
      targets: ['all'],
      description: '手动创建'
    })
    ElMessage.success('备份创建成功')
    loadData()
  } catch (e) {
    ElMessage.error(`创建失败: ${e.message}`)
  } finally {
    creating.value = false
  }
}

const handleView = (row) => {
  currentBackup.value = row
  detailDrawer.value = true
}

const handleRestore = async (row) => {
  if (!row) return
  try {
    await ElMessageBox.confirm(
      `确定要恢复备份"${row.name}"吗？恢复操作会覆盖当前数据，此操作不可逆。`,
      '确认恢复',
      { type: 'warning', confirmButtonText: '确认恢复', cancelButtonText: '取消' }
    )
    await backup.restore(row.id, { target: 'all', create_pre_backup: true })
    ElMessage.success('恢复任务已创建')
    detailDrawer.value = false
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(`恢复失败: ${e.message}`)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除备份"${row.name}"吗？此操作不可逆。`, '确认删除', {
      type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消'
    })
    await backup.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(`删除失败: ${e.message}`)
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 16px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
