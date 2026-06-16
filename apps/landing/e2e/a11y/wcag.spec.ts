/**
 * Astro landing docsite axe scan.
 *
 * This test runs INSIDE apps/landing and is invoked by the a11y-thegent.yml
 * workflow's `app_dir: apps/landing` matrix entry. It walks all .astro pages
 * under src/pages/ via import.meta.glob and runs an axe scan against each
 * when the dev server is running on http://localhost:4321.
 */

import { test, expect } from '@playwright/test';
import { buildAxeBuilder, isFailingImpact } from '../axe-config';

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:4321';

// Eagerly enumerate every Astro page at build time so we don't miss a new
// route when pages are added. import.meta.glob uses Vite's globbing; the
// `{ eager: true }` mode returns the modules but we only need the *keys* (the
// paths) so we wrap with `.keys()`.
const pageModules = import.meta.glob<true, string, unknown>('../src/pages/**/*.astro');
const pagePaths = Object.keys(pageModules)
  // Strip the leading '../src/pages' and trailing '.astro' to get a route.
  .map((p) => p.replace(/^\.\.\/src\/pages/, '').replace(/\.astro$/, ''))
  // Filter out dynamic routes ([param]) — those need a server fixture.
  .filter((p) => !p.includes('['))
  // Root index.astro -> '/'  (the 'index' segment collapses).
  .map((p) => (p === '/index' ? '/' : p));

test.describe('AT1 — Astro landing docsite WCAG scan', () => {
  for (const route of pagePaths) {
    test(`landing${route} has no critical/serious violations`, async ({ page }) => {
      const url = `${BASE_URL}${route}`.replace(/\/+$/, '/');
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.evaluate(() => document.fonts.ready);

      const results = await buildAxeBuilder(page).analyze();
      const failing = results.violations.filter((v) =>
        isFailingImpact(v.impact),
      );

      if (failing.length > 0) {
        // eslint-disable-next-line no-console
        console.log(
          `[landing${route}] failing axe violations:\n` +
            failing
              .map(
                (v) =>
                  `  - ${v.id} [${v.impact}] ${v.help} ` +
                  `(helpUrl: ${v.helpUrl})`,
              )
              .join('\n'),
        );
      }

      expect(failing).toEqual([]);
    });
  }
});
