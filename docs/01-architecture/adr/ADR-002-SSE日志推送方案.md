# ADR-002: 自动化执行日志推送采用 SSE 而非 WebSocket

> **状态**：已接受
> **日期**：2026-05-29
> **决策者**：ITOps Platform 开发团队

---

## 背景

自动化执行（automation execution）过程中，需要将 stdout/stderr 实时推送给前端。当前技术选型有 SSE（Server-Sent Events）和 WebSocket 两种方案。

## 决策

采用 **SSE（Server-Sent Events）** 作为实时日志推送方案。

- **端点**：`GET /api/v1/automation/executions/{id}/stream`
- **实现**：SSEProducer 类，基于 asyncio 实现，支持 Redis PubSub 跨进程和内存队列双模式
- **数据格式**：`data: <json>\n\n`
- **断线重连**：前端 EventSource 自动重连，SSE 原生支持

## 备选方案

| 方案 | 优点 | 缺点 |
|------|------|------|
| SSE（当前选型）✅ | 浏览器原生支持；单向下行；自动重连；实现简单；HTTP/1.1 兼容 | 单向（服务器→客户端）；需轮询鉴权 |
| WebSocket | 双向；低延迟 | 需特殊前端库；反向代理（Nginx）配置复杂；握手协议不同 |
| Long Polling | HTTP 兼容性好 | 实现复杂；资源消耗高 |

## 结论

SSE 更适合"服务端推送日志→前端展示"的单向场景，且实现和运维成本更低。WebSocket 的双向能力在当前场景无必要。

## 后续

如未来需要双向通信（如前端发送控制命令），可升级为 WebSocket，届时只需在 `/ws/` 路径下单独挂载。
