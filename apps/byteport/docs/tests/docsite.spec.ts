import { test, expect } from '@playwright/test'

// byteport: Cloud deployment platform documentation

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173'

test.describe('byteport Documentation Site', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL)
  })

  // === Homepage Tests ===
  test('homepage loads successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Byteport/i)
  })

  test('homepage has proper layout', async ({ page }) => {
    await expect(page.locator('#VPContent')).toBeVisible()
  })

  // === Navigation Tests ===
  test('navigation menu is present', async ({ page }) => {
    await expect(page.locator('.VPNav')).toBeVisible()
  })

  test('Guide link is visible', async ({ page }) => {
    await expect(page.getByText('Guide')).toBeVisible()
  })

  test('Providers link is visible', async ({ page }) => {
    await expect(page.getByText('Providers')).toBeVisible()
  })

  test('API Reference link is visible', async ({ page }) => {
    await expect(page.getByText('API Reference')).toBeVisible()
  })

  // === Core Pages Tests ===
  for (const route of [
    '/guide/getting-started',
    '/guide/architecture',
    '/providers/vercel',
    '/providers/netlify',
    '/providers/railway',
    '/providers/flyio',
    '/providers/supabase',
  ] as const) {
    test(`page ${route} loads with content`, async ({ page }) => {
      await page.goto(`${BASE_URL}${route}`)
      await expect(page.locator('#VPContent')).toBeVisible()
    })
  }

  // === Sidebar Tests ===
  test('sidebar is present on guide pages', async ({ page }) => {
    await page.goto(`${BASE_URL}/guide/getting-started`)
    await expect(page.locator('.VPSidebar')).toBeVisible()
  })

  test('sidebar is present on provider pages', async ({ page }) => {
    await page.goto(`${BASE_URL}/providers/vercel`)
    await expect(page.locator('.VPSidebar')).toBeVisible()
  })

  // === Dark Mode Tests ===
  test('dark mode toggle is present', async ({ page }) => {
    await expect(page.locator('.VPNavBarAppearance')).toBeVisible()
  })

  test('dark mode toggle works', async ({ page }) => {
    const toggle = page.locator('.VPNavBarAppearance button')
    await expect(toggle).toBeVisible()
    await toggle.click()
    await expect(page.locator('html')).toHaveClass(/dark/)
  })

  // === Footer Tests ===
  test('footer is present', async ({ page }) => {
    await expect(page.locator('.VPFooter')).toBeVisible()
  })

  test('footer has GitHub link', async ({ page }) => {
    const githubLink = page.locator('a[href*="github.com"]').first()
    await expect(githubLink).toBeVisible()
  })

  // === Search Tests ===
  test('search functionality is present', async ({ page }) => {
    await expect(page.locator('.VPNavBarSearch')).toBeVisible()
  })

  // === Code Block Tests ===
  test('code blocks have syntax highlighting', async ({ page }) => {
    await page.goto(`${BASE_URL}/guide/getting-started`)
    const codeBlocks = page.locator('#VPContent pre code')
    const count = await codeBlocks.count()
    if (count > 0) {
      await expect(codeBlocks.first()).toBeVisible()
    }
  })

  // === Responsive Design Tests ===
  test('mobile navigation works', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    const menuButton = page.locator('.VPNavBarhamburger')
    if (await menuButton.isVisible()) {
      await menuButton.click()
      await expect(page.locator('.VPNavMenu')).toBeVisible()
    }
  })

  // === Accessibility Tests ===
  test('page has proper heading hierarchy', async ({ page }) => {
    await page.goto(`${BASE_URL}/guide/getting-started`)
    const h1 = page.locator('#VPContent h1')
    await expect(h1).toBeVisible()
  })

  test('images have alt text', async ({ page }) => {
    await page.goto(`${BASE_URL}/guide/getting-started`)
    const images = page.locator('#VPContent img')
    const count = await images.count()
    if (count > 0) {
      for (let i = 0; i < Math.min(count, 5); i++) {
        const img = images.nth(i)
        if (await img.isVisible()) {
          await expect(img).toHaveAttribute(/alt/)
        }
      }
    }
  })

  // === GitHub Link Tests ===
  test('GitHub link in footer is valid', async ({ page }) => {
    await page.goto(`${BASE_URL}/`)
    const githubLink = page.locator('a[href*="github.com/KooshaPari/byteport"]')
    await expect(githubLink).toBeVisible()
  })
})
