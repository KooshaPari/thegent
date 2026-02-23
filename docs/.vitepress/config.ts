import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { imagetools } from 'vite-imagetools'
import { crossProjectLinks } from './plugins/cross-project-links'
import { contentTabsPlugin } from './plugins/content-tabs'
import { videoEmbedPlugin } from './plugins/video-embed'
import { sidebar } from './sidebar-canonical'
import { createRequire } from 'module'

const require = createRequire(import.meta.url)
const markdownItKatex = require('markdown-it-katex')
const markdownItEmoji = require('markdown-it-emoji').full
const algoliaAppId = process.env.VITEPRESS_ALGOLIA_APP_ID
const algoliaApiKey = process.env.VITEPRESS_ALGOLIA_API_KEY
const algoliaIndexName = process.env.VITEPRESS_ALGOLIA_INDEX_NAME
const hasAlgolia = Boolean(algoliaAppId && algoliaApiKey && algoliaIndexName)
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'thegent'
const isPagesBuild = process.env.GITHUB_ACTIONS === 'true' || process.env.GITHUB_PAGES === 'true'
const docsBaseOverride = process.env.VITEPRESS_BASE
// Hardcode to /thegent/ for GitHub Pages deployment
const docsBase = '/thegent/'
const faviconHref = `${docsBase}favicon.ico`

// Supported locales: en, zh-CN, zh-TW, fa, fa-Latn
const locales = {
  root: { label: "English", lang: "en", title: 'thegent', description: 'AI Agent Governance & MCP Server' },
  "zh-CN": { label: "简体中文", lang: "zh-CN", title: 'thegent', description: 'AI 代理治理和 MCP 服务器' },
  "zh-TW": { label: "繁體中文", lang: "zh-TW", title: 'thegent', description: 'AI 代理治理和 MCP 伺服器' },
  fa: { label: "فارسی", lang: "fa", title: 'thegent', description: 'حکمرانی عامل هوش مصنوعی و سرور MCP' },
  "fa-Latn": { label: "Pinglish", lang: "fa-Latn", title: 'thegent', description: 'AI Agent Governance (Latin)' }
}

const config = defineConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  base: docsBase,
  locales,
  head: [
    ['link', { rel: 'icon', href: faviconHref }],
  ],
  appearance: true,
  lastUpdated: true,

  // Exclude problematic directories from the build
  srcExclude: [
    'docset/**',
    'fragemented/**',
    'plans/**',
    'research/**',
    'reports/**',
    'reference/api/**',
    'reference/WORK_STREAM.md',
    'context/**',
    'contracts/TEST_HEALTH_DASHBOARD.md',
  ],

  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,

  vite: {
    plugins: [
      // VitePress bundles its own vite; cast required to resolve dual-vite Plugin type mismatch
      imagetools({
        defaultDirectives: (url) => {
          // Image optimization: WebP/AVIF conversion, lazy loading handled by browser
          if (url.searchParams.has('format')) {
            return new URLSearchParams({
              format: url.searchParams.get('format') || 'avif',
              as: 'picture',
            })
          }
          // Default to AVIF with WebP fallback for better compression
          return new URLSearchParams({
            format: 'avif',
            as: 'picture',
          })
        }
      }) as any
    ],
    build: {
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Keep chunking simple to avoid mermaid/vue circular init ordering bugs.
            if (id.includes('node_modules')) {
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

      // Emoji support - use defaults to avoid undefined rendering in tables
      md.use(markdownItEmoji)
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
        text: 'Start Here',
        link: '/start-here.md'
      },
      {
        text: 'Tutorials',
        link: '/tutorials/'
      },
      {
        text: 'How-to',
        link: '/how-to/'
      },
      {
        text: 'Reference',
        link: '/reference/',
        activeMatch: '/reference/'
      },
      {
        text: 'Explanation',
        link: '/explanation/'
      },
      {
        text: 'Operations',
        link: '/operations/'
      },
      {
        text: 'API',
        link: '/api/'
      },
      {
        text: "🌐 Language",
        items: [
          { text: "English", link: "/" },
          { text: "简体中文", link: "/zh-CN/" },
          { text: "繁體中文", link: "/zh-TW/" },
          { text: "فارسی", link: "/fa/" },
          { text: "Pinglish", link: "/fa-Latn/" }
        ]
      }
    ],

    sidebar: sidebar,

    socialLinks: [],
    search: hasAlgolia
      ? {
          provider: 'algolia',
          options: {
            appId: algoliaAppId as string,
            apiKey: algoliaApiKey as string,
            indexName: algoliaIndexName as string,
          },
        }
      : undefined,
    outline: 'deep',

    editLink: {
      pattern: 'https://github.com/kooshapari/temp-PRODVERCEL/485/kush/thegent/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },
  },

  // Mermaid configuration
  // Note: Mermaid doesn't support CSS variables - use actual color values
  mermaid: {
    theme: 'base',
    themeVariables: {
      primaryColor: '#42b883',
      background: '#ffffff',
      primaryTextColor: '#213547',
      primaryBorderColor: '#e0e0e0',
      lineColor: '#666666',
      secondaryColor: '#747bff',
      tertiaryColor: '#f5f5f5',
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
