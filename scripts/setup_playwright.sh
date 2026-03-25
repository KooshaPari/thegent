#!/usr/bin/env zsh
# Setup Playwright for browser recordings in documentation

set -e

echo "Setting up Playwright for browser recordings..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    echo "Install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if bun is installed (bun includes Node.js)
if ! command -v bun &> /dev/null; then
    echo "Error: bun is required but not installed."
    echo "Install bun from https://bun.sh/"
    exit 1
fi

# Install Playwright if not already installed
if [ ! -d "node_modules/@playwright" ]; then
    echo "Installing Playwright..."
    bun add -d @playwright/test playwright
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
npx playwright install --with-deps

# Create playwright config if it doesn't exist
if [ ! -f "playwright.config.js" ]; then
    cat > playwright.config.js << 'EOF'
// Playwright configuration for documentation browser recordings
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './docs/recordings',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'playwright-report.json' }],
  ],
  use: {
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
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
});
EOF
    echo "Created playwright.config.js"
fi

# Create recordings directory
mkdir -p docs/recordings

echo "✅ Playwright setup complete!"
echo "Run 'npx playwright test' to run browser recordings"
