/**
 * Playwright config for the Astro landing docsite (apps/landing).
 *
 * Boots `astro dev` (or `astro preview` for build-mode tests) and exposes the
 * dev server on the configured port. The a11y suite is the primary consumer;
 * other e2e suites can be added in `testMatch` as the surface grows.
 */

import { defineConfig, devices } from '@playwright/test';

const PORT = Number(process.env.PLAYWRIGHT_PORT ?? 4321);

export default defineConfig({
  testDir: './e2e',
  testMatch: ['**/a11y/**/*.spec.ts'],
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? `http://localhost:${PORT}`,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: process.env.A11Y_USE_PREVIEW
      ? 'bun run preview'
      : 'bun run dev -- --port ' + PORT,
    url: `http://localhost:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
