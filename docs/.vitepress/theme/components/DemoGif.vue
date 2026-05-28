<script setup lang="ts">
withDefaults(
  defineProps<{
    src: string
    alt?: string
    caption?: string
  }>(),
  {
    alt: '',
    caption: '',
  },
)
</script>

<template>
  <figure class="demo-gif">
    <img :src="src" :alt="alt" loading="lazy" />
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.demo-gif {
  margin: 1rem 0;
}

.demo-gif img {
  display: block;
  max-width: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--vp-c-divider);
}

.demo-gif figcaption {
  margin-top: 0.5rem;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}
</style>
