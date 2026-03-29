---
layout: home

hero:
  name: "{{PROJECT_NAME}}"
  text: "{{PROJECT_TAGLINE}}"
  tagline: "{{PROJECT_DESCRIPTION}}"
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/your-org/{{PROJECT_NAME}}

features:
  - title: Fast
    details: Built for speed with VitePress's blazing fast development experience.
  - title: Customizable
    details: Extend with custom themes, components, and plugins.
  - title: Documentation First
    details: Beautiful, searchable documentation out of the box.

---

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('Welcome to {{PROJECT_NAME}} documentation!')
})
</script>

## Quick Links

- [Installation Guide](/guide/installation)
- [API Reference](/api/overview)
- [Examples](/examples)

<Callout type="tip" title="Pro Tip">
  Use the search feature (Cmd/Ctrl + K) to quickly find what you're looking for!
</Callout>
