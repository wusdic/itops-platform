<template>
  <div class="page-card" :class="{ 'no-padding': noPadding }">
    <div v-if="title || $slots.header" class="page-card-header">
      <slot name="header">
        <div class="header-content">
          <h3 v-if="title" class="page-card-title">{{ title }}</h3>
          <p v-if="description" class="page-card-desc">{{ description }}</p>
        </div>
        <div v-if="$slots.actions" class="header-actions">
          <slot name="actions" />
        </div>
      </slot>
    </div>
    <div class="page-card-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  noPadding: { type: Boolean, default: false }
})
</script>

<style scoped lang="scss">
.page-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.page-card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  :deep(.el-space) {
    width: 100%;
  }
}

.header-content {
  flex: 1;
}

.page-card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
  margin: 0;
}

.page-card-desc {
  font-size: 13px;
  color: #86909c;
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-card-body {
  padding: 20px;

  .no-padding & {
    padding: 0;
  }
}
</style>
