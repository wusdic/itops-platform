# 设备指纹信息增强 - 系统规划

## 核心目的
不登录也能看到设备完整指纹信息（操作系统、CPU、内存、磁盘、网络等），并在前端正确展示。

## 现状分析

### 后端现状
- `api/routes/asset.py` 的 `get_devices` 和 `get_device/{id}` 都依赖 `get_current_user` → 未登录被拦截
- `LinuxCollector.collect_all()` 已采集：distro, kernel, os_name, uptime, cpu(model/cores/usage/load), memory, disks, network(interfaces+MAC), network_stats, processes, ports, services, users
- `WindowsCollector.collect_all()` 已采集：system(OS/version/arch/manufacturer/model/serial), disks, network, services, processes, event_logs, software, updates, performance
- `get_devices()` 只把 `os_type` 和 `manufacturer` 从采集数据写入返回结果，浪费了大量已有数据

### 前端现状
- `devices.vue` 表格列：hostname, ip_address, device_type, status, os_type, last_collect_time
- 抽屉详情：只显示 hostname, ip, 类型, 状态, OS, 制造商, 型号, SN, 位置, IDC, 机柜
- **缺失展示**：CPU信息、内存信息、磁盘信息、网络接口信息、运行时间、负载、进程数等

### 数据库现状
- `Device` 模型已有：cpu, memory, disk, network_interfaces 字段（JSON存储）
- 但采集数据写入 metrics 后，这些 DB 字段从未被填充

## 系统架构

```
Collector采集 → DeviceManager.get_last_metrics() 
                           ↓
              metrics.metrics 字典（包含所有采集数据）
                           ↓
         get_devices() 提取关键字段 → 前端展示
```

## 目标字段映射

### Linux 设备（从 last_metrics.metrics）
| 采集字段 | 说明 | 前端展示位置 |
|---------|------|------------|
| distro | 发行版 | OS类型 |
| system.os_name | 完整OS名 | OS版本 |
| system.kernel | 内核版本 | 详情 |
| system.uptime | 运行时间 | 详情 |
| cpu.model | CPU型号 | CPU列 |
| cpu.cores | CPU核心数 | CPU列 |
| cpu.usage | CPU使用率 | 性能 |
| memory.total_mb | 内存总量 | 内存列 |
| memory.usage_percent | 内存使用率 | 性能 |
| disks | 磁盘列表(JSON) | 详情 |
| network | 网络接口列表 | 详情 |
| ports | 监听端口列表 | 详情 |
| services | 服务列表 | 详情 |

### Windows 设备（从 last_metrics.metrics）
| 采集字段 | 说明 | 前端展示位置 |
|---------|------|------------|
| system.os_name | 操作系统 | OS类型 |
| system.version | 版本 | OS版本 |
| system.architecture | 架构 | 详情 |
| system.manufacturer | 制造商 | 制造商 |
| system.model | 型号 | 型号 |
| system.serial_number | 序列号 | SN |
| cpu_usage | CPU使用率 | 性能 |
| memory_usage | 内存使用率 | 性能 |
| disks | 磁盘列表 | 详情 |
| network | 网络接口 | 详情 |
| software | 已安装软件 | 详情 |

## 执行计划

### Track 1: 后端 - 去除登录拦截 + 丰富字段
1. 修改 `asset.py`：移除 `get_devices` 和 `get_device/{id}` 的 `current_user` 依赖
2. 修改 `_device_to_dict()`：新增字段映射
3. 修改 `get_devices()`：从 `last_metrics.metrics` 提取更多字段
4. 重启容器验证

### Track 2: 后端 - Linux 采集增强
为 Linux 增加：
- `collect_hardware_info()` - SMBIOS/DMI硬件信息（型号/厂商/序列号）
- `collect_container_info()` - Docker/containerd容器信息
- `collectPackage_info()` - RPM/DEB包数量
- 确保 collect_all() 包含所有字段

### Track 3: 前端 - devices.vue 表格列扩展
新增列：
- CPU（型号 + 核心数）
- 内存（总量 + 使用率）
- 运行时间
- 负载
- 磁盘使用率
- 在线时长

### Track 4: 前端 - 设备详情抽屉扩展
在详情抽屉中新增：
- 系统信息区块（内核/运行时间/运行级别）
- CPU区块（型号/核心/使用率/负载）
- 内存区块（总量/可用/使用率）
- 磁盘区块（列表+使用率）
- 网络区块（接口+IP+MAC）
- 进程区块（Top5 CPU/Mem）
- 端口区块（监听端口）
- 服务区块（运行中服务数）

### Track 5: 构建验证
- `npm run build`
- `docker compose down api && docker compose up -d api`
- 浏览器强制刷新验证

## 验收标准
1. 不登录状态下访问 `/monitoring/devices` 正常显示设备列表（无401）
2. 设备列表显示 CPU、内存、运行时间等新字段
3. 点击设备展开详情，显示完整指纹信息
4. Linux 设备显示发行版、内核、负载、端口等
5. Windows 设备显示 OS、架构、已安装软件等
