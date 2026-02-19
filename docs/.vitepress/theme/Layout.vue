<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import { useData } from 'vitepress'
import StickyHeader from './components/StickyHeader.vue'
import StickySidebar from './components/StickySidebar.vue'
import ToastContainer from './components/ToastContainer.vue'
import BackToTop from './components/BackToTop.vue'
import './custom.css'

const { Layout } = DefaultTheme
const { frontmatter, page } = useData()
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
