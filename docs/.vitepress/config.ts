import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { OramaPlugin } from '@orama/plugin-vitepress'
import { imagetools } from 'vite-imagetools'
import { crossProjectLinks } from './plugins/cross-project-links'
import { contentTabsPlugin } from './plugins/content-tabs'
import { sidebar } from './sidebar'

const config = defineConfig({
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
    plugins: [
      OramaPlugin({
        // Orama search plugin configuration
        // Automatically indexes all markdown content
        // Supports full-text search with typo tolerance
        // OSS, self-hosted, no external services required
      }),
      imagetools({
        // Image optimization: WebP/AVIF conversion, lazy loading
        // Usage: ![Image](./image.jpg?format=webp&w=800)
        defaultDirectives: (url) => {
          if (url.searchParams.has('format')) {
            return new URLSearchParams({
              format: url.searchParams.get('format') || 'webp',
            })
          }
          return new URLSearchParams()
        }
      })
    ],
    build: {
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
              if (id.includes('@orama')) {
                return 'orama'
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
      
      // Math support (KaTeX)
      md.use(require('markdown-it-katex'), {
        throwOnError: false,
        errorColor: '#cc0000'
      })
      
      // Emoji support
      md.use(require('markdown-it-emoji'), {
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
    search: {
      provider: 'orama',
      options: {
        // Orama search configuration
        // Indexes all markdown content automatically
        // Supports full-text, vector, and hybrid search
      }
    },
    outline: 'deep',

    editLink: {
      pattern: 'https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },
  },

  build: {
    outDir: '../docs-dist',
    assetsDir: 'assets',
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
