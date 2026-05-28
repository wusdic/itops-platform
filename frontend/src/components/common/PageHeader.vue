<template>
  <div class="page-header" :class="{ 'has-breadcrumb': showBreadcrumb }">
    <div v-if="showBreadcrumb" class="breadcrumb-wrapper">
      <el-breadcrumb :separator-icon="ArrowRight">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-main">
      <div class="header-left">
        <div v-if="backRoute" class="back-btn" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
        </div>
        <div class="title-section">
          <h1 class="page-title">{{ title }}</h1>
          <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        </div>
      </div>

      <div class="header-right">
        <slot name="extra" />
        <el-space v-if="showToolbar">
          <el-button
            v-for="action in toolbarActions"
            :key="action.key"
            :type="action.type || 'default'"
            :icon="action.icon"
            :loading="action.loading"
            @click="action.handler"
          >
            {{ action.label }}
          </el-button>
        </el-space>
      </div>
    </div>

    <div v-if="$slots.tabs" class="header-tabs">
      <slot name="tabs" />
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  backRoute: { type: String, default: '' },
  showBreadcrumb: { type: Boolean, default: false },
  breadcrumbs: { type: Array, default: () => [] },
  showToolbar: { type: Boolean, default: true },
  toolbarActions: { type: Array, default: () => [] }
})

const router = useRouter()

const handleBack = () => {
  if (props.backRoute) {
    router.push(props.backRoute)
  } else {
    router.back()
  }
}
</script>

<style scoped lang="scss">
.page-header {
  margin-bottom: 20px;

  &.has-breadcrumb {
    .breadcrumb-wrapper {
      margin-bottom: 12px;
    }
  }
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f5f7fa;
  transition: background 0.2s;

  &:hover {
    background: #e8f0ff;
  }
}

.title-section {
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #1d2129;
    margin: 0;
  }

  .page-subtitle {
    font-size: 13px;
    color: #86909c;
    margin: 4px 0 0 0;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-tabs {
  margin-top: 16px;
}
</style>
