import { test, expect } from '@playwright/test'

test('VitePress homepage loads and navigates', async ({ page }) => {
  // Navigation to homepage
  await page.goto('/')

  // Verify some content exists
  const heroText = page.locator('h1, h2, .hero-title, .title')
  const count = await heroText.count()
  if (count > 0) {
    await expect(heroText.first()).toBeVisible()
  } else {
    // If no explicit hero, just check if body has content
    await expect(page.locator('body')).not.toBeEmpty()
  }
})
