import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  appearance: true,
  lastUpdated: true,

  srcDir: 'docs',

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Architecture', link: '/ARCHITECTURE_LAYERS.md' },
      { text: 'Guides', link: '/docs/guides/' },
      { text: 'Reference', link: '/docs/reference/' },
    ],

    sidebar: {
      '/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/' },
          ]
        },
        {
          text: 'Architecture',
          items: [
            { text: 'Layers', link: '/ARCHITECTURE_LAYERS.md' },
            { text: 'Orchestration', link: '/ORCHESTRATION.md' },
          ]
        }
      ],
      '/docs/guides/': [
        {
          text: 'Guides',
          items: [
            { text: 'Overview', link: '/docs/guides/' },
          ]
        }
      ]
    },

    socialLinks: [],
    search: { provider: 'local' },
    outline: 'deep',
  },

  build: {
    outDir: '../docs-dist',
    assetsDir: 'assets',
  },

  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      }
    }
  }
})
