import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  webServer: {
    command: 'npm run docs:build && npm run docs:dev',
    port: 4191,
    reuseExistingServer: !process.env.CI,
  },
});
