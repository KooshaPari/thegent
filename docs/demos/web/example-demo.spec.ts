import { test, expect } from '@playwright/test';

/**
 * Example Playwright test for generating demo GIFs
 * Run with: npx playwright test --gif
 */
test('thegent documentation demo', async ({ page }) => {
  // Navigate to docs
  await page.goto('/');

  // Wait for page to load
  await page.waitForLoadState('networkidle');

  // Example: Click on a navigation item
  const navLink = page.locator('nav a').first();
  if (await navLink.isVisible()) {
    await navLink.click();
    await page.waitForLoadState('networkidle');
  }

  // Example: Search
  const searchButton = page.locator('button[aria-label="Search"]');
  if (await searchButton.isVisible()) {
    await searchButton.click();
    await page.fill('input[type="search"]', 'agent');
    await page.waitForTimeout(500); // Show search results
  }

  // Take screenshot for GIF
  await page.screenshot({ path: 'demo-screenshot.png', fullPage: true });
});
