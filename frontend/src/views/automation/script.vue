<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>脚本管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建规则
          </el-button>
        </div>
      </template>

      <el-space style="margin-bottom: 12px">
        <el-input v-model.trim="searchKeyword" placeholder="搜索规则名称" clearable style="width: 200px" @change="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterType" :options="typeOptions" placeholder="规则类型" clearable style="width: 140px" @change="loadData" />
      </el-space>

      <el-table :data="ruleList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="conditions_count" label="条件数" width="90">
          <template #default="{ row }">
            <span>{{ Array.isArray(row.conditions) ? row.conditions.length : (row.conditions ? '1' : '0') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="actions_count" label="动作数" width="90">
          <template #default="{ row }">
            <span>{{ Array.isArray(row.actions) ? row.actions.length : (row.actions ? '1' : '0') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" quaternary type="info" @click="handleTestRule(row)">测试</el-button>
            <el-button size="small" quaternary type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" quaternary type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && ruleList.length === 0" description="暂无数据" />

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 新建/编辑规则 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" label-placement="left" label-width="100">
        <el-form-item label="规则名称" required>
          <el-input v-model.trim="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="form.type" :options="typeOptions" placeholder="请选择" style="width: 100%" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="条件配置">
          <el-input v-model.trim="form.conditions" type="textarea" :rows="4" placeholder="请输入触发条件 (JSON格式)" />
        </el-form-item>
        <el-form-item label="动作配置">
          <el-input v-model.trim="form.actions" type="textarea" :rows="4" placeholder="请输入执行动作 (JSON格式)" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space justify="end">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 测试结果 -->
    <el-dialog v-model="testDialogVisible" title="测试规则" width="600px">
      <div v-loading="testing" style="padding: 8px 0;">
        <el-input type="textarea" v-model="testResult" :rows="15" readonly placeholder="暂无测试结果" />
      </div>
      <template #footer>
        <el-space justify="end">
          <el-button @click="testDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleTest" :loading="testing">重新测试</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { automation } from '@/api'

const message = ElMessage
const loading = ref(false)
const submitting = ref(false)
const testing = ref(false)
const ruleList = ref([])
const searchKeyword = ref('')
const filterType = ref(null)
const dialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogTitle = ref('新建规则')
const testResult = ref('')
const currentTestRule = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({ id: null, name: '', type: 'threshold', enabled: true, conditions: '', actions: '', description: '' })

const typeOptions = [
  { label: '阈值触发', value: 'threshold' },
  { label: '趋势触发', value: 'trend' },
  { label: '异常触发', value: 'anomaly' },
  { label: '周期触发', value: 'periodic' }
]

const getTypeText = (t) => ({ threshold: '阈值触发', trend: '趋势触发', anomaly: '异常触发', periodic: '周期触发' })[t] || t

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filterType.value) params.type = filterType.value
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await automation.triggerRules.getList(params)
    if (!res || typeof res !== 'object') throw new Error('响应格式异常')
    ruleList.value = res.items || res.data?.items || []
    pagination.total = res.total || res.data?.total || 0
  } catch (e) {
    message.error(`加载规则失败: ${e.message}`)
    ruleList.value = []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '新建规则'
  Object.assign(form, { id: null, name: '', type: 'threshold', enabled: true, conditions: '', actions: '', description: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑规则'
  Object.assign(form, {
    id: row.id,
    name: row.name,
    type: row.type || 'threshold',
    enabled: row.enabled ?? true,
    conditions: typeof row.conditions === 'string' ? row.conditions : JSON.stringify(row.conditions, null, 2),
    actions: typeof row.actions === 'string' ? row.actions : JSON.stringify(row.actions, null, 2),
    description: row.description || ''
  })
  dialogVisible.value = true
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除触发规则「${row.name}」吗？`, '删除确认', { type: 'warning' })
  try {
    await automation.triggerRules.delete(row.id)
    message.success('删除成功')
    loadData()
  } catch (e) {
    message.error(`删除失败: ${e.message}`)
  }
}

async function handleTestRule(row) {
  currentTestRule.value = row
  testDialogVisible.value = true
  testResult.value = ''
  await handleTest()
}

async function handleTest() {
  if (!currentTestRule.value) return
  testing.value = true
  testResult.value = ''
  try {
    const data = await automation.triggerRules.test(currentTestRule.value.id)
    testResult.value = JSON.stringify(data, null, 2)
  } catch (e) {
    testResult.value = `测试失败: ${e.message}`
    message.error(`测试失败: ${e.message}`)
  } finally {
    testing.value = false
  }
}

async function submitForm() {
  if (!form.name) { message.warning('请填写规则名称'); return }
  submitting.value = true
  try {
    const payload = { ...form }
    try {
      if (payload.conditions) {
        const parsed = JSON.parse(payload.conditions)
        payload.conditions = parsed
      }
    } catch { /* keep as string if not valid JSON */ }
    try {
      if (payload.actions) {
        const parsed = JSON.parse(payload.actions)
        payload.actions = parsed
      }
    } catch { /* keep as string if not valid JSON */ }

    if (form.id) {
      await automation.triggerRules.update(form.id, payload)
    } else {
      await automation.triggerRules.create(payload)
    }
    message.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    message.error(`操作失败: ${e.message}`)
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 16px; }
</style>