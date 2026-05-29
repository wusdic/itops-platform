<template>
  <div class="ldap-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>LDAP / AD 集成配置</span>
          <el-button type="primary" @click="openCreateDialog">新增配置</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="配置名称">
          <el-input v-model="searchName" placeholder="搜索配置名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadConfigs">搜索</el-button>
          <el-button @click="searchName=''; loadConfigs()">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="configs" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column prop="server" label="服务器" min-width="180">
          <template #default="{ row }">{{ row.server }}:{{ row.port }}</template>
        </el-table-column>
        <el-table-column prop="base_dn" label="基准DN" min-width="180" show-overflow-tooltip />
        <el-table-column prop="enabled" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sync_interval_minutes" label="同步周期" width="100" align="center">
          <template #default="{ row }">{{ row.sync_interval_minutes || 60 }}分钟</template>
        </el-table-column>
        <el-table-column prop="last_sync_at" label="最后同步" width="160">
          <template #default="{ row }">{{ row.last_sync_at || '从未同步' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="info" @click="testConnection(row)">测试</el-button>
            <el-button size="small" type="warning" @click="syncUsers(row)">同步</el-button>
            <el-button size="small" type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadConfigs"
          @current-change="loadConfigs"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="130px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：公司LDAP" />
        </el-form-item>
        <el-form-item label="服务器地址" prop="server">
          <el-input v-model="form.server" placeholder="ldap://ldap.company.com 或 ldaps://..." />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="form.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="使用SSL" prop="use_ssl">
          <el-switch v-model="form.use_ssl" />
        </el-form-item>
        <el-form-item label="Bind DN" prop="bind_dn">
          <el-input v-model="form.bind_dn" placeholder="cn=admin,dc=company,dc=com" />
        </el-form-item>
        <el-form-item label="Bind密码" prop="bind_password">
          <el-input v-model="form.bind_password" type="password" show-password placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="基准DN" prop="base_dn">
          <el-input v-model="form.base_dn" placeholder="dc=company,dc=com" />
        </el-form-item>
        <el-form-item label="用户搜索过滤器" prop="user_filter">
          <el-input v-model="form.user_filter" placeholder="(uid={username})" />
        </el-form-item>
        <el-form-item label="用户搜索基础" prop="user_search_base">
          <el-input v-model="form.user_search_base" placeholder="ou=Users,dc=company,dc=com" />
        </el-form-item>
        <el-form-item label="用户名字段" prop="username_attr">
          <el-input v-model="form.username_attr" placeholder="sAMAccountName 或 uid" />
        </el-form-item>
        <el-form-item label="邮箱字段" prop="email_attr">
          <el-input v-model="form.email_attr" placeholder="mail" />
        </el-form-item>
        <el-form-item label="显示名字段" prop="display_name_attr">
          <el-input v-model="form.display_name_attr" placeholder="displayName 或 cn" />
        </el-form-item>
        <el-form-item label="同步周期" prop="sync_interval_minutes">
          <el-input-number v-model="form.sync_interval_minutes" :min="5" :max="1440" /> 分钟
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试连接结果 -->
    <el-dialog v-model="testResultVisible" title="连接测试结果" width="450px">
      <el-alert v-if="testResult" :type="testResult.success ? 'success' : 'error'" show-icon>
        <p>{{ testResult.message }}</p>
        <p v-if="testResult.simulated" style="font-size:12px;color:#909399">* ldap3 未安装或服务器不可达，结果为模拟数据</p>
      </el-alert>
      <template #footer><el-button @click="testResultVisible = false">关闭</el-button></template>
    </el-dialog>

    <!-- 同步日志 -->
    <el-dialog v-model="syncLogsVisible" title="同步日志" width="800px">
      <el-table v-loading="syncLogsLoading" :data="syncLogs" stripe max-height="400">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="users_synced" label="同步用户数" width="120" />
        <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
        <el-table-column prop="started_at" label="开始时间" width="160" />
        <el-table-column prop="completed_at" label="完成时间" width="160" />
      </el-table>
      <template #footer><el-button @click="syncLogsVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as ldapApi from '@/api/ldap'

const loading = ref(false)
const submitLoading = ref(false)
const testResultVisible = ref(false)
const syncLogsVisible = ref(false)
const syncLogsLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const configs = ref([])
const syncLogs = ref([])
const testResult = ref(null)
const formRef = ref(null)

const searchName = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogTitle = computed(() => isEdit.value ? '编辑LDAP配置' : '新增LDAP配置')

const defaultForm = () => ({
  name: '',
  server: 'ldap://',
  port: 389,
  use_ssl: false,
  bind_dn: '',
  bind_password: '',
  base_dn: '',
  user_filter: '(objectClass=user)',
  user_search_base: '',
  username_attr: 'sAMAccountName',
  email_attr: 'mail',
  display_name_attr: 'displayName',
  sync_interval_minutes: 60,
  description: '',
  enabled: true
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  server: [{ required: true, message: '请输入服务器地址', trigger: 'blur' }],
  base_dn: [{ required: true, message: '请输入基准DN', trigger: 'blur' }]
}

async function loadConfigs() {
  loading.value = true
  try {
    const res = await ldapApi.getLDAPConfigs({ page: page.value, page_size: pageSize.value, name: searchName.value })
    configs.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    ElMessage.error('加载LDAP配置失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEdit.value = false
  Object.assign(form, defaultForm())
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  ldapApi.getLDAPConfig(row.id).then(res => {
    Object.assign(form, res.data)
    form.bind_password = '' // 不返回密码
    dialogVisible.value = true
  }).catch(() => ElMessage.error('加载配置详情失败'))
}

function resetForm() {
  formRef.value?.resetFields()
}

async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      const data = { ...form }
      if (!data.bind_password) delete data.bind_password
      await ldapApi.updateLDAPConfig(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await ldapApi.createLDAPConfig(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadConfigs()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitLoading.value = false
  }
}

async function deleteConfig(row) {
  await ElMessageBox.confirm(`确定删除配置"${row.name}"？`, '确认删除')
  await ldapApi.deleteLDAPConfig(row.id)
  ElMessage.success('删除成功')
  loadConfigs()
}

async function testConnection(row) {
  try {
    const res = await ldapApi.testLDAPConfig(row.id)
    testResult.value = res.data
    testResultVisible.value = true
  } catch (e) {
    ElMessage.error('测试连接失败')
  }
}

async function syncUsers(row) {
  try {
    ElMessage.info('同步任务已启动，请稍后查看同步日志')
    await ldapApi.syncLDAPUsers(row.id)
    // 打开同步日志
    syncLogsLoading.value = true
    syncLogsVisible.value = true
    const res = await ldapApi.getLDAPSyncLogs(row.id, { page: 1, page_size: 10 })
    syncLogs.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    syncLogsLoading.value = false
  }
}

loadConfigs()
</script>

<style scoped>
.ldap-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 16px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
