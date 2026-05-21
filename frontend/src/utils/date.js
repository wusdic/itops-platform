/**
 * 日期时间工具
 * 所有时间格式化统一使用平台配置的时区（而非浏览器本地时区）
 */

// 当前配置的时区，默认取浏览器本地时区
let _timezone = Intl.DateTimeFormat().resolvedOptions().timeZone

/**
 * 设置平台时区（从后端 system.timezone 配置读取后调用）
 * @param {string} tz IANA 时区名，如 'Asia/Shanghai'
 */
export const setTimezone = (tz) => {
  if (tz) _timezone = tz
}

/**
 * 获取当前时区
 */
export const getTimezone = () => _timezone

/**
 * 格式化日期（使用平台配置的时区）
 * @param {string|Date} date 日期字符串或对象
 * @param {string} format 格式字符串，如 'YYYY-MM-DD HH:mm:ss'
 */
export const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const opts = { timeZone: _timezone }
  const parts = {
    year: new Intl.DateTimeFormat('en-US', { ...opts, year: 'numeric' }).format(d),
    month: new Intl.DateTimeFormat('en-US', { ...opts, month: '2-digit' }).format(d),
    day: new Intl.DateTimeFormat('en-US', { ...opts, day: '2-digit' }).format(d),
    hour: new Intl.DateTimeFormat('en-US', { ...opts, hour: '2-digit', hour12: false }).format(d),
    minute: new Intl.DateTimeFormat('en-US', { ...opts, minute: '2-digit' }).format(d),
    second: new Intl.DateTimeFormat('en-US', { ...opts, second: '2-digit' }).format(d),
  }

  return format
    .replace('YYYY', parts.year)
    .replace('MM', parts.month)
    .replace('DD', parts.day)
    .replace('HH', parts.hour)
    .replace('mm', parts.minute)
    .replace('ss', parts.second)
}

/**
 * 相对时间描述
 */
export const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return formatDate(date, 'MM-DD HH:mm')
}

export const getWeekday = (date) => {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weekdays[new Date(date).getDay()]
}
