// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://thegent.kooshapari.com',
  base: process.env.GITHUB_PAGES === 'true' ? '/thegent' : '/',
  vite: {
    plugins: [tailwindcss()],
  },
});
