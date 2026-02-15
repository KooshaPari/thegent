import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'thegent',
  description: 'AI Agent Governance & MCP Server',
  appearance: true,
  lastUpdated: true,
  srcDir: '.',
  outDir: '../docs-dist/',
  srcExclude: [
    'plans/**',
    'reference/**',
    'reports/**',
    'research/**',
    'changes/**',
    'governance/**',
    'enterprise/**',
    'guides/**',
    'docset/**',
    'closure/**',
    'sessions/**',
    'contracts/**',
  ],
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
    ],
    sidebar: [],
    socialLinks: [],
    search: { provider: 'local' },
  },
})
