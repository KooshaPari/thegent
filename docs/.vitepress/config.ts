import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { withMermaid } from 'vitepress-plugin-mermaid'
import { imagetools } from 'vite-imagetools'
import { crossProjectLinks } from './plugins/cross-project-links'
import { contentTabsPlugin } from './plugins/content-tabs'
import { videoEmbedPlugin } from './plugins/video-embed'
import { sidebar } from './sidebar-canonical'
import { createRequire } from 'module'
import { createPhenotypeConfig } from '@phenotype/docs/config'

const docsDir = dirname(fileURLToPath(import.meta.url))

const require = createRequire(import.meta.url)
const markdownItEmoji = require('markdown-it-emoji').full
const katex = require('markdown-it-mathjax3')
const algoliaAppId = process.env.VITEPRESS_ALGOLIA_APP_ID
const algoliaApiKey = process.env.VITEPRESS_ALGOLIA_API_KEY
const algoliaIndexName = process.env.VITEPRESS_ALGOLIA_INDEX_NAME
const hasAlgolia = Boolean(algoliaAppId && algoliaApiKey && algoliaIndexName)

// Hardcode to /thegent/ for GitHub Pages deployment
const docsBase = '/thegent/'

// Supported locales: en, zh-CN, zh-TW, fa, fa-Latn
const locales = {
  root: { label: "English", lang: "en", title: 'thegent', description: 'AI Agent Governance & MCP Server' },
  "zh-CN": { label: "简体中文", lang: "zh-CN", title: 'thegent', description: 'AI 代理治理和 MCP 服务器' },
  "zh-TW": { label: "繁體中文", lang: "zh-TW", title: 'thegent', description: 'AI 代理治理和 MCP 伺服器' },
  fa: { label: "فارسی", lang: "fa", title: 'thegent', description: 'حکمرانی عامل هوش مصنوعی و سرور MCP' },
  "fa-Latn": { label: "Pinglish", lang: "fa-Latn", title: 'thegent', description: 'AI Agent Governance (Latin)' }
}

const config = createPhenotypeConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  base: docsBase,
  srcDir: '.',
  githubOrg: 'KooshaPari',
  githubRepo: 'thegent',

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
      text: "\uD83C\uDF10 Language",
      items: [
        { text: "English", link: "/" },
        { text: "\u7B80\u4F53\u4E2D\u6587", link: "/zh-CN/" },
        { text: "\u7E41\u9AD4\u4E2D\u6587", link: "/zh-TW/" },
        { text: "\u0641\u0627\u0631\u0633\u06CC", link: "/fa/" },
        { text: "Pinglish", link: "/fa-Latn/" }
      ]
    }
  ],

  sidebar: sidebar,

  overrides: {
    locales,
    appearance: true,

    // Exclude problematic directories from the build
    // IMPORTANT: Keep aggressive to avoid build timeouts (7800+ md files total)
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

    vite: {
      plugins: [
        imagetools({
          defaultDirectives: (url: URL) => {
            if (url.searchParams.has('format')) {
              return new URLSearchParams({
                format: url.searchParams.get('format') || 'avif',
                as: 'picture',
              })
            }
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
            manualChunks: (id: string) => {
              if (id.includes('node_modules')) {
                return 'vendor'
              }
            }
          }
        }
      }
    },

    markdown: {
      config: (md: any) => {
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

        // Emoji support
        md.use(markdownItEmoji)
      },
      math: true,
    },

    themeConfig: {
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
    },

    // Mermaid configuration
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
  },
})

export default withMermaid(config)
