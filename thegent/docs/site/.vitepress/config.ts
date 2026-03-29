import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'thegent',
  description: 'AI agent orchestration and governance platform',
  outDir: '../public',
  ignoreDeadLinks: false,
  lastUpdated: true,

  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/' },
      { text: 'Operations', link: '/operations/' },
      { text: 'Reference', link: '/reference/' },
      { text: 'API', link: '/api/' },
      { text: 'GitHub', link: 'https://github.com/kooshapari/thegent' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/guide/' },
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'CLI Reference', link: '/guide/cli-reference' },
            { text: 'Providers', link: '/guide/providers' },
            { text: 'Architecture', link: '/guide/architecture' },
            { text: 'Governance', link: '/guide/governance' },
          ],
        },
      ],
      '/operations/': [
        {
          text: 'Operations',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/operations/' },
            { text: 'Troubleshooting', link: '/operations/troubleshooting' },
            { text: 'Runbooks', link: '/operations/runbooks' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/reference/' },
            { text: 'Routing', link: '/reference/routing' },
            { text: 'Configuration', link: '/reference/configuration' },
          ],
        },
      ],
      '/api/': [
        {
          text: 'API',
          collapsed: false,
          items: [{ text: 'API Index', link: '/api/' }],
        },
      ],
    },

    search: {
      provider: 'local',
    },

    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Back to top',

    socialLinks: [
      { icon: 'github', link: 'https://github.com/kooshapari/thegent' },
    ],

    editLink: {
      pattern: 'https://github.com/kooshapari/thegent/edit/main/docs/site/:path',
      text: 'Edit this page on GitHub',
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present thegent contributors',
    },
  },
})
