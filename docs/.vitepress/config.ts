import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { imagetools } from 'vite-imagetools'
import { crossProjectLinks } from './plugins/cross-project-links'
import { contentTabsPlugin } from './plugins/content-tabs'
import { videoEmbedPlugin } from './plugins/video-embed'
import { sidebar } from './sidebar'
import { createRequire } from 'module'

const require = createRequire(import.meta.url)
const markdownItKatex = require('markdown-it-katex')
const markdownItEmoji = require('markdown-it-emoji').full
const algoliaAppId = process.env.VITEPRESS_ALGOLIA_APP_ID
const algoliaApiKey = process.env.VITEPRESS_ALGOLIA_API_KEY
const algoliaIndexName = process.env.VITEPRESS_ALGOLIA_INDEX_NAME
const hasAlgolia = Boolean(algoliaAppId && algoliaApiKey && algoliaIndexName)

const config = defineConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  base: '/thegent/',
  appearance: true,
  lastUpdated: true,

  // Exclude problematic directories from the build
  srcExclude: [
    'docset/**',
    'plans/**',
    'research/**',
    'reference/api/**',
  ],

  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,

  vite: {
    plugins: [
      // VitePress bundles its own vite; cast required to resolve dual-vite Plugin type mismatch
      imagetools({
        defaultDirectives: (url) => {
          if (url.searchParams.has('format')) {
            return new URLSearchParams({
              format: url.searchParams.get('format') || 'webp',
            })
          }
          return new URLSearchParams()
        }
      }) as any
    ],
    build: {
      outDir: '../docs-dist',
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Optimize code splitting for faster loads
            if (id.includes('node_modules')) {
              // Split large vendor chunks
              if (id.includes('mermaid')) {
                return 'mermaid'
              }
              if (id.includes('vue')) {
                return 'vue'
              }
              if (id.includes('markdown-it')) {
                return 'markdown'
              }
              return 'vendor'
            }
          }
        }
      }
    }
  },

  markdown: {
    config: (md) => {
      md.use(crossProjectLinks)
      md.use(contentTabsPlugin)
      md.use(videoEmbedPlugin, {
        controls: true,
        width: '100%',
      })

      // Math support (KaTeX)
      md.use(markdownItKatex, {
        throwOnError: false,
        errorColor: '#cc0000'
      })

      // Emoji support
      md.use(markdownItEmoji, {
        shortcuts: {},
        defs: {}
      })
    },
    // Enable line numbers for code blocks
    lineNumbers: true,
    // Enable code highlighting
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { 
        text: 'Architecture', 
        link: '/ARCHITECTURE_LAYERS.md',
        activeMatch: '/architecture/'
      },
      { 
        text: 'Guides', 
        link: '/guides/',
        activeMatch: '/guides/'
      },
      { 
        text: 'Reference', 
        link: '/reference/',
        activeMatch: '/reference/'
      },
    ],

    sidebar: sidebar,

    socialLinks: [],
    search: hasAlgolia
      ? {
          provider: 'algolia',
          options: {
            appId: algoliaAppId,
            apiKey: algoliaApiKey,
            indexName: algoliaIndexName,
          },
        }
      : { provider: 'local' },
    outline: 'deep',

    editLink: {
      pattern: 'https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },
  },

  // Mermaid configuration
  mermaid: {
    theme: 'base',
    themeVariables: {
      primaryColor: '#42b883',
      background: 'var(--vp-c-bg)',
      primaryTextColor: 'var(--vp-c-text-1)',
      primaryBorderColor: 'var(--vp-c-divider)',
      lineColor: 'var(--vp-c-text-2)',
      secondaryColor: 'var(--vp-c-brand-light)',
      tertiaryColor: 'var(--vp-c-bg-soft)',
    },
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
    },
    sequence: {
      useMaxWidth: true,
    },
    gantt: {
      useMaxWidth: true,
    },
  },

})

export default withMermaid(config)
