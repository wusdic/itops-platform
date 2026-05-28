<template>
  <div class="adapter-page">
    <el-tabs v-model="activeTab" type="line" animated>
      <el-tab-pane name="adapters" label="协议适配器">
        <el-card title="协议适配器模板" class="mb-4">
          <template #header>
            <div class="card-header">
              <span>协议适配器模板</span>
              <el-button type="primary" @click="openAddModal">
                <el-icon><Plus /></el-icon>
                新建适配器
              </el-button>
            </div>
          </template>
          <el-table
            :data="adapterList"
            :loading="adapterLoading"
            :row-key="row => row.id"
            stripe
            style="width: 100%"
          >
            <el-table-column v-for="col in adapterColumns" :key="col.key" v-bind="col" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane name="device-config" label="设备协议配置">
        <el-card title="设备协议配置" class="mb-4">
          <template #header>
            <div class="card-header">
              <span>设备协议配置</span>
              <el-button @click="loadDeviceProtocols" :loading="protocolLoading">
                <el-icon><RefreshRight /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-space direction="vertical" :size="12">
            <el-space>
              <el-select
                v-model="selectedDeviceId"
                :options="deviceOptions"
                placeholder="选择设备"
                style="width: 300px"
                filterable
                @change="onDeviceChange"
              />
              <el-button @click="testDeviceProtocol" :loading="testing" :disabled="!selectedDeviceId">测试连接</el-button>
            </el-space>
            <el-table
              :data="deviceProtocols"
              :loading="protocolLoading"
              :row-key="row => row.protocol_type"
              stripe
              style="width: 100%"
            >
              <el-table-column v-for="col in protocolColumns" :key="col.key" v-bind="col" />
            </el-table>
          <el-empty v-if="!loading && deviceProtocols.length === 0" description="暂无数据" />
          </el-space>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 新建/编辑适配器弹窗 -->
    <el-dialog v-model="showAddModal" :title="editingId ? '编辑适配器' : '新建适配器'" width="600px">
      <el-form label-position="top" label-width="120">
        <el-form-item label="协议类型">
          <el-select
            v-model="form.protocol_type"
            :options="protocolOptions"
            placeholder="选择协议"
            :disabled="!!editingId"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="模板名称">
          <el-input v-model.trim="form.name" placeholder="如: MySQL标准模板" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model.trim="form.description" type="textarea" placeholder="模板描述" />
        </el-form-item>

        <el-divider>默认配置</el-divider>

        <template v-if="form.protocol_type === 'snmp'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="SNMP版本">
            <el-select v-model="form.default_config.version" :options="snmpVersionOptions" style="width:100%" />
          </el-form-item>
          <el-form-item label="Community">
            <el-input v-model.trim="form.default_config.community" placeholder="public" />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'ssh'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.username" placeholder="root" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" placeholder="留空使用密钥" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'http' || form.protocol_type === 'zabbix' || form.protocol_type === 'prometheus' || form.protocol_type === 'redfish'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.username" placeholder="admin" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" placeholder="密码" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'mysql' || form.protocol_type === 'postgres'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.username" placeholder="root" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'redis'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" placeholder="无密码则留空" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'rabbitmq'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.username" placeholder="guest" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" placeholder="guest" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'vmware'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.user" placeholder="administrator@vsphere.local" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" show-password />
          </el-form-item>
        </template>

        <template v-if="form.protocol_type === 'browser'">
          <el-form-item label="端口">
            <el-input-number v-model.trim="form.default_config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model.trim="form.default_config.username" placeholder="admin" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.default_config.password" type="password" show-password />
          </el-form-item>
        </template>

        <el-form-item label="超时(秒)">
          <el-input-number v-model.trim="form.default_config.timeout" :min="5" :max="300" />
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space justify="end">
          <el-button @click="showAddModal = false">取消</el-button>
          <el-button type="primary" @click="saveAdapter" :loading="saving">保存</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import { adapters, request } from '@/api'

const activeTab = ref('adapters')
const adapterLoading = ref(false)
const protocolLoading = ref(false)
const saving = ref(false)
const testing = ref(false)
const showAddModal = ref(false)
const editingId = ref(null)

const adapterList = ref([])
const deviceProtocols = ref([])
const selectedDeviceId = ref(null)
const deviceOptions = ref([])

