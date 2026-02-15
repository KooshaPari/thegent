<script setup lang="ts">
defineProps<{
  type?: 'tip' | 'warning' | 'danger' | 'note'
}>()
</script>

<template>
  <div class="callout" :class="type || 'note'">
    <div class="callout-title">
      <span v-if="type === 'tip'">💡 Tip</span>
      <span v-else-if="type === 'warning'">⚠️ Warning</span>
      <span v-else-if="type === 'danger'">❌ Danger</span>
      <span v-else>📝 Note</span>
    </div>
    <div class="callout-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.callout {
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  border-left: 4px solid;
}

.callout-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.callout.tip {
  background: #f6ffed;
  border-color: #52c41a;
}

.callout.warning {
  background: #fffbe6;
  border-color: #faad14;
}

.callout.danger {
  background: #fff1f0;
  border-color: #ff4d4f;
}

.callout.note {
  background: #f0f5ff;
  border-color: #1890ff;
}
</style>
