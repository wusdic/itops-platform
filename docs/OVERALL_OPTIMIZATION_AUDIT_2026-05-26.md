# ITOps Platform 整体优化审计报告（代码实证版）

> 生成时间：2026-05-26；范围：后端 FastAPI、frontend/src、modules、整体优化要求.docx。当前只做审计与方案，不进入业务代码修复。

## 1. 审计基线

- 后端静态路由数量：453
- 前端 API 调用数量：333
- 设备相关模型/模块文件数量：14
- 疑似占位/短页面候选数量：11（需页面验证，不直接认定为 bug）

## 2. docx 问题逐项复核

| ID | 问题 | 当前状态 | 代码证据摘要 | 后续动作 |
|---|---|---|---|---|
| P0-1 | README/PHYSICAL_DEPLOY/deploy.sh 旧仓库地址 | 已完成 | `["未发现 itops-deploy 旧仓库引用"]` | 无需处理 |
| P2-dev-port | 前端 dev 端口不一致 | 已完成 | `{"vite_has_5173": true, "package_has_5173": true}` | 保持 vite.config.js 与 package.json 都为 5173 |
| P1-4/N-7 | 通知中心 messages/unread/read 单条消息能力 | 已完成 | `{"backend": [[813, "@router.get(\"/messages\", summary=\"获取站内消息列表\")"], [814, "async def get_messages("], [831, "messages = service.list_messages("], [840, "total = service.count_messages("], [847, "\"items\": [msg.to_di` | 如缺失则补后端 messages 路由和前端路径 |
| N-8/N-9 | 监控 metrics history/top 接口 | 已完成 | `{"backend_history": [[415, "@router.get(\"/metrics/history\", summary=\"查询指标历史\")"]], "backend_top": [[456, "@router.get(\"/metrics/top/{metric_type}\", summary=\"获取TopN指标\")"]], "frontend": [[69, "request.get(`/devices/` | 如缺失则补齐 API |
| N-5/N-6 | AI /ai/analyze 与 /ai/analyze/history | 已完成 | `{"backend": [[1181, "@router.post(\"/analyze/logs\", summary=\"analysislog\")"], [1440, "\"/analyze/{alert_id}/root-cause\","], [1553, "\"/analyze/{alert_id}/remediation\","], [1631, "# ============== C4: 统一分析接口（POST /ai` | 补统一分析接口并接前端 |
| N-10 | 告警转工单接口 | 已完成 | `{"backend": [[1490, "@router.post(\"/convert-to-workorder\", summary=\"告警转工单\")"]], "frontend": [[56, "convertToWorkorder: (alertId, data) => request.post('/workorders/convert-to-workorder', { alert_id: alertId, ...data ` | 统一路径，验证 curl |
| P0-2 | 前后端接口契约不统一 | 部分已修复/需继续验证 | `{"backend_routes": 453, "frontend_api_calls": 333, "known_fixed": ["notification messages", "monitoring metrics history/top", "AI analyze", "alert convert-to-workorder"]}` | 下一阶段做自动化 API 契约比对，逐项 curl 验证 404/422/500 |
| P0-3 | 设备主数据模型混乱 | 需进一步治理 | `{"device_model_files": ["modules/collection/device_manager.py", "modules/collection/device_fingerprint.py", "modules/foundation/db_models/adapter.py", "modules/foundation/db_models/monitoring.py", "modules/foundation/db_` | 确认 canonical Device 主表和 DTO；前端统一 ip/ip_address、type/status 枚举 |
| P0-4 | 自动化模块前后端产品模型不一致 | 需验证 | `{"backend": [[10, "- 保持 trigger-rules 和 rollback 相关 API 兼容"], [106, "@router.get(\"/scripts\", summary=\"获取脚本列表\")"], [107, "async def list_scripts("], [145, "@router.post(\"/scripts\", summary=\"创建脚本\", response_model=B` | 按 scripts/tasks/executions/trigger-rules 四类建立契约测试 |
| P1-1 | 网络扫描配置页面/入口 | 部分已具备/需页面验证 | `{"frontend_discovery_api": [[9, "getList: (params) => request.get('/discovery/networks', { params }),"], [10, "getById: (id) => request.get(`/discovery/networks/${id}`),"], [11, "create: (data) => request.post('/discover` | 用浏览器验证是否能创建扫描网段、发起扫描、导入设备 |
| P1-2 | 登录返回格式与前端期望 | 需运行验证 | `{"frontend_auth": [], "backend_auth": [[35, "access_token: str"], [36, "token_type: str = \"bearer\""], [40, "# 确保同时返回 access_token 和 token 两个字段"], [42, "data['token'] = data.get('access_token')"], [89, "def create_acces` | curl 登录并检查前端 token 取值路径 |
| P1-3 | 系统菜单/字典管理 | 需验证/可能缺后端路由 | `{"frontend_views": [], "backend_candidates": [{"file": "api/routes/admin.py", "method": "GET", "path": "/menu"}, {"file": "api/routes/admin.py", "method": "GET", "path": "/menus"}, {"file": "api/routes/admin.py", "method` | 若后端缺失，新增 menu/dict CRUD；若已有，前端对接 |
| P1-5 | AI Copilot/Analyze 闭环 | 接口已部分补齐/页面需验证 | `{"views": [], "backend_ai_routes": 17}` | 验证告警/工单/日志上下文是否可带入 AI 并生成处置建议 |
| P2-2 | FastAPI main.py 初始化过重 | 确认存在但暂不重构 | `{"api/main.py_lines": 308, "lifespan": [[42, "from api.lifespan import lifespan"], [64, "lifespan=lifespan,"], [109, "app.include_router("], [115, "app.include_router("], [121, "app.include_router("], [127, "app.include_` | P2 单独 Track，避免本轮大重构 |
| P3-1 | 前端占位/功能少页面 | 需页面级验证 | `{"candidate_pages": [{"file": "frontend/src/views/api-keys/index.vue", "lines": 278, "marker": true}, {"file": "frontend/src/views/deploy/canary.vue", "lines": 514, "marker": true}, {"file": "frontend/src/views/deploy/he` | 逐页浏览器验证；真实占位才改，不凭行数直接判断 |

## 3. 核心能力矩阵

| 能力 | 现有证据 | 结论 | 缺口/验证项 |
|---|---|---|---|
| 设备自动发现 | 后端 discovery 扫描/导入存在，前端 discovery API 存在 | 部分闭环 | 需页面验证扫描目标配置、进度、导入 |
| 设备详细识别 | enhanced_scanner + DeviceImporter 存在 | 部分闭环 | 需验证 OS/vendor/model/SNMP 字段实际落库 |
| 状态查验/指标采集 | device_metrics/monitoring/collection 路由存在 | 部分闭环 | 需 curl 验证采集任务和状态字段一致性 |
| 异常告警 | monitoring alerts/rules/trigger-rules 存在 | 部分闭环 | 需验证规则触发、通知、工单转换 |
| LLM研判 | ai chat/troubleshoot/analyze 存在 | 部分闭环 | 需验证本地模型配置、告警上下文注入 |
| 自动处置 | automation scripts/tasks/executions/rollback 存在 | 部分闭环 | 需验证脚本执行安全/审批/回滚 |
| 定期巡检 | inspection tasks/reports/results/statistics 存在 | 部分闭环 | 需验证调度器是否实际执行和归档 |
| 企业后台配置 | system/user/role 有，menu/dict 待验证 | 缺口 | 需补/对接 menu dict |

## 4. 建议优先级

### P0：先做可用性契约验证
1. 自动生成前端 API → 后端 OpenAPI 的契约比对清单，逐项 curl 验证 404/422/500。
2. 登录、设备列表、网络扫描、告警列表、告警转工单、AI 分析、巡检任务这 7 条主链路先跑通。

### P1：补齐业务闭环
1. 网络扫描页面：扫描目标配置 → 扫描进度 → 发现结果 → 导入设备。
2. 告警闭环：规则触发 → 通知 → AI 研判 → 转工单/自动化处置。
3. 巡检闭环：任务创建 → 定时执行 → 结果归档 → 报告导出。

### P2：架构治理
1. 设备主数据 DTO/枚举统一。
2. main.py 初始化拆分仅作为单独 Track，不在功能修复中顺手重构。
3. 自动化执行安全边界、审批和回滚统一。

## 5. 执行原则
- 先验证，后修复；每个问题只做最小必要修改。
- 修复后必须说明文件/行号、预期界面效果、验证方式。
- 每个修复点必须 curl 或页面验证，不能只看 build。
