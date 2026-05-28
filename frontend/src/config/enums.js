/**
 * ITOps Platform 枚举常量
 * 与后端 Python 枚举保持一致（modules/foundation/db_models/）
 * 用于前端下拉选项、筛选条件、状态显示
 */

// ============ 设备相关 ============

/** 设备类型 */
export const DEVICE_TYPES = [
  // 服务器
  { label: 'Windows服务器', value: 'server_windows' },
  { label: 'Linux服务器', value: 'server_linux' },
  { label: 'VMware虚拟机', value: 'server_vmware' },
  { label: 'Hyper-V虚拟机', value: 'server_hyperv' },
  { label: 'KVM虚拟机', value: 'server_kvm' },
  // 网络设备
  { label: '交换机', value: 'network_switch' },
  { label: '路由器', value: 'network_router' },
  { label: '防火墙', value: 'network_firewall' },
  { label: 'WAF', value: 'network_waf' },
  { label: '负载均衡', value: 'network_loadbalancer' },
  { label: 'VPN网关', value: 'network_vpn' },
  { label: '无线AP', value: 'network_ap' },
  { label: '无线控制器', value: 'network_ac' },
  // 安全设备
  { label: '入侵检测(IDS)', value: 'security_ids' },
  { label: '入侵防御(IPS)', value: 'security_ips' },
  { label: '杀毒软件', value: 'security_antivirus' },
  // 存储设备
  { label: '存储阵列', value: 'storage_array' },
  { label: 'NAS存储', value: 'storage_nas' },
  { label: '磁带库', value: 'storage_tape' },
  // 其他
  { label: '其他设备', value: 'other' },
]

/** 设备状态 */
export const DEVICE_STATUSES = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
  { label: '警告', value: 'warning' },
  { label: '严重', value: 'critical' },
  { label: '维护中', value: 'maintenance' },
  { label: '未知', value: 'unknown' },
]

/** 设备状态颜色映射 */
export const DEVICE_STATUS_COLORS = {
  online: '#67C23A',
  offline: '#909399',
  warning: '#E6A23C',
  critical: '#F56C6C',
  maintenance: '#909399',
  unknown: '#909399',
}

// ============ 告警相关 ============

/** 告警级别 */
export const ALERT_SEVERITIES = [
  { label: '提示', value: 'info' },
  { label: '警告', value: 'warning' },
  { label: '错误', value: 'error' },
  { label: '严重', value: 'critical' },
]

/** 告警级别颜色映射 */
export const ALERT_SEVERITY_COLORS = {
  info: '#909399',
  warning: '#E6A23C',
  error: '#F56C6C',
  critical: '#F56C6C',
}

// ============ 工单相关 ============

/** 工单状态 */
export const WORKORDER_STATUSES = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '待审批', value: 'pending_approval' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已解决', value: 'resolved' },
  { label: '已关闭', value: 'closed' },
  { label: '已取消', value: 'cancelled' },
]

/** 工单优先级 */
export const WORKORDER_PRIORITIES = [
  { label: 'P1 - 紧急', value: 'P1' },
  { label: 'P2 - 高', value: 'P2' },
  { label: 'P3 - 中', value: 'P3' },
  { label: 'P4 - 低', value: 'P4' },
]

/** 工单优先级颜色映射 */
export const WORKORDER_PRIORITY_COLORS = {
  P1: '#F56C6C',
  P2: '#E6A23C',
  P3: '#409EFF',
  P4: '#67C23A',
}

/** 工单状态颜色映射 */
export const WORKORDER_STATUS_COLORS = {
  pending: '#E6A23C',
  processing: '#409EFF',
  pending_approval: '#9C27B0',
  approved: '#67C23A',
  rejected: '#F56C6C',
  resolved: '#67C23A',
  closed: '#909399',
  cancelled: '#909399',
}

// ============ 工单类型 ============

/** 工单类型 */
export const WORKORDER_TYPES = [
  { label: '故障报修', value: '故障报修' },
  { label: '变更申请', value: '变更申请' },
  { label: '权限申请', value: '权限申请' },
  { label: '数据查询', value: '数据查询' },
  { label: '安全事件', value: '安全事件' },
  { label: '性能优化', value: '性能优化' },
  { label: '容量规划', value: '容量规划' },
  { label: '日常巡检', value: '日常巡检' },
  { label: '其他', value: '其他' },
]

// ============ 通知相关 ============

/** 通知类型 */
export const NOTIFICATION_TYPES = [
  { label: '邮件', value: 'email' },
  { label: '短信', value: 'sms' },
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wechat' },
  { label: '飞书', value: 'feishu' },
  { label: 'Webhook', value: 'webhook' },
]

/** 通知状态 */
export const NOTIFICATION_STATUSES = [
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' },
]

// ============ 扫描相关 ============

/** 扫描协议 */
export const SCAN_PROTOCOLS = [
  { label: 'ICMP Ping', value: 'icmp' },
  { label: 'TCP Connect', value: 'tcp' },
  { label: 'SNMP', value: 'snmp' },
  { label: 'SSH', value: 'ssh' },
]

// ============ 脚本相关 ============

/** 脚本类型 */
export const SCRIPT_TYPES = [
  { label: 'Shell', value: 'shell' },
  { label: 'Python', value: 'python' },
  { label: 'PowerShell', value: 'powershell' },
  { label: 'Ansible', value: 'ansible' },
]

/** 脚本状态 */
export const SCRIPT_STATUSES = [
  { label: '草稿', value: 'draft' },
  { label: '已发布', value: 'published' },
  { label: '已禁用', value: 'disabled' },
]

// ============ 执行相关 ============

/** 执行状态 */
export const EXECUTION_STATUSES = [
  { label: '等待中', value: 'pending' },
  { label: '运行中', value: 'running' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '超时', value: 'timeout' },
  { label: '已取消', value: 'cancelled' },
]

/** 执行状态颜色映射 */
export const EXECUTION_STATUS_COLORS = {
  pending: '#E6A23C',
  running: '#409EFF',
  success: '#67C23A',
  failed: '#F56C6C',
  timeout: '#E6A23C',
  cancelled: '#909399',
}
