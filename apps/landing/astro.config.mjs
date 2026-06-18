// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

/**
 * Astro config with i18n wired in for the AT4 baseline.
 *
 *   - defaultLocale: 'en'   (the base dictionary, 100% translated)
 *   - locales: ['en', 'es'] (Spanish, the second locale per the spec)
 *   - routing.prefixDefaultLocale: false  so /en/ routes work but / also
 *     resolves to English (preserves existing /, /qa, /otel, /preview/... links)
 *   - The dir attribute is set per-page in BaseLayout.astro from
 *     src/lib/rtl.ts → isRtl(locale).
 */
export default defineConfig({
  site: 'https://thegent.kooshapari.com',
  base: process.env.GITHUB_PAGES === 'true' ? '/thegent' : '/',
  vite: {
    plugins: [tailwindcss()],
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es'],
    routing: {
      prefixDefaultLocale: false,
      redirectToDefaultLocale: false,
    },
    fallback: {
      es: 'en',
    },
  },
});
