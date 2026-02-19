import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for browser demo recordings
 * Used to generate GIFs for documentation
 */
export default defineConfig({
  testDir: './',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:5173', // VitePress dev server
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on',
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
  ],

  webServer: {
    command: 'npm run docs:dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