const snmpVersionOptions = [
  { label: 'v1', value: 'v1' },
  { label: 'v2c', value: 'v2c' },
  { label: 'v3', value: 'v3' },
]

const protocolOptions = [
  { label: 'SNMP', value: 'snmp' },
  { label: 'SSH', value: 'ssh' },
  { label: 'HTTP', value: 'http' },
  { label: 'WinRM', value: 'winrm' },
  { label: 'IPMI', value: 'ipmi' },
  { label: 'Kubernetes', value: 'kubernetes' },
  { label: 'Docker', value: 'docker' },
  { label: 'Zabbix', value: 'zabbix' },
  { label: 'Prometheus', value: 'prometheus' },
  { label: 'Browser', value: 'browser' },
  { label: 'Redfish', value: 'redfish' },
  { label: 'Syslog', value: 'syslog' },
  { label: 'Telnet', value: 'telnet' },
  { label: 'MySQL', value: 'mysql' },
  { label: 'PostgreSQL', value: 'postgres' },
  { label: 'Redis', value: 'redis' },
  { label: 'RabbitMQ', value: 'rabbitmq' },
  { label: 'Kafka', value: 'kafka' },
  { label: 'Elasticsearch', value: 'elasticsearch' },
  { label: 'VMware', value: 'vmware' },
]

const emptyForm = () => ({
  protocol_type: '',
  name: '',
  description: '',
  default_config: { port: 22, timeout: 30 },
  enabled: true,
})
const form = reactive(emptyForm())

// ==================== 适配器管理 ====================
const loadAdapters = async () => {
  adapterLoading.value = true
  try {
    const data = await adapters.getTemplates({ page_size: 100 })
    adapterList.value = data.items || []
  } catch (e) {
    ElMessage.error('加载适配器失败: ' + e.message)
  } finally {
    adapterLoading.value = false
  }
}

const openAddModal = () => {
  editingId.value = null
  Object.assign(form, emptyForm())
  showAddModal.value = true
}

const editAdapter = (row) => {
  editingId.value = row.id
  Object.assign(form, {
    protocol_type: row.protocol_type,
    name: row.name,
    description: row.description || '',
    default_config: { ...row.default_config },
    enabled: row.enabled,
  })
  showAddModal.value = true
}

