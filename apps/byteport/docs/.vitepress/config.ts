import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Byteport',
  description: 'Cloud deployment platform — deploy anything, anywhere, for free',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Providers', link: '/providers/vercel' },
      { text: 'API Reference', link: '/api/overview' },
    ],
    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Architecture', link: '/guide/architecture' },
          ],
        },
      ],
      '/providers/': [
        {
          text: 'Providers',
          items: [
            { text: 'Vercel', link: '/providers/vercel' },
            { text: 'Netlify', link: '/providers/netlify' },
            { text: 'Railway', link: '/providers/railway' },
            { text: 'Fly.io', link: '/providers/flyio' },
            { text: 'Supabase', link: '/providers/supabase' },
          ],
        },
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/KooshaPari/byteport' },
    ],
  },
})
