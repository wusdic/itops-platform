#!/usr/bin/env python3
"""
知识库填充脚本 - 向 ITOps Platform 填充真实的 IT 运维知识
用法: python seed_knowledge_base.py
"""
import json, urllib.request, urllib.error, time

API_BASE = "http://localhost:8000/api/v1"
# 先尝试登录获取 token
def login():
    req = urllib.request.Request(
        f"{API_BASE}/auth/login",
        data=json.dumps({"username": "admin", "password": "Admin@123456"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    body = json.loads(resp.read())
    # 支持多种响应格式
    token = (body.get("data", {}) or body or {}).get("token") or body.get("access_token", "")
    return token

def api(method, path, data=None, token=None, retry=2):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers=headers, method=method)
    for attempt in range(retry):
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read()
            try:
                err = json.loads(body)
                print(f"    ⚠️ HTTP {e.code}: {err.get('detail', err)}")
            except:
                print(f"    ⚠️ HTTP {e.code}: {body[:100]}")
            if e.code in (401, 403):
                return None
            if attempt == retry - 1:
                raise
        except Exception as e:
            if attempt == retry - 1:
                raise
            time.sleep(1)
    return None

def main():
    print("=== 登录 ===")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print(f"✅ 登录成功")

    # ========== 1. 创建分类 ==========
    print("\n=== 1. 创建分类 ===")
    categories = [
        {"name": "服务器运维", "code": "SERVER", "doc_type": "sop"},
        {"name": "网络运维", "code": "NETWORK", "doc_type": "sop"},
        {"name": "数据库运维", "code": "DATABASE", "doc_type": "sop"},
        {"name": "中间件运维", "code": "MIDDLEWARE", "doc_type": "sop"},
        {"name": "存储运维", "code": "STORAGE", "doc_type": "sop"},
        {"name": "安全运维", "code": "SECURITY", "doc_type": "sop"},
        {"name": "容器与云原生", "code": "CONTAINER", "doc_type": "sop"},
        {"name": "监控与告警", "code": "MONITORING", "doc_type": "sop"},
        {"name": "故障案例库", "code": "FAULT", "doc_type": "fault_case"},
        {"name": "变更管理", "code": "CHANGE", "doc_type": "sop"},
    ]
    cat_id_map = {}
    for cat in categories:
        r = api("POST", "/knowledge/category", cat, token)
        if r and "id" in r:
            cat_id_map[cat["code"]] = r["id"]
            print(f"  ✅ 分类: {cat['name']} (id={r['id']})")
        elif r is None:
            print(f"  ⚠️  分类 {cat['name']} 需要认证，跳过")
        else:
            print(f"  ⚠️  分类 {cat['name']}: {r}")

    # ========== 2. 创建标签 ==========
    print("\n=== 2. 创建标签 ===")
    tags_data = [
        {"name": "Linux", "category_id": cat_id_map.get("SERVER")},
        {"name": "Windows", "category_id": cat_id_map.get("SERVER")},
        {"name": "CPU", "category_id": cat_id_map.get("SERVER")},
        {"name": "内存", "category_id": cat_id_map.get("SERVER")},
        {"name": "磁盘", "category_id": cat_id_map.get("STORAGE")},
        {"name": "SSD", "category_id": cat_id_map.get("STORAGE")},
        {"name": "网络", "category_id": cat_id_map.get("NETWORK")},
        {"name": "DNS", "category_id": cat_id_map.get("NETWORK")},
        {"name": "负载均衡", "category_id": cat_id_map.get("NETWORK")},
        {"name": "MySQL", "category_id": cat_id_map.get("DATABASE")},
        {"name": "Redis", "category_id": cat_id_map.get("DATABASE")},
        {"name": "PostgreSQL", "category_id": cat_id_map.get("DATABASE")},
        {"name": "MongoDB", "category_id": cat_id_map.get("DATABASE")},
        {"name": "nginx", "category_id": cat_id_map.get("MIDDLEWARE")},
        {"name": "Tomcat", "category_id": cat_id_map.get("MIDDLEWARE")},
        {"name": "Docker", "category_id": cat_id_map.get("CONTAINER")},
        {"name": "Kubernetes", "category_id": cat_id_map.get("CONTAINER")},
        {"name": "Prometheus", "category_id": cat_id_map.get("MONITORING")},
        {"name": "Grafana", "category_id": cat_id_map.get("MONITORING")},
        {"name": "告警", "category_id": cat_id_map.get("MONITORING")},
        {"name": "安全", "category_id": cat_id_map.get("SECURITY")},
        {"name": "防火墙", "category_id": cat_id_map.get("SECURITY")},
        {"name": "权限", "category_id": cat_id_map.get("SECURITY")},
        {"name": "高可用", "category_id": None},
        {"name": "备份", "category_id": cat_id_map.get("STORAGE")},
        {"name": "迁移", "category_id": None},
        {"name": "性能优化", "category_id": None},
    ]
    tag_id_map = {}
    for tag in tags_data:
        r = api("POST", "/knowledge/tag", tag, token)
        if r and "id" in r:
            tag_id_map[tag["name"]] = r["id"]
            print(f"  ✅ 标签: {tag['name']} (id={r['id']})")
        elif r is None:
            print(f"  ⚠️  标签 {tag['name']} 需要认证，跳过")
        else:
            print(f"  ⚠️  标签 {tag['name']}: {r}")

    # ========== 3. 创建 SOP 文档 ==========
    print("\n=== 3. 创建 SOP 文档 ===")
    sops = [
        {
            "title": "Linux 服务器 CPU 负载过高排查流程",
            "content": """# Linux 服务器 CPU 负载过高排查流程

## 1. 适用场景
服务器 CPU 使用率持续超过 80%，或 Load Average 超过 CPU 核心数。

## 2. 排查步骤

### 2.1 查看整体 CPU 使用情况
```bash
# 查看 CPU 使用率（每核）
top -c
# 按 P 查看占用最高的进程
top 然后按 P

# 查看 CPU 详细信息
mpstat -P ALL 1 5
vmstat 1 5
```

### 2.2 定位高 CPU 进程
```bash
# 找出 CPU 占用最高的 10 个进程
ps aux --sort=-%cpu | head -n 11

# 查看指定进程的线程 CPU 占用
ps -p <PID> -L -o pid,tid,%cpu,cmd
top -H -p <PID>
```

### 2.3 分析 Java 进程（如果有）
```bash
# Java 进程堆栈分析
jstack <PID> > /tmp/jstack_<PID>.log

# 查看 GC 情况（可能引发 CPU 高）
jstat -gc <PID> 1000 10
```

### 2.4 检查系统状态
```bash
# 查看中断分布（IRQ）
cat /proc/interrupts

# 检查 CPU 频率
cpufreq-info

# 查看 CPU 温度
sensors
```

## 3. 常见原因
- 业务流量突增
- 定时任务集中执行
- Java Full GC 导致 CPU 飙升
- 挖矿木马或其他恶意进程
- 内核参数配置不当

## 4. 应急处理
1. `kill -STOP <PID>` 暂停进程
2. 确认原因后 `kill -CONT` 恢复或 `kill -9` 终止
3. 横向扩展增加服务器

## 5. 预防措施
- 配置 CPU 使用率告警（阈值 80%）
- 避免单服务器部署关键业务
- 定期巡检服务器性能基线
- 使用 `atop` 记录历史资源占用
""",
            "category_id": cat_id_map.get("SERVER"),
            "tags": "Linux,CPU,性能优化",
        },
        {
            "title": "MySQL 数据库连接数过高处理手册",
            "content": """# MySQL 数据库连接数过高处理手册

## 1. 问题识别
当 `show processlist` 显示大量连接，或应用出现 `Too many connections` 错误时，表明连接数已超出上限。

## 2. 排查步骤

### 2.1 查看当前连接数
```sql
-- 查看当前连接数
SHOW STATUS LIKE 'Threads_connected';

-- 查看最大连接数
SHOW VARIABLES LIKE 'max_connections';

-- 查看当前所有连接
SHOW PROCESSLIST;
```

### 2.2 按用户/Host 分组统计
```sql
SELECT user, host, COUNT(*) as cnt
FROM information_schema.processlist
GROUP BY user, host
ORDER BY cnt DESC;
```

## 3. 快速处理

### 3.1 杀掉空闲连接
```sql
-- 杀掉指定主机的所有空闲连接（Sleep状态超过300秒）
SELECT CONCAT('KILL ', id, ';')
FROM information_schema.processlist
WHERE command = 'Sleep' AND time > 300;
```

### 3.2 调整临时连接数
```sql
-- 临时增加最大连接数
SET GLOBAL max_connections = 2000;
```

## 4. 根因分析
- 应用连接池配置过小或泄漏
- 慢查询阻塞连接
- 长事务未提交
- 短连接应用频繁创建新连接

## 5. 预防措施
- 合理配置 `max_connections`（建议 500-2000）
- 使用连接池（ Druid / HikariCP）
- 配置 `wait_timeout` 和 `interactive_timeout`
- 部署连接监控告警
""",
            "category_id": cat_id_map.get("DATABASE"),
            "tags": "MySQL,数据库,性能优化",
        },
        {
            "title": "Nginx 502/504 错误排查与解决方案",
            "content": """# Nginx 502/504 错误排查与解决方案

## 错误类型
- **502 Bad Gateway**：Nginx 无法从上游获取有效响应
- **504 Gateway Timeout**：上游服务响应超时

## 排查步骤

### 1. 检查 Nginx 错误日志
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 2. 检查上游服务状态
```bash
# 检查 FastCGI/PHP-FPM 进程
ps aux | grep php-fpm

# 检查 uWSGI/Django 进程
ps aux | grep uwsgi

# 检查 Node.js/后端服务
netstat -tlnp | grep <端口>
```

### 3. 常见原因与处理

| 原因 | 表现 | 解决方案 |
|------|------|---------|
| PHP-FPM 进程池耗尽 | fastcgi_queue 队列满 | 增加 `pm.max_children`，优化 PHP 脚本 |
| 后端服务宕机 | upstream timed out | 重启后端服务，检查网络连通性 |
| 缓冲区不足 | upstream sent too big header | 增加 `fastcgi_buffer_size` |
| 慢查询阻塞 | connection refused | 优化数据库查询，增加超时时间 |

### 4. 关键配置调优
```nginx
fastcgi_connect_timeout 60;
fastcgi_send_timeout 300;
fastcgi_read_timeout 300;
fastcgi_buffer_size 64k;
fastcgi_buffers 4 64k;
fastcgi_busy_buffers_size 128k;
fastcgi_temp_file_write_size 128k;
proxy_read_timeout 300;
proxy_send_timeout 300;
```

## 5. 预防措施
- 配置健康检查
- 限制单 IP 请求频率
- 监控 upstream 响应时间
- 设置合理的超时时间
""",
            "category_id": cat_id_map.get("MIDDLEWARE"),
            "tags": "nginx,中间件",
        },
        {
            "title": "Kubernetes Pod 无法启动排查指南",
            "content": """# Kubernetes Pod 无法启动排查指南

## 常见状态
- `Pending`：调度失败或资源不足
- `ImagePullBackOff`：镜像拉取失败
- `CrashLoopBackOff`：容器反复崩溃
- `Error`：容器以错误状态终止

## 排查步骤

### 1. 查看 Pod 状态
```bash
kubectl get pod <pod-name> -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous
```

### 2. 常见问题处理

#### ImagePullBackOff
```bash
# 检查镜像是否存在
docker images | grep <image>

# 检查 secret 是否正确
kubectl get secret -n <namespace>

# 使用拉取镜像
kubectl debug <pod-name> -n <namespace> --image=<correct-image>
```

#### CrashLoopBackOff
```bash
# 查看详细日志
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous

# 检查资源限制
kubectl describe pod <pod-name> | grep -A 5 "Limits"
```

#### Pending（资源不足）
```bash
# 检查节点资源
kubectl describe nodes | grep -A 5 "Allocated resources"

# 检查 Pod 调度情况
kubectl get events --sort-by=.lastTimestamp -n <namespace>
```

## 3. 节点层问题
```bash
# 检查 kubelet 状态
systemctl status kubelet
journalctl -u kubelet -n 100

# 检查节点磁盘
df -h
kubectl describe node <node-name> | grep -E "Conditions|Storage"

# 检查 DNS 解析
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default
```
""",
            "category_id": cat_id_map.get("CONTAINER"),
            "tags": "Kubernetes,Docker,容器与云原生",
        },
        {
            "title": "Prometheus 告警规则配置与告警处理流程",
            "content": """# Prometheus 告警规则配置与告警处理流程

## 告警规则文件示例
```yaml
groups:
  - name: node_exporter_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高"
          description: "实例 {{ $labels.instance }} CPU 使用率已超过 80% 超过 5 分钟"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "实例 {{ $labels.instance }} 内存使用率已超过 85%"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "磁盘空间不足"
```

## 告警处理 SOP
1. 收到告警后 5 分钟内确认
2. 查看 Grafana 关联面板分析趋势
3. 检查是否有变更记录（变更窗口内优先回滚）
4. 定位根因后执行对应预案
5. 告警恢复后更新事件记录

## 告警抑制配置
```yaml
inhibit_rules:
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['instance']
```
""",
            "category_id": cat_id_map.get("MONITORING"),
            "tags": "Prometheus,Grafana,告警",
        },
        {
            "title": "DNS 解析故障排查标准流程",
            "content": """# DNS 解析故障排查标准流程

## 1. 常见 DNS 故障表现
- 域名无法解析（`ping: unknown host`）
- 特定地区/运营商无法访问
- 解析延迟高（首次访问慢）
- 解析结果错误（IP 不正确）

## 2. 排查步骤

### 2.1 本地解析测试
```bash
# 测试域名解析
nslookup <domain>
dig <domain> +trace
host <domain>

# 刷新本地 DNS 缓存
# Linux
systemd-resolve --flush-caches
# Windows
ipconfig /flushdns
```

### 2.2 分层测试
```bash
# 测试权威 DNS
dig @8.8.8.8 google.com
dig @114.114.114.114 google.com

# 测试内网 DNS
dig @<internal-dns-ip> <internal-domain>

# 测试递归解析路径
dig +trace example.com
```

### 2.3 检查 DNS 服务器状态
```bash
# 检查 DNS 服务进程
systemctl status named
systemctl status bind9

# 查看 DNS 查询日志
tail -f /var/log/named/query.log
```

## 3. 常见故障处理
| 故障 | 原因 | 解决 |
|------|------|------|
| 权威 NS 不一致 | NS 记录未同步 | 等待 TTL 过期或强制刷新 |
| CNAME 循环 | 配置错误 | 检查 CNAME 链 |
| 缓存投毒 | 安全攻击 | 升级 DNS 软件 |
| 解析超时 | 网络问题 | 检查防火墙/路由 |
""",
            "category_id": cat_id_map.get("NETWORK"),
            "tags": "DNS,网络",
        },
        {
            "title": "Redis 内存满了怎么办 - OOM 排查与数据迁移",
            "content": """# Redis 内存满了怎么办 - OOM 排查与数据迁移

## 1. 识别问题
```bash
# 查看内存使用
redis-cli info memory
redis-cli info memory | grep used_memory_human

# 查看最大内存限制
redis-cli config get maxmemory

# 查看内存碎片
redis-cli info memory | grep mem_fragmentation_ratio
```

## 2. 紧急处理
```bash
# 删除过期 key（主动释放）
redis-cli -h <host> -p <port> --scan --pattern "*" | head -1000 | xargs redis-cli -h <host> -p <port> unlink

# 设置过期时间
redis-cli expire <key> 3600

# 调整内存策略
redis-cli config set maxmemory-policy allkeys-lru
```

## 3. 分析内存占用
```bash
# 按大小查看 TOP 10 key
redis-cli --bigkeys

# 抽样分析 key 类型分布
redis-cli --scan --pattern "*" | head -10000 | xargs -I{} redis-cli type {}
```

## 4. 数据迁移（从机升主）
```bash
# 在从节点执行
redis-cli replicaof no one

# 修改应用程序连接新主节点
```

## 5. 预防措施
- 设置 `maxmemory`，建议留 20% buffer
- 使用 `volatile-lru` 淘汰策略
- 监控内存使用率，阈值 80% 告警
- 定期 `BGSAVE` 持久化 RDB 备份
""",
            "category_id": cat_id_map.get("DATABASE"),
            "tags": "Redis,数据库,高可用",
        },
        {
            "title": "防火墙规则变更安全管理流程",
            "content": """# 防火墙规则变更安全管理流程

## 变更前检查
1. 确认变更窗口（通常为 22:00-06:00）
2. 评估影响范围（哪些业务/用户受影响）
3. 准备回滚方案（记录当前规则快照）
4. 通知相关人员

## 规则变更步骤
```bash
# 1. 备份当前规则
iptables-save > /root/iptables.backup.$(date +%Y%m%d%H%M%S)

# 2. 添加新规则（建议使用 ipset 管理 IP 白名单）
ipset create whitelist hash:ip
ipset add whitelist 10.0.0.0/8

# 3. 应用规则
iptables -A INPUT -p tcp --dport 443 -m set --match-set whitelist src -j ACCEPT

# 4. 验证规则生效
iptables -L -n -v | grep <port>
```

## 回滚操作
```bash
# 立即回滚
iptables-restore < /root/iptables.backup.<timestamp>
```

## 合规要求
- 所有规则变更必须记录在变更管理系统
- 高危端口（22, 3389）不对互联网开放
- 数据库端口仅对应用网段开放
- 定期审计防火墙规则（建议每月）
""",
            "category_id": cat_id_map.get("SECURITY"),
            "tags": "防火墙,安全,权限",
        },
    ]

    for sop in sops:
        r = api("POST", "/knowledge/sop", sop, token)
        if r and "id" in r:
            print(f"  ✅ SOP: {sop['title'][:40]} (id={r['id']})")
        elif r is None:
            print(f"  ⚠️  SOP 需要认证，跳过")
        else:
            print(f"  ⚠️  SOP {sop['title'][:30]}: {str(r)[:80]}")

    # ========== 4. 创建故障案例 ==========
    print("\n=== 4. 创建故障案例 ===")
    fault_cases = [
        {
            "title": "生产环境 MySQL 主从复制中断",
            "fault_level": "P1",
            "fault_category": "数据库",
            "symptom": "从库数据落后主库超过 30 分钟，业务报表查询出现数据不一致告警。监控显示 `Seconds_Behind_Master` 从 0 跳升至 1800+，从库只读状态已自动切换为读写。",
            "root_cause": "从库执行大事务时（误删除历史数据），从库 SQL 线程因 `Lock wait timeout exceeded` 而断开与主库的连接。复制中断后，网络抖动导致重连机制未能自动恢复。",
            "solution": "1. 确认从库当前Relay Log位置；2. 在主库执行 `SHOW BINLOG EVENTS` 找到对应位置；3. 使用 `CHANGE MASTER TO` 重新指向正确位置；4. `START SLAVE`；5. 验证 `SHOW SLAVE STATUS\\G` 两线程均Yes。",
            "prevention": "大事务拆分为小批次（单次不超过 5000 行）；主从复制链路上增加延时监控（阈值 5 分钟告警）；重要删除操作前先在测试环境验证。",
            "tags": "MySQL,数据库,高可用",
        },
        {
            "title": "Kubernetes 集群所有 Pod 网络不通",
            "fault_level": "P1",
            "fault_category": "网络",
            "symptom": "集群内所有 Pod 之间网络全部不通，`kubectl exec` 进入容器也无法 ping 通其他 Pod。Node 节点之间 SSH 正常，但容器间通信完全断裂。",
            "root_cause": "CoreDNS 在升级过程中被重启，CoreDNS 的 ConfigMap 中 `forward` 策略指向了一个已失效的 DNS 服务器，导致集群内所有基于服务名（ClusterIP）的 DNS 解析全部失败。",
            "solution": "1. 恢复 CoreDNS ConfigMap 的 `forward` 配置；2. `kubectl rollout restart deployment/coredns -n kube-system`；3. 验证 DNS：`kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default`；4. 确认 Pod 网络恢复。",
            "prevention": "CoreDNS 升级前检查 ConfigMap 配置；部署 CoreDNS 高可用（多副本）；增加 DNS 解析成功率监控。",
            "tags": "Kubernetes,网络,DNS",
        },
        {
            "title": "Nginx  upstream 502 错误导致业务中断",
            "fault_level": "P2",
            "fault_category": "中间件",
            "symptom": "用户反馈页面间歇性返回 502 Bad Gateway，刷新后恢复，约 10% 请求失败。",
            "root_cause": "PHP-FPM 的 `pm.max_children` 设置为 50，但高峰时段并发 PHP 请求超过 50，PHP-FPM 队列积压。新请求因等待超时被 Nginx 502。",
            "solution": "1. 临时增加 `pm.max_children` 到 200；2. `service php-fpm reload`；3. 观察 `pm.active_processes` 稳定在 100 以下；4. 后续优化 PHP 慢查询，减少单请求占用进程时间。",
            "prevention": "基于历史峰值配置 `max_children`；增加 PHP-FPM 队列监控；使用 `pm.status_path` 暴露状态页面给 Prometheus。",
            "tags": "nginx,中间件,高可用",
        },
        {
            "title": "Prometheus 查询超时导致 Grafana 仪表盘空白",
            "fault_level": "P2",
            "fault_category": "监控",
            "symptom": "Grafana 部分仪表盘页面加载不出来，浏览器控制台显示 `gateway timeout` 或 `504`。其他监控系统正常。",
            "root_cause": "Prometheus 由于 `rate()` 查询范围过大（90天），且存在大量 `label_values` 子查询，导致单个查询占用内存超过 30GB，引发 OOM 被 kill，查询超时。",
            "solution": "1. 增加 Prometheus 内存限制；2. 优化查询表达式，避免大范围 `rate()`；3. 使用 Recording Rules 预计算常用指标；4. 重启 Prometheus 后 Grafana 恢复。",
            "prevention": "Prometheus 内存建议 64GB+；重要查询配置查询超时；使用 Thanos 或 VictoriaMetrics 做长期存储。",
            "tags": "Prometheus,Grafana,告警",
        },
        {
            "title": "服务器被植入挖矿木马",
            "fault_level": "P1",
            "fault_category": "安全",
            "symptom": "CPU 使用率 100%，但 `top` 查看无明显高占用进程。安全扫描发现定时任务包含可疑脚本 `/tmp/.cache/stream`，网络连接向境外矿池地址。",
            "root_cause": "Redis 未设置密码且暴露在公网，攻击者通过 Redis 写入 crontab 任务下载并执行挖矿脚本。",
            "solution": "1. 立即隔离服务器（断网或关机）；2. 删除所有可疑 crontab 任务；3. 删除 `/tmp/.cache`、`/var/tmp/` 下可疑文件；4. 为 Redis 设置强密码并绑定本地IP；5. 检查其他服务器是否有类似入侵痕迹；6. 恢复后重新部署业务。",
            "prevention": "Redis 不对公网开放；Redis 设置强密码（`requirepass`）；服务器禁止 SSH 密码登录，使用密钥；部署主机入侵检测系统（HIDS）。",
            "tags": "安全,Linux",
        },
        {
            "title": "Docker 磁盘空间占满导致容器无法启动",
            "fault_level": "P2",
            "fault_category": "容器",
            "symptom": "部分 Pod 无法启动，`kubectl describe pod` 显示 `docker-storage-monitor` 磁盘空间不足。Docker 日志报错 `no space left on device`。",
            "root_cause": "容器日志未配置日志轮转，单个容器日志文件超过 50GB；加上 `/var/lib/docker/overlay2` 大量未清理的dangling镜像，导致磁盘占满。",
            "solution": "1. 清理容器日志：`truncate -s 0 /var/lib/docker/containers/*/*.log`；2. 删除 dangling 镜像：`docker image prune -f`；3. 删除已停止容器：`docker container prune -f`；4. 重启 Docker：`systemctl restart docker`；5. 配置日志轮转（`max-size`、`max-file`）。",
            "prevention": "Docker daemon.json 配置日志驱动和轮转；定期 `docker system prune -a`；监控 `/var/lib/docker` 磁盘使用率；提醒开发者应用日志输出到 stdout。",
            "tags": "Docker,Kubernetes,磁盘",
        },
    ]

    for case in fault_cases:
        r = api("POST", "/knowledge/fault-case", case, token)
        if r and "id" in r:
            print(f"  ✅ 案例: {case['title'][:40]} (id={r['id']})")
        elif r is None:
            print(f"  ⚠️  故障案例需要认证，跳过")
        else:
            print(f"  ⚠️  故障案例 {case['title'][:30]}: {str(r)[:80]}")

    # ========== 5. 验证结果 ==========
    print("\n=== 5. 验证填充结果 ===")
    r_sops = api("GET", "/knowledge/sop", token=token)
    r_cases = api("GET", "/knowledge/fault-case", token=token)
    r_cats = api("GET", "/knowledge/category", token=token)
    r_tags = api("GET", "/knowledge/tag", token=token)
    r_stats = api("GET", "/knowledge/stats", token=token)

    print(f"  SOP 文档: {r_sops.get('total', '?') if r_sops else '?'} 条")
    print(f"  故障案例: {r_cases.get('total', '?') if r_cases else '?'} 条")
    print(f"  分类:     {r_cats.get('total', '?') if r_cats else '?'} 条")
    print(f"  标签:     {len(r_tags.get('items', [])) if r_tags else '?'} 条")
    if r_stats:
        print(f"  统计: {json.dumps(r_stats, ensure_ascii=False)}")

    print("\n✅ 知识库填充完成！")

if __name__ == "__main__":
    main()
