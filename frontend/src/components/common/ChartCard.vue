<template>
  <div class="chart-card card" :class="{ 'show-controls': showControls }">
    <div v-if="showControls" class="widget-controls">
      <el-button-group size="small">
        <el-button
          @click.stop="toggleVisibility"
          :type="visible === false ? 'info' : 'default'"
          :icon="visible === false ? Hide : View"
        />
        <el-button
          @click.stop="toggleCollapse"
          :type="collapsed ? 'warning' : 'default'"
          :icon="collapsed ? DArrowRight : DArrowLeft"
        />
      </el-button-group>
    </div>

    <div v-show="visible !== false && !collapsed" class="card-inner">
      <div class="card-header">
        <span class="card-title">{{ title }}</span>
        <div class="card-extra">
          <slot name="extra" />
        </div>
      </div>
      <div class="card-body">
        <div ref="chartRef" class="chart-container" :class="chartClass"></div>
        <div v-if="$slots.table" class="table-slot">
          <slot name="table" />
        </div>
      </div>
    </div>

    <div v-show="visible !== false && collapsed" class="card-collapsed">
      <span>{{ title }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { View, Hide, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  title: { type: String, default: '图表' },
  chartClass: { type: String, default: '' },
  showControls: { type: Boolean, default: false },
  visible: { type: Boolean, default: true },
  collapsed: { type: Boolean, default: false },
  // 自动初始化图表
  autoInit: { type: Boolean, default: false },
  // 图表选项
  option: { type: Object, default: null }
})

const emit = defineEmits(['visibility-change', 'collapse-change', 'chart-ready'])

const chartRef = ref(null)
let chartInstance = null

const toggleVisibility = () => {
  emit('visibility-change', props.visible === false ? true : false)
}

const toggleCollapse = () => {
  emit('collapse-change', !props.collapsed)
}

// 初始化 ECharts 实例
const initChart = (option) => {
  if (!chartRef.value || typeof window.echarts === 'undefined') {
    console.warn('Chart container or ECharts not available')
    return null
  }

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = window.echarts.init(chartRef.value)
  
  if (option) {
    chartInstance.setOption(option)
  }

  emit('chart-ready', chartInstance)
  return chartInstance
}

// 设置图表选项
const setOption = (option) => {
  if (chartInstance) {
    chartInstance.setOption(option)
  }
}

// 调整图表大小
const resize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 暴露方法给父组件
defineExpose({
  initChart,
  setOption,
  resize,
  getInstance: () => chartInstance
})

// 监听窗口变化
let resizeTimer = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    resize()
  }, 100)
}

onMounted(() => {
  if (props.autoInit && props.option) {
    nextTick(() => initChart(props.option))
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped lang="scss">
.chart-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
}

.widget-controls {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.card-inner {
  width: 100%;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
}

.card-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-body {
  padding: 16px 20px;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.table-slot {
  margin-top: 16px;
}

.card-collapsed {
  padding: 12px 16px;
  font-size: 12px;
  color: #86909c;
}
</style>
