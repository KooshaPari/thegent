import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright configuration for VitePress documentation recording.
 * Captures browser interactions, videos, and screenshots for feature demonstrations.
 *
 * Usage:
 *   npx playwright codegen localhost:5173 --output recordings/feature-demo.spec.ts
 *   npx playwright test recordings/feature-demo.spec.ts --headed
 */
export default defineConfig({
  testDir: './recordings',
  fullyParallel: true,
  forbidOnly: process.env.CI ? true : false,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/playwright-results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],

  use: {
    // Base URL for local VitePress development
    baseURL: 'http://localhost:5173',

    // Trace on failure for debugging
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video recording configuration
    video: 'retain-on-failure',

    // Locale and timezone for consistent behavior
    locale: 'en-US',
    timezoneId: 'America/New_York',

    // Viewport size for documentation demos
    viewport: { width: 1280, height: 720 },

    // Accept downloads
    acceptDownloads: true,

    // HTTP authentication (if needed)
    httpCredentials: undefined,

    // Device scale factor for HiDPI captures
    deviceScaleFactor: 1,

    // No ignore HTTPS errors for documentation
    ignoreHTTPSErrors: false,

    // Action timeout for demo interactions
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  webServer: {
    // Use 'bun run docs:dev' for development
    command: 'bun run docs:dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile browsers for responsive demos
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Output directories
  outputDir: 'test-results/output',
  snapshotDir: 'test-results/snapshots',
  snapshotPathTemplate: '{snapshotDir}/{testFileDir}/{testFileName}-{platform}{ext}',
})
