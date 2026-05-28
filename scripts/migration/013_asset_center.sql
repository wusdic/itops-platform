-- ============================================================
-- ITOps Platform - 资产中心数据库迁移
-- 版本: 013
-- 描述: 按文档8.1节创建资产中心核心表
-- 文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1
-- 运行方式: mysql -u root -p itops_platform < 013_asset_center.sql
-- ============================================================

USE itops_platform;

-- ============================================================
-- 1. 资产主表 (assets)
-- 平台所有可观测、可配置、可告警、可执行对象的统一账本
-- ============================================================
CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id VARCHAR(64) NOT NULL UNIQUE COMMENT '业务ID，如 AST-000001',
    name VARCHAR(128) NOT NULL COMMENT '资产名称',
    asset_type VARCHAR(64) NOT NULL COMMENT '类型: server/network/storage/security/middleware/database/app',
    sub_type VARCHAR(64) COMMENT '子类型: server_linux/server_windows/switch_firewall/...',
    status VARCHAR(32) DEFAULT 'active' COMMENT '状态: active/inactive/maintenance/decommissioned',
    
    -- 位置信息
    idc VARCHAR(128) COMMENT '机房',
    building VARCHAR(64) COMMENT '楼宇',
    floor VARCHAR(32) COMMENT '楼层',
    rack VARCHAR(64) COMMENT '机柜',
    rack_position VARCHAR(32) COMMENT '机柜位置',
    
    -- 厂商信息
    vendor VARCHAR(128) COMMENT '厂商',
    model VARCHAR(128) COMMENT '型号',
    serial_number VARCHAR(128) COMMENT '序列号',
    manufacturer VARCHAR(128) COMMENT '制造商',
    purchase_date DATE COMMENT '采购日期',
    warranty_end DATE COMMENT '保修结束',
    cost DECIMAL(12,2) COMMENT '成本',
    
    -- 操作系统/软件
    os_type VARCHAR(64) COMMENT '操作系统类型',
    os_version VARCHAR(128) COMMENT '操作系统版本',
    kernel_version VARCHAR(128) COMMENT '内核版本',
    cpu VARCHAR(128) COMMENT 'CPU信息',
    memory VARCHAR(64) COMMENT '内存',
    disk VARCHAR(256) COMMENT '磁盘',
    network_interfaces JSON COMMENT '网络接口列表',
    
    -- 管理接口
    ssh_port INT DEFAULT 22 COMMENT 'SSH端口',
    ssh_username VARCHAR(64) COMMENT 'SSH用户名',
    web_url VARCHAR(256) COMMENT 'Web管理URL',
    web_port INT COMMENT 'Web管理端口',
    
    -- 元数据
    tags JSON COMMENT '标签列表',
    custom_fields JSON COMMENT '自定义字段',
    metadata JSON COMMENT '扩展元数据',
    
    -- 业务关联
    business_id INT COMMENT '所属业务系统ID',
    business_name VARCHAR(128) COMMENT '所属业务系统名称',
    group_id INT COMMENT '所属资产组ID',
    
    -- 生命周期
    first_discovered_at DATETIME COMMENT '首次发现时间',
    last_seen_at DATETIME COMMENT '最后在线时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64) COMMENT '创建人',
    updated_by VARCHAR(64) COMMENT '更新人',
    
    -- 租户隔离
    tenant_id VARCHAR(64) COMMENT '租户ID',
    
    INDEX idx_asset_id (asset_id),
    INDEX idx_name (name),
    INDEX idx_asset_type (asset_type),
    INDEX idx_sub_type (sub_type),
    INDEX idx_status (status),
    INDEX idx_idc (idc),
    INDEX idx_vendor (vendor),
    INDEX idx_business_id (business_id),
    INDEX idx_group_id (group_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_first_discovered (first_discovered_at),
    INDEX idx_last_seen (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产主表';

-- ============================================================
-- 2. 资产IP地址表 (asset_ips)
-- 支持多IP、多网卡、IPv4/IPv6
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL COMMENT '资产ID',
    ip_address VARCHAR(64) NOT NULL COMMENT 'IP地址',
    ip_type VARCHAR(8) DEFAULT 'ipv4' COMMENT 'ipv4/ipv6',
    mac_address VARCHAR(64) COMMENT 'MAC地址',
    hostname VARCHAR(128) COMMENT '主机名（DNS反向解析）',
    interface_name VARCHAR(64) COMMENT '网卡名称，如 eth0',
    interface_type VARCHAR(32) COMMENT '网卡类型: physical/virtual/logical',
    is_management BOOLEAN DEFAULT FALSE COMMENT '是否管理接口',
    is_primary BOOLEAN DEFAULT FALSE COMMENT '是否主IP',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公网IP',
    vlan_id INT COMMENT 'VLAN ID',
    subnet_mask VARCHAR(64) COMMENT '子网掩码',
    gateway VARCHAR(64) COMMENT '网关',
    dns_servers JSON COMMENT 'DNS服务器',
    bandwidth VARCHAR(32) COMMENT '带宽',
    NAT_ip VARCHAR(64) COMMENT 'NAT转换后IP',
    NAT_port INT COMMENT 'NAT转换后端口',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    UNIQUE KEY uk_asset_ip_interface (asset_id, ip_address, interface_name),
    INDEX idx_ip_address (ip_address),
    INDEX idx_asset_id (asset_id),
    INDEX idx_mac_address (mac_address),
    INDEX idx_is_management (is_management),
    INDEX idx_is_primary (is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产IP地址表';

-- ============================================================
-- 3. 资产标签表 (asset_tags)
-- 支持多对多标签，一个标签可关联多个资产
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tag_key VARCHAR(64) NOT NULL COMMENT '标签键',
    tag_value VARCHAR(256) COMMENT '标签值',
    tag_color VARCHAR(16) DEFAULT '#1890ff' COMMENT '标签颜色',
    tag_category VARCHAR(64) COMMENT '标签分类: env/role/owner/business',
    description VARCHAR(256) COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_tag_key_value (tag_key, tag_value),
    INDEX idx_tag_key (tag_key),
    INDEX idx_tag_category (tag_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产标签定义表';

CREATE TABLE IF NOT EXISTS asset_tag_bindings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64) COMMENT '绑定人',
    
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES asset_tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_asset_tag (asset_id, tag_id),
    INDEX idx_asset_id (asset_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产标签绑定表';

-- ============================================================
-- 4. 资产分组表 (asset_groups)
-- 支持树形层级分组
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_code VARCHAR(64) NOT NULL UNIQUE COMMENT '分组编码',
    group_name VARCHAR(128) NOT NULL COMMENT '分组名称',
    parent_id INT COMMENT '父分组ID，NULL表示根分组',
    group_type VARCHAR(32) COMMENT '分组类型: idc/business/role/custom',
    description VARCHAR(256) COMMENT '描述',
    display_order INT DEFAULT 0 COMMENT '排序',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开（跨租户可见）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    tenant_id VARCHAR(64) COMMENT '租户ID',
    
    INDEX idx_parent_id (parent_id),
    INDEX idx_group_type (group_type),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产分组表';

-- ============================================================
-- 5. 资产关系表 (asset_relations)
-- 表达资产之间的拓扑关系、依赖关系、网络关系
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_asset_id INT NOT NULL COMMENT '源资产ID',
    target_asset_id INT NOT NULL COMMENT '目标资产ID',
    relation_type VARCHAR(32) NOT NULL COMMENT '关系类型: network/depends_on/contains/runs_on/connects_to',
    relation_label VARCHAR(128) COMMENT '关系标签，如"上联交换机"',
    bidirectional BOOLEAN DEFAULT FALSE COMMENT '是否双向关系',
    metadata JSON COMMENT '扩展属性，如带宽、端口号',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    
    FOREIGN KEY (source_asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    FOREIGN KEY (target_asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    UNIQUE KEY uk_relation (source_asset_id, target_asset_id, relation_type),
    INDEX idx_source_asset (source_asset_id),
    INDEX idx_target_asset (target_asset_id),
    INDEX idx_relation_type (relation_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产关系表';

-- ============================================================
-- 6. 资产凭证绑定表 (asset_credentials)
-- 关联资产与凭证（密码/密钥/Token）
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL COMMENT '资产ID',
    credential_id INT NOT NULL COMMENT '凭证ID（引用 credentials 表）',
    credential_type VARCHAR(32) NOT NULL COMMENT '凭证类型: ssh/api/snmp/vmware/ipmi',
    interface_name VARCHAR(64) COMMENT '应用接口，如 eth0',
    is_primary BOOLEAN DEFAULT TRUE COMMENT '是否主凭证',
    priority INT DEFAULT 0 COMMENT '优先级，优先使用高优先级',
    description VARCHAR(256) COMMENT '描述',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    last_verified_at DATETIME COMMENT '最后验证时间',
    last_success_at DATETIME COMMENT '最后成功使用时间',
    last_failure_at DATETIME COMMENT '最后失败时间',
    last_failure_reason VARCHAR(256) COMMENT '最后失败原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    -- credential_id 引用 credentials 表（后面阶段创建）
    UNIQUE KEY uk_asset_credential (asset_id, credential_id, interface_name),
    INDEX idx_asset_id (asset_id),
    INDEX idx_credential_id (credential_id),
    INDEX idx_credential_type (credential_type),
    INDEX idx_is_primary (is_primary),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产凭证绑定表';

-- ============================================================
-- 7. 资产采集配置表 (asset_collection_profiles)
-- 绑定采集模板到资产
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_collection_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL COMMENT '资产ID',
    profile_name VARCHAR(128) NOT NULL COMMENT '采集配置名称',
    collector_type VARCHAR(64) NOT NULL COMMENT '采集器类型: ssh/snmp/ipmi/redfish/vmware',
    collection_interval INT DEFAULT 60 COMMENT '采集间隔（秒）',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    config JSON COMMENT '采集器特定配置',
    metrics JSON COMMENT '采集指标列表',
    status VARCHAR(32) DEFAULT 'active' COMMENT '配置状态: active/paused/error',
    last_collection_at DATETIME COMMENT '最后采集时间',
    last_success_at DATETIME COMMENT '最后成功采集时间',
    last_failure_at DATETIME COMMENT '最后失败时间',
    last_failure_reason VARCHAR(256) COMMENT '最后失败原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    INDEX idx_asset_id (asset_id),
    INDEX idx_collector_type (collector_type),
    INDEX idx_enabled (enabled),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产采集配置表';

-- ============================================================
-- 8. 资产策略绑定表 (asset_policy_bindings)
-- 将策略绑定到资产/分组
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_policy_bindings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT COMMENT '资产ID，NULL表示按分组绑定',
    group_id INT COMMENT '分组ID',
    policy_id INT NOT NULL COMMENT '策略ID',
    policy_version VARCHAR(32) COMMENT '策略版本',
    binding_type VARCHAR(16) DEFAULT 'direct' COMMENT '绑定类型: direct/group/auto',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    priority INT DEFAULT 0 COMMENT '优先级',
    start_time DATETIME COMMENT '生效开始时间',
    end_time DATETIME COMMENT '生效结束时间',
    description VARCHAR(256) COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    
    -- policy_id 引用 policies 表（后面阶段创建）
    INDEX idx_asset_id (asset_id),
    INDEX idx_group_id (group_id),
    INDEX idx_policy_id (policy_id),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产策略绑定表';

-- ============================================================
-- 9. 资产生命周期事件表 (asset_lifecycle_events)
-- 记录资产全生命周期重要事件
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_lifecycle_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL COMMENT '资产ID',
    event_type VARCHAR(64) NOT NULL COMMENT '事件类型',
    event_subtype VARCHAR(64) COMMENT '事件子类型',
    severity VARCHAR(16) DEFAULT 'info' COMMENT '严重级别: critical/warning/info',
    description TEXT COMMENT '事件描述',
    actor VARCHAR(64) COMMENT '触发者: system/user',
    actor_name VARCHAR(128) COMMENT '触发者名称',
    metadata JSON COMMENT '扩展数据',
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '事件发生时间',
    trace_id VARCHAR(64) COMMENT '关联trace_id',
    
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    INDEX idx_asset_id (asset_id),
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity),
    INDEX idx_occurred_at (occurred_at),
    INDEX idx_trace_id (trace_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产生命周期事件表';

-- ============================================================
-- 事件类型参考：
-- discovered          - 资产发现
-- imported            - 手工导入
-- registered          - 注册登记
-- ssh_connected       - SSH连接成功
-- ssh_failed          - SSH连接失败
-- metric_first        - 首次采集到指标
-- metric_missing      - 指标中断
-- alert_triggered     - 触发告警
-- policy_bound        - 策略绑定
-- policy_triggered    - 策略触发
-- action_executed     - 执行动作
-- credential_updated  - 凭证更新
-- status_changed      - 状态变更
-- maintenance_start   - 进入维护
-- maintenance_end     - 维护结束
-- decommissioned     - 下线退役
-- ============================================================
