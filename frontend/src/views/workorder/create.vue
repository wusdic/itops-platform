<template>
  <div class="page-container">
    <el-card title="创建工单" shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" label-width="120" style="max-width: 800px">
        <el-form-item label="工单标题" prop="title">
          <el-input v-model.trim="form.title" placeholder="请输入工单标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" :options="priorityOptions" placeholder="请选择" style="width: 200px" />
        </el-form-item>

        <el-form-item label="工单类型" prop="type">
          <el-select v-model="form.type" :options="typeOptions" placeholder="请选择工单类型" style="width: 100%" />
        </el-form-item>

        <el-form-item label="关联设备">
          <el-select v-model="form.device_id" :options="deviceOptions" placeholder="请选择关联设备（可选）" style="width: 100%" clearable />
        </el-form-item>

        <el-form-item label="工单描述" prop="description">
          <el-input v-model.trim="form.description" type="textarea" :rows="6" placeholder="请详细描述工单内容" />
        </el-form-item>

        <el-form-item>
          <el-space>
            <el-button type="primary" @click="submitForm" :loading="submitting">提交工单</el-button>
            <el-button @click="$router.push('/workorder/my')">取消</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CONFIG } from '@/config/constants'
import { workorder } from '@/api/workorder'
import { devices } from '@/api/monitoring'

const router = useRouter()
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  title: '',
  priority: 'P3',
  type: '',
  device_id: null,
  description: ''
})

const rules = {
  title: { required: true, message: '请输入工单标题', trigger: 'blur' },
  type: { required: true, message: '请选择工单类型', trigger: 'change' },
  description: { required: true, message: '请输入工单描述', trigger: 'blur' }
}

const priorityOptions = [
  { label: 'P1 - 紧急', value: 'P1' },
  { label: 'P2 - 高', value: 'P2' },
  { label: 'P3 - 中', value: 'P3' },
  { label: 'P4 - 低', value: 'P4' }
]

const typeOptions = [
  { label: '故障报修', value: 'fault' },
  { label: '需求申请', value: 'requirement' },
  { label: '变更申请', value: 'change' },
  { label: '日常巡检', value: 'inspection' }
]

const deviceOptions = ref([])

async function loadDevices() {
  try {
    const res = await devices.getList({ page: 1, page_size: CONFIG.MAX_PAGE_SIZE || 200 })
    const list = res?.items || res?.data || []
    deviceOptions.value = list.map(d => ({
      label: `${d.name} (${d.ip_address || d.ip})`,
      value: d.id
    }))
  } catch (e) {
    deviceOptions.value = []
    ElMessage.error(`加载设备列表失败: ${e.message}`)
  }
}

async function submitForm() {
  submitting.value = true
  try {
    await formRef.value?.validate()
  } catch {
    submitting.value = false
    return
  }

  try {
    const payload = {
      title: form.title,
      description: form.description,
      priority: form.priority,
      order_type: form.type,
      device_id: form.device_id
    }
    await workorder.create(payload)
    ElMessage.success('工单提交成功')
    router.push('/workorder/my')
  } catch (e) {
    ElMessage.error(`提交失败: ${e.message}`)
  } finally {
    submitting.value = false
  }
}

onMounted(loadDevices)
</script>

<style scoped>
.page-container { padding: 16px; }
</style>
