import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
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
          autogenerate: { directory: 'projects' },
        },
        {
          label: 'Services',
          autogenerate: { directory: 'services' },
        },
        {
          label: 'Governance',
          autogenerate: { directory: 'governance' },
        },
      ],
      customCss: ['./src/styles/custom.css'],
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
