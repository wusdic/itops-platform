<template>
  <n-card title="参数配置" class="page-card">
    <template #header-extra>
      <n-space>
        <n-button type="primary" @click="loadData" :loading="loading">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          刷新
        </n-button>
      </n-space>
    </template>

    <n-alert type="info" :show-icon="true" style="margin-bottom: 16px">
      <strong>参数配置说明：</strong>系统级配置项，控制平台全局行为。修改前请确认用途，错误配置可能影响系统稳定性。
    </n-alert>

    <n-data-table
      :columns="columns"
      :data="configList"
      :loading="loading"
      :pagination="pagination"
      :row-key="row => row.key"
    />
  </n-card>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useMessage, NButton, NIcon, NAlert, NSelect } from 'naive-ui'
import { RefreshOutline, CreateOutline, CheckmarkOutline, CloseOutline } from '@vicons/ionicons5'
import { formatDate } from '@/utils/date'

const message = useMessage()
const loading = ref(false)
const configList = ref([])

// 常用时区列表
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

const pagination = {
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page) => {
    pagination.page = page
    loadData()
  },
  onUpdatePageSize: (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadData()
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/admin/config?page=${pagination.page}&page_size=${pagination.pageSize}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('请求失败')
    const data = await res.json()
    configList.value = (data.items || []).map(c => ({ ...c, editing: false, editValue: c.value }))
  } catch (error) {
    message.error('加载配置失败')
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
    message.success('保存成功')

    // 如果修改的是时区，立即应用到全局
    if (row.key === 'system.timezone') {
      const { setTimezone } = await import('@/utils/date')
      setTimezone(row.value)
    }
  } catch (error) {
    message.error('保存失败')
  }
}

// 根据配置键判断是否有时区选择器
const isTimezoneKey = (key) => key === 'system.timezone'

// 构建编辑控件（时区用下拉框，普通配置用 input）
const buildEditControl = (row) => {
  if (isTimezoneKey(row.key)) {
    return h(NSelect, {
      value: row.editValue,
      options: TIMEZONE_OPTIONS,
      style: 'width: 260px',
      onUpdateValue: (val) => { row.editValue = val }
    })
  }
  return h('input', {
    value: row.editValue,
    onInput: (e) => { row.editValue = e.target.value },
    style: 'width: 200px; padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px;'
  })
}

const columns = [
  {
    title: '配置键',
    key: 'key',
    width: 200,
    ellipsis: { tooltip: true }
  },
  {
    title: '配置值',
    key: 'value',
    width: 320,
    ellipsis: { tooltip: true },
    render(row) {
      if (!row.editing) {
        // 时区配置显示中文说明
        if (isTimezoneKey(row.key)) {
          const opt = TIMEZONE_OPTIONS.find(o => o.value === row.value)
          return opt ? opt.label.split(' ')[0] + ' ' + opt.label.split(' ')[1] : row.value
        }
        return row.value
      }
      return buildEditControl(row)
    }
  },
  {
    title: '描述',
    key: 'description',
    width: 200,
    ellipsis: { tooltip: true }
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 180,
    render(row) {
      return formatDate(row.updated_at)
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    render(row) {
      if (!row.editing) {
        return h(
          NButton,
          { type: 'primary', size: 'small', onClick: () => handleEdit(row) },
          { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }), default: () => '编辑' }
        )
      }
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(
          NButton,
          { type: 'primary', size: 'small', onClick: () => handleSave(row) },
          { icon: () => h(NIcon, null, { default: () => h(CheckmarkOutline) }), default: () => '保存' }
        ),
        h(
          NButton,
          { type: 'info', size: 'small', onClick: () => handleCancel(row) },
          { icon: () => h(NIcon, null, { default: () => h(CloseOutline) }), default: () => '取消' }
        )
      ])
    }
  }
]

onMounted(() => { loadData() })
</script>

<style lang="scss" scoped>
.page-card {
  margin: 16px;
}
</style>
