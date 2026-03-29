<script setup lang="ts">
import PhenoDocsTheme from '@phenodocs-theme'

const { Layout } = PhenoDocsTheme
</script>

<template>
  <Layout>
    <template #nav-bar-content-before>
      <StickyHeader>
        <slot name="nav-bar-content-before" />
      </StickyHeader>
    </template>

    <template #sidebar-nav-before>
      <StickySidebar>
        <slot name="sidebar-nav-before" />
      </StickySidebar>
    </template>

    <template #sidebar-nav-after>
      <StickySidebar>
        <slot name="sidebar-nav-after" />
      </StickySidebar>
    </template>

    <template #page-bottom>
      <slot name="page-bottom" />
    </template>

    <!-- Global Components -->
    <ToastContainer />
    <BackToTop />
  </Layout>
</template>

<style scoped>
:deep(.VPNav) {
  position: sticky;
  top: 0;
  z-index: 100;
}

:deep(.VPSidebar) {
  position: sticky;
  top: var(--vp-header-height, 64px);
  max-height: calc(100vh - var(--vp-header-height, 64px));
  overflow-y: auto;
}
</style>
