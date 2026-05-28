<template>
  <div class="filter-bar" :class="{ 'is-compact': compact }">
    <div class="filter-items">
      <el-form
        :model="modelValue"
        :inline="true"
        :label-width="labelWidth"
        @submit.prevent="handleSubmit"
      >
        <slot />
      </el-form>
    </div>
    <div v-if="$slots.actions || showDefaultActions" class="filter-actions">
      <el-button @click="handleReset">{{ resetText }}</el-button>
      <el-button type="primary" native-type="submit" @click="handleSubmit">
        {{ searchText }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Object, required: true },
  labelWidth: { type: [String, Number], default: '80px' },
  compact: { type: Boolean, default: false },
  showDefaultActions: { type: Boolean, default: true },
  searchText: { type: String, default: '搜索' },
  resetText: { type: String, default: '重置' }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const handleSubmit = () => {
  emit('search', { ...props.modelValue })
}

const handleReset = () => {
  const resetData = {}
  Object.keys(props.modelValue).forEach(key => {
    resetData[key] = ''
  })
  emit('update:modelValue', resetData)
  emit('reset')
}
</script>

<style scoped lang="scss">
.filter-bar {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;

  &.is-compact {
    padding: 12px 16px;
  }
}

.filter-items {
  flex: 1;

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 4px;
}
</style>
