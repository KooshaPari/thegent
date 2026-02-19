<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  type?: 'tip' | 'warning' | 'danger' | 'note' | 'info' | 'success' | 'question' | 'example'
  title?: string
  collapsible?: boolean
}>(), {
  type: 'note',
  collapsible: false
})

const collapsed = ref(false)

const icons = {
  tip: '💡',
  warning: '⚠️',
  danger: '❌',
  note: '📝',
  info: 'ℹ️',
  success: '✅',
  question: '❓',
  example: '📚'
}

const labels = {
  tip: 'Tip',
  warning: 'Warning',
  danger: 'Danger',
  note: 'Note',
  info: 'Info',
  success: 'Success',
  question: 'Question',
  example: 'Example'
}

const displayTitle = props.title || labels[props.type]
</script>

<template>
  <div
    :class="['callout', `callout-${type}`, { collapsible: collapsible }]"
    role="alert"
    :aria-live="type === 'danger' ? 'assertive' : 'polite'"
  >
    <button
      v-if="collapsible"
      @click="collapsed = !collapsed"
      class="callout-toggle"
      :aria-expanded="!collapsed"
      aria-controls="callout-content"
    >
      <span class="callout-icon" aria-hidden="true">{{ icons[type] }}</span>
      <span class="callout-title">{{ displayTitle }}</span>
      <span class="callout-arrow" :class="{ collapsed }" aria-hidden="true">▼</span>
    </button>
    <div v-else class="callout-header">
      <span class="callout-icon" aria-hidden="true">{{ icons[type] }}</span>
      <span class="callout-title">{{ displayTitle }}</span>
    </div>
    <div
      v-show="!collapsed"
      id="callout-content"
      class="callout-content"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
.callout {
  padding: var(--vp-spacing-4);
  border-radius: var(--vp-radius-md);
  margin: var(--vp-spacing-6) 0;
  border-left: 4px solid;
  background: var(--vp-c-bg-soft);
  box-shadow: var(--vp-shadow-sm);
  transition: all var(--vp-transition-base) var(--vp-ease-out);
}

.callout:hover {
  box-shadow: var(--vp-shadow-md);
}

.callout-header,
.callout-toggle {
  display: flex;
  align-items: center;
  gap: var(--vp-spacing-2);
  margin-bottom: var(--vp-spacing-2);
  font-weight: var(--vp-font-weight-semibold);
  font-size: var(--vp-font-size-sm);
}

.callout-toggle {
  width: 100%;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  text-align: left;
  color: inherit;
  transition: opacity var(--vp-transition-fast) var(--vp-ease-out);
}

.callout-toggle:hover {
  opacity: 0.8;
}

.callout-toggle:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
  border-radius: var(--vp-radius-sm);
}

.callout-icon {
  font-size: var(--vp-font-size-lg);
  flex-shrink: 0;
  line-height: 1;
}

.callout-title {
  flex: 1;
}

.callout-arrow {
  transition: transform var(--vp-transition-base) var(--vp-ease-out);
  font-size: var(--vp-font-size-xs);
  opacity: 0.6;
}

.callout-arrow.collapsed {
  transform: rotate(-90deg);
}

.callout-content {
  font-size: var(--vp-font-size-sm);
  line-height: var(--vp-line-height-relaxed);
  color: var(--vp-c-text-1);
}

.callout-content :deep(p) {
  margin-bottom: var(--vp-spacing-2);
}

.callout-content :deep(p:last-child) {
  margin-bottom: 0;
}

.callout-content :deep(ul),
.callout-content :deep(ol) {
  margin: var(--vp-spacing-2) 0;
  padding-left: var(--vp-spacing-5);
}

.callout-content :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.125rem 0.25rem;
  border-radius: var(--vp-radius-sm);
  font-size: 0.9em;
}

.dark .callout-content :deep(code) {
  background: rgba(255, 255, 255, 0.1);
}

/* Callout Types */
.callout-tip {
  background: var(--vp-c-success-soft);
  border-color: var(--vp-c-success);
  color: var(--vp-c-success-dark);
}

.callout-warning {
  background: var(--vp-c-warning-soft);
  border-color: var(--vp-c-warning);
  color: var(--vp-c-warning-dark);
}

.callout-danger {
  background: var(--vp-c-error-soft);
  border-color: var(--vp-c-error);
  color: var(--vp-c-error-dark);
}

.callout-note {
  background: var(--vp-c-info-soft);
  border-color: var(--vp-c-info);
  color: var(--vp-c-info-dark);
}

.callout-info {
  background: var(--vp-c-info-soft);
  border-color: var(--vp-c-info);
  color: var(--vp-c-info-dark);
}

.callout-success {
  background: var(--vp-c-success-soft);
  border-color: var(--vp-c-success);
  color: var(--vp-c-success-dark);
}

.callout-question {
  background: var(--vp-c-info-soft);
  border-color: var(--vp-c-info);
  color: var(--vp-c-info-dark);
}

.callout-example {
  background: var(--vp-c-bg-soft);
  border-color: var(--vp-c-brand);
  color: var(--vp-c-text-1);
}

/* Dark mode adjustments */
.dark .callout {
  box-shadow: var(--vp-shadow-md);
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .callout {
    padding: var(--vp-spacing-3);
    margin: var(--vp-spacing-4) 0;
  }
  
  .callout-header,
  .callout-toggle {
    font-size: var(--vp-font-size-xs);
  }
  
  .callout-icon {
    font-size: var(--vp-font-size-base);
  }
}
</style>