const saveAdapter = async () => {
  if (!form.protocol_type || !form.name) {
    ElMessage.warning('请填写协议类型和模板名称')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await adapters.updateTemplate(editingId.value, { ...form })
    } else {
      await adapters.createTemplate({ ...form })
    }
    ElMessage.success('保存成功')
    showAddModal.value = false
    editingId.value = null
    loadAdapters()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const deleteAdapter = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除适配器「${row.name}」吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await adapters.deleteTemplate(row.id)
    ElMessage.success('删除成功')
    loadAdapters()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

const getTagType = (protocolType) => {
  const colors = {
    snmp: 'info', ssh: 'success', http: 'warning', mysql: 'error',
    redis: 'info', postgres: 'success', vmware: 'warning', kafka: 'error',
  }
  return colors[protocolType] || 'default'
}

const adapterColumns = [
  {
    title: '协议',
    key: 'protocol_type',
    width: 120,
    render({ row }) {
      return h('span', [
        h(ElTag, { type: getTagType(row.protocol_type), size: 'small' }, { default: () => row.protocol_type.toUpperCase() })
      ])
    }
  },
  { title: '模板名称', key: 'name', minWidth: 150, showOverflowTooltip: true },
  { title: '描述', key: 'description', minWidth: 150, showOverflowTooltip: true },
  { title: '默认端口', key: 'default_config.port', width: 100 },
  {
    title: '状态',
    key: 'enabled',
    width: 80,
    render({ row }) {
      return h(ElTag, { type: row.enabled ? 'success' : 'info', size: 'small' },
        { default: () => row.enabled ? '启用' : '禁用' })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    render({ row }) {
      return h(ElSpace, { size: 8 }, {
        default: () => [
          h(ElButton, { size: 'small', text: true, type: 'primary', onClick: () => editAdapter(row) },
            { default: () => '编辑' }),
          h(ElButton, { size: 'small', text: true, type: 'danger', onClick: () => deleteAdapter(row) },
            { default: () => '删除' }),
        ]
      })
    }
  },
]

// ==================== 设备协议配置 ====================
const loadDevices = async () => {
  try {
    const data = await request.get('/assets/device', { params: { page_size: 100 } })
    deviceOptions.value = (data.items || []).map(d => ({
      label: d.name + ' (' + d.ip_address + ')',
      value: d.id,
    }))
  } catch (e) {
    // load devices failed silently
  }
}

const onDeviceChange = async (deviceId) => {
  selectedDeviceId.value = deviceId
  await loadDeviceProtocols()
}

const loadDeviceProtocols = async () => {
  if (!selectedDeviceId.value) {
    deviceProtocols.value = []
    return
  }
  protocolLoading.value = true
  try {
    const data = await adapters.getDeviceProtocols(selectedDeviceId.value)
    deviceProtocols.value = data.items || []
  } catch (e) {
    ElMessage.error('加载设备协议失败')
  } finally {
    protocolLoading.value = false
  }
}

const testDeviceProtocol = async () => {
  if (!selectedDeviceId.value) {
    ElMessage.warning('请先选择设备')
    return
  }
  testing.value = true
  try {
    const configured = deviceProtocols.value.find(p => p.enabled && p.adapter_template_id)
    const protocolType = configured ? configured.protocol_type : 'snmp'

    const data = await adapters.testDeviceProtocol(selectedDeviceId.value, protocolType)
    if (data.success !== false) {
      ElMessage.success('连接成功: ' + (data.message || ''))
    } else {
      ElMessage.warning('连接失败: ' + (data.message || ''))
    }
  } catch (e) {
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

const updateDeviceProtocol = async (row, field, value) => {
  row[field] = value
  try {
    const payload = {
      device_id: selectedDeviceId.value,
      protocol_type: row.protocol_type,
      adapter_template_id: row.adapter_template_id || null,
      overrides: row.overrides || {},
      enabled: row.enabled,
    }

    await adapters.saveDeviceProtocols(selectedDeviceId.value, [payload])
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const protocolColumns = [
  {
    title: '协议',
    key: 'protocol_type',
    width: 120,
    render({ row }) {
      return h(ElTag, { type: getTagType(row.protocol_type), size: 'small' },
        { default: () => row.protocol_type.toUpperCase() })
    }
  },
  {
    title: '适配器模板',
    key: 'adapter_template_id',
    width: 200,
    render({ row }) {
      const opts = adapterList.value
        .filter(a => a.protocol_type === row.protocol_type && a.enabled)
        .map(a => ({ label: a.name, value: a.id }))

      if (!opts.length) return h('span', { style: 'color:#999' }, '无可用模板')

      return h(ElSelect, {
        modelValue: row.adapter_template_id,
        options: opts,
        size: 'small',
        placeholder: '选择模板',
        style: 'width:180px',
        clearable: true,
        'onUpdate:modelValue': (v) => updateDeviceProtocol(row, 'adapter_template_id', v),
      })
    }
  },
  {
    title: '覆盖参数(JSON)',
    key: 'overrides',
    showOverflowTooltip: true,
    render({ row }) {
      const json = JSON.stringify(row.overrides || {})
      return h(ElInput, {
        modelValue: json,
        size: 'small',
        placeholder: '{}',
        style: 'width:200px',
        'onUpdate:modelValue': (v) => {
          try { row.overrides = JSON.parse(v) } catch {}
        },
        blur: () => updateDeviceProtocol(row, 'overrides', row.overrides),
      })
    }
  },
  {
    title: '启用',
    key: 'enabled',
    width: 80,
    render({ row }) {
      return h(ElSwitch, {
        modelValue: row.enabled,
        size: 'small',
        'onUpdate:modelValue': (v) => updateDeviceProtocol(row, 'enabled', v),
      })
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render({ row }) {
      if (!row.adapter_template_id && (!row.overrides || Object.keys(row.overrides).length === 0)) {
        return h(ElTag, { type: 'info', size: 'small' }, { default: () => '未配置' })
      }
      return h(ElTag, { type: row.enabled ? 'success' : 'warning', size: 'small' },
        { default: () => row.enabled ? '已配置' : '已禁用' })
    }
  },
]

onMounted(() => {
  loadAdapters()
  loadDevices()
})
</script>

<style scoped>
.adapter-page { padding: 16px; }
.mb-4 { margin-bottom: 16px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
