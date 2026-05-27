<template>
  <div class="page-card-wrapper">
    <el-card shadow="never">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>参数配置</span>
          <el-button type="primary" size="small" @click="loadData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-alert type="info" :show-icon="true" style="margin-bottom: 16px">
        <strong>参数配置说明：</strong>系统级配置项，控制平台全局行为。修改前请确认用途，错误配置可能影响系统稳定性。
      </el-alert>

      <el-table
        :data="configList"
        v-loading="loading"
        :pagination="paginationConfig"
        row-key="key"
        size="small"
      >
        <el-table-column label="配置键" prop="key" width="200" show-overflow-tooltip />
        <el-table-column label="配置值" prop="value" width="320" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="!row.editing">
              <span v-if="isTimezoneKey(row.key)">{{ getTimezoneLabel(row.value) }}</span>
              <span v-else>{{ row.value }}</span>
            </span>
            <span v-else>
              <el-select v-if="isTimezoneKey(row.key)" v-model="row.editValue" :options="TIMEZONE_OPTIONS" style="width: 260px" />
              <el-input v-else v-model.trim="row.editValue" style="width: 200px" />
            </span>
          </template>
        </el-table-column>
        <el-table-column label="描述" prop="description" width="200" show-overflow-tooltip />
        <el-table-column label="更新时间" prop="updated_at" width="180">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <span v-if="!row.editing">
              <el-button type="primary" size="small" link @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
            </span>
            <span v-else>
              <el-button type="primary" size="small" link @click="handleSave(row)">
                <el-icon><Check /></el-icon>保存
              </el-button>
              <el-button type="info" size="small" link @click="handleCancel(row)">
                <el-icon><Close /></el-icon>取消
              </el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && configList.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Edit, Check, Close } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'

const loading = ref(false)
const configList = ref([])

const TIMEZONE_OPTIONS = [
  { label: '亚洲/上海 (UTC+8)', value: 'Asia/Shanghai' },
  { label: '亚洲/东京 (UTC+9)', value: 'Asia/Tokyo' },
  { label: '亚洲/香港 (UTC+8)', value: 'Asia/Hong_Kong' },
  { label: '亚洲/新加坡 (UTC+8)', value: 'Asia/Singapore' },
  { label: '美国/太平洋 (UTC-8)', value: 'America/Los_Angeles' },
  { label: '美国/东部 (UTC-5)', value: 'America/New_York' },
  { label: '欧洲/伦敦 (UTC+0)', value: 'Europe/London' },
  { label: '欧洲/柏林 (UTC+1)', value: 'Europe/Berlin' },
  { label: 'UTC', value: 'UTC' },
]

const getTimezoneLabel = (val) => {
  const opt = TIMEZONE_OPTIONS.find(o => o.value === val)
  return opt ? opt.label.split(' ')[0] + ' ' + opt.label.split(' ')[1] : val
}

const paginationConfig = reactive({
  currentPage: 1,
  pageSize: 10,
  pageSizes: [10, 20, 50],
  layout: 'sizes, prev, pager, next',
  onCurrentChange: (page) => {
    paginationConfig.currentPage = page
    loadData()
  },
  onSizeChange: (pageSize) => {
    paginationConfig.pageSize = pageSize
    paginationConfig.currentPage = 1
    loadData()
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/admin/config?page=${paginationConfig.currentPage}&page_size=${paginationConfig.pageSize}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()
    configList.value = (data.items || []).map(c => ({ ...c, editing: false, editValue: c.value }))
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = (row) => {
  row.editing = true
  row.editValue = row.value
}

const handleCancel = (row) => {
  row.editing = false
  row.editValue = row.value
}

const handleSave = async (row) => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/admin/config/${row.key}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ value: row.editValue })
    })
    if (!res.ok) throw new Error('更新失败')
    row.value = row.editValue
    row.editing = false
    ElMessage.success('保存成功')

    if (row.key === 'system.timezone') {
      const { setTimezone } = await import('@/utils/date')
      setTimezone(row.value)
    }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const isTimezoneKey = (key) => key === 'system.timezone'

onMounted(() => { loadData() })
</script>

<style lang="scss" scoped>
.page-card-wrapper {
  margin: 16px;
}
</style>
