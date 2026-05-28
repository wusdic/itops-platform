import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

/**
 * ECharts 封装 composable
 */
export function useChart(containerRef, options = {}) {
  const {
    autoResize = true,
    theme = 'default'
  } = options

  const chartInstance = ref(null)
  const isReady = ref(false)

  const initChart = (opts) => {
    if (!containerRef.value || typeof window.echarts === 'undefined') {
      console.warn('Chart container or ECharts not available')
      return null
    }

    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    chartInstance.value = window.echarts.init(containerRef.value, theme)
    isReady.value = true

    if (opts) {
      chartInstance.value.setOption(opts)
    }

    return chartInstance.value
  }

  const setOption = (opts) => {
    if (chartInstance.value) {
      chartInstance.value.setOption(opts, { notMerge: true })
    }
  }

  const resize = () => {
    if (chartInstance.value) {
      chartInstance.value.resize()
    }
  }

  const dispose = () => {
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
      isReady.value = false
    }
  }

  // 窗口变化时自动调整大小
  let resizeTimer = null
  const handleResize = () => {
    if (resizeTimer) clearTimeout(resizeTimer)
    resizeTimer = setTimeout(() => {
      resize()
    }, 100)
  }

  if (autoResize) {
    window.addEventListener('resize', handleResize)
  }

  onUnmounted(() => {
    if (autoResize) {
      window.removeEventListener('resize', handleResize)
    }
    if (resizeTimer) clearTimeout(resizeTimer)
    dispose()
  })

  return {
    chartInstance,
    isReady,
    initChart,
    setOption,
    resize,
    dispose
  }
}

/**
 * 图表通用配置生成器
 */
export const chartConfig = {
  // 通用网格配置
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },

  // 通用 Tooltip 配置
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e8e8e8',
    borderWidth: 1,
    textStyle: {
      color: '#1d2129'
    }
  },

  // 折线图配置
  lineOption: (data, color = '#165dff') => ({
    tooltip: chartConfig.tooltip,
    grid: chartConfig.grid,
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      data: data.values,
      lineStyle: { color },
      itemStyle: { color }
    }]
  }),

  // 饼图配置
  pieOption: (data, radius = ['40%', '70%']) => ({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [{
      type: 'pie',
      radius,
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' }
      },
      data
    }]
  }),

  // 柱状图配置
  barOption: (data, color = '#165dff') => ({
    tooltip: chartConfig.tooltip,
    grid: chartConfig.grid,
    xAxis: {
      type: 'category',
      data: data.categories
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'bar',
      data: data.values,
      itemStyle: { color }
    }]
  })
}
