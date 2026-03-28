import { defineConfig } from 'vitepress';
import { createSiteMeta } from './site-meta.mjs';

const siteMeta = createSiteMeta();

export default defineConfig({
  title: 'phenotype-config',
  description: 'Configuration crate for phenotype projects',
  lang: 'en-US',
  srcDir: '.',
  outDir: '../.vitepress-dist',
  head: [['meta', { name: 'theme-color', content: '#334155' }]],
  themeConfig: {
    nav: [
      { text: 'Home', link: siteMeta.locales.root },
      { text: 'Tests', link: '/tests' },
    ],
    sidebar: [
      { text: 'Start', items: [{ text: 'Docs', link: '/' }] },
      {
        text: 'Reference',
        items: [{ text: 'Tests', link: '/tests' }],
      },
    ],
    socialLinks: [],
  },
});
