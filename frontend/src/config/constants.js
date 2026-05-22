// 系统常量配置
export const CONFIG = {
  // API
  REQUEST_TIMEOUT: 30000,
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // 轮询间隔 (ms)
  POLL_INTERVAL_SHORT: 30000,   // 30秒 - 设备列表、告警、工单列表
  POLL_INTERVAL_LONG: 60000,    // 60秒 - 通知计数

  // Token 检查 (ms)
  TOKEN_CHECK_INTERVAL: 60000,  // 1分钟

  // SSE/Streaming
  SSE_RECONNECT_DELAY: 5000,   // 5秒

  // 时间窗口 (ms)
  METRICS_TIME_WINDOW: 2 * 24 * 60 * 60 * 1000,  // 2天 - 监控图表时间范围

  // 搜索防抖 (ms)
  SEARCH_DEBOUNCE: 300,
}
