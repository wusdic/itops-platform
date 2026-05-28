<template>
  <div
    class="stat-card"
    :class="{ 'is-clickable': clickable, 'is-collapsed': collapsed }"
    :style="{ borderLeftColor: color }"
    @click="handleClick"
  >
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

    <div v-show="visible !== false && !collapsed" class="stat-content">
      <div class="stat-icon-wrap" :style="{ background: bgColor }">
        <el-icon :size="24" :color="color">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-body">
        <div class="stat-value">{{ displayValue }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>

    <div v-show="visible !== false && collapsed" class="stat-collapsed">
      <span class="collapsed-hint">{{ label }}: {{ displayValue }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { View, Hide, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  // 数值
  value: { type: [Number, String], default: 0 },
  // 标签
  label: { type: String, default: '' },
  // 图标组件
  icon: { type: Object, default: null },
  // 主题色
  color: { type: String, default: '#165dff' },
  // 是否可点击
  clickable: { type: Boolean, default: false },
  // 显示自定义控件
  showControls: { type: Boolean, default: false },
  // 可见性（用于自定义模式）
  visible: { type: Boolean, default: true },
  // 折叠状态
  collapsed: { type: Boolean, default: false },
  // 数值格式化
  formatter: { type: Function, default: null }
})

const emit = defineEmits(['click', 'visibility-change', 'collapse-change'])

const bgColor = computed(() => {
  const hex = props.color.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, 0.1)`
})

const displayValue = computed(() => {
  if (props.formatter) {
    return props.formatter(props.value)
  }
  return props.value
})

const handleClick = () => {
  if (props.clickable) {
    emit('click', props.value)
  }
}

const toggleVisibility = () => {
  emit('visibility-change', props.visible === false ? true : false)
}

const toggleCollapse = () => {
  emit('collapse-change', !props.collapsed)
}
</script>

<style scoped lang="scss">
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  border-left: 4px solid;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;

  &.is-clickable {
    cursor: pointer;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
  }

  &.is-collapsed {
    padding: 12px 16px;
    justify-content: flex-start;
  }
}

.widget-controls {
  position: absolute;
  top: 8px;
  right: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
}

.stat-collapsed {
  .collapsed-hint {
    font-size: 12px;
    color: #86909c;
  }
}
</style>
