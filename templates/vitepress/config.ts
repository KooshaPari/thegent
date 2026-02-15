import { defineConfig } from 'vitepress'
import { crossProjectLinks } from './plugins/cross-project-links'

export default defineConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  appearance: true,
  lastUpdated: true,

  // Exclude problematic directories from the build
  ignore: [
    'docset/',
    'plans/',
    'research/',
    'docset',
    'plans',
    'research',
  ],

  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,

  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      }
    }
  },

  markdown: {
    config: (md) => {
      md.use(crossProjectLinks)
    }
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Architecture', link: '/ARCHITECTURE_LAYERS.md' },
      { text: 'Guides', link: '/guides/' },
      { text: 'Reference', link: '/reference/' },
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
        },
        {
          text: 'Testing',
          items: [
            { text: 'Cross-Project Links', link: '/cross-links-test.md' },
            { text: 'Callouts', link: '/test-callouts.md' },
          ]
        }
      ],
      '/guides/': [
        {
          text: 'Guides',
          items: [
            { text: 'Overview', link: '/guides/' },
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Overview', link: '/reference/' },
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
})
