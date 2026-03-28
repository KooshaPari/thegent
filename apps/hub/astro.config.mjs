import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://phenotype.dev',
  integrations: [
    starlight({
      title: 'Phenotype',
      description: 'The Phenotype ecosystem hub — all projects, docs, and services in one place.',
      social: {
        github: 'https://github.com/KooshaPari',
      },
      sidebar: [
        {
          label: 'Projects',
          items: [
            { label: 'Overview', link: '/projects/' },
            { label: 'heliosCLI', link: '/projects/helios-cli/' },
            { label: 'heliosApp', link: '/projects/helios-app/' },
            { label: 'AgilePlus', link: '/projects/agileplus/' },
            { label: 'cliproxyapi', link: '/projects/cliproxy/' },
            { label: 'agent-wave', link: '/projects/agent-wave/' },
            { label: 'phenotype-gauge', link: '/projects/gauge/' },
          ],
        },
        {
          label: 'Services',
          items: [
            { label: 'Service Registry', link: '/services/' },
            { label: 'Port Allocation', link: '/services/ports/' },
          ],
        },
        {
          label: 'Governance',
          items: [
            { label: 'Architecture Decisions', link: '/governance/adrs/' },
            { label: 'Standards', link: '/governance/standards/' },
          ],
        },
      ],
      customCss: ['./src/styles/custom.css'],
      head: [
        { tag: 'meta', attrs: { property: 'og:type', content: 'website' } },
        { tag: 'meta', attrs: { property: 'og:site_name', content: 'Phenotype Ecosystem' } },
      ],
    }),
    react(),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  server: {
    port: 9000,
  },
});
