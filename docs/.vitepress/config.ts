import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { imagetools } from 'vite-imagetools'
import { crossProjectLinks } from './plugins/cross-project-links'
import { contentTabsPlugin } from './plugins/content-tabs'
import { imageOptimizationPlugin } from './plugins/image-optimization'
import { videoEmbedPlugin } from './plugins/video-embed'
import { sidebar } from './sidebar-canonical'
import { createRequire } from 'module'

const docsDir = dirname(fileURLToPath(import.meta.url))

const require = createRequire(import.meta.url)
const markdownItEmoji = require('markdown-it-emoji').full
const katex = require('markdown-it-mathjax3')
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
  // IMPORTANT: Keep aggressive to avoid build timeouts (7800+ md files total)
  // Only include: index.md, start-here.md, tutorials/, how-to/, reference/, operations/, api/
  srcExclude: [
    // Research/context dumps (566MB+)
    'context/**',
    'diagrams/**',
    'dumps/**',
    'docset/**',
    // Fragmented/in-progress content
    'fragemented/**',
    'plans/**',
    'research/**',
    'reports/**',
    'changes/**',
    'specs/**',
    // Auto-generated API docs (691 files)
    'reference/api/**',
    'reference/WORK_STREAM.md',
    // Archives and legacy
    'archives/**',
    'contracts/**',
    'migration/**',
    'closure/**',
    // Large generated sections
    'governance/**',
    'architecture/**',
    'guides/**',
    'checklists/**',
    'examples/**',
    'security/**',
    'deployment/**',
    'tasks/**',
    'demos/**',
    'concepts/**',
    'projects/**',
    'recordings/**',
    'references/**',
    'site/**',
    // Root-level large files
    'AGENT_*.md',
    'AUDIT_*.md',
    'CROSS_*.md',
    'DISCOVERY.md',
    'DOCUMENT_*.md',
    'FASTMCP_*.md',
    'GAP_*.md',
    'GOVERNANCE_*.md',
    'IMPLEMENTATION_*.md',
    'INSTALL_*.md',
    'LLM_*.md',
    'MAINTENANCE_*.md',
    'MISE_*.md',
    'MONITORING_*.md',
    'MULTI_*.md',
    'NATS_*.md',
    'NEO4J_*.md',
    'NAVIGATION_*.md',
    'NEXT_*.md',
    'ORCHESTRATION_*.md',
    'PATCHES_*.md',
    'PLANNING_*.md',
    'POST_*.md',
    'PYTHON_*.md',
    'QUALITY_*.md',
    'RESUME_*.md',
    'RUNBOOK.md',
    'SETUP-*.md',
    'SHELL_*.md',
    'SPECS_*.md',
    'STATE_*.md',
    'ULTRA_*.md',
    'VERIFICATION_*.md',
    'WHAT_*.md',
    'WORK_*.md',
    'ZSH_*.md',
  ],

  // Disable dead link check (links are external or cross-project)
  ignoreDeadLinks: true,

  vite: {
    resolve: {
      alias: {
      },
    },
    server: {
      fs: {
        allow: [],
      },
    },
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
      md.use(katex, {
        throwOnError: false,
        errorColor: '#cc0000'
      })

      md.use(imageOptimizationPlugin)
      // Emoji support - use defaults to avoid undefined rendering in tables
      md.use(markdownItEmoji)
    },
    // Enable line numbers for code blocks
    math: true,
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
