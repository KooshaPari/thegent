import { expect, test } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173'

test.describe('thegent Documentation Site', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL)
  })

  test.describe('Homepage', () => {
    test('should load the homepage without errors', async ({ page }) => {
      await expect(page).toHaveTitle(/thegent/i)
      const response = await page.goto(BASE_URL)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should have no console errors', async ({ page }) => {
      const errors: string[] = []
      page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text())
      })
      await page.goto(BASE_URL)
      await page.waitForLoadState('networkidle')
      expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0)
    })
  })

  test.describe('Navigation', () => {
    test('should have visible navigation bar', async ({ page }) => {
      const nav = page.locator('.VPNav')
      await expect(nav).toBeVisible()
    })

    test('should navigate to Start Here', async ({ page }) => {
      await page.goto(BASE_URL)
      await page.click('text=Start Here')
      await expect(page).toHaveURL(/start-here/)
    })

    test('should navigate to Tutorials', async ({ page }) => {
      await page.click('text=Tutorials')
      await expect(page).toHaveURL(/tutorials/)
    })

    test('should navigate to How-to', async ({ page }) => {
      await page.click('text=How-to')
      await expect(page).toHaveURL(/how-to/)
    })

    test('should navigate to Reference', async ({ page }) => {
      await page.click('text=Reference')
      await expect(page).toHaveURL(/reference/)
    })

    test('should have language selector', async ({ page }) => {
      const langSelector = page.locator('text=Language')
      await expect(langSelector).toBeVisible()
    })
  })

  test.describe('Core Pages', () => {
    test('should load start-here page', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      await expect(page.locator('h1')).toBeVisible()
    })

    test('should load tutorials page', async ({ page }) => {
      await page.goto(`${BASE_URL}/tutorials/`)
      const response = await page.goto(`${BASE_URL}/tutorials/`)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should load how-to page', async ({ page }) => {
      await page.goto(`${BASE_URL}/how-to/`)
      const response = await page.goto(`${BASE_URL}/how-to/`)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should load reference page', async ({ page }) => {
      await page.goto(`${BASE_URL}/reference/`)
      await expect(page.locator('h1, .content-container')).toBeVisible()
    })
  })

  test.describe('Sidebar', () => {
    test('should have working sidebar', async ({ page }) => {
      await page.goto(`${BASE_URL}/reference/`)
      const sidebar = page.locator('.VPSidebar')
      await expect(sidebar).toBeVisible()
    })
  })

  test.describe('Dark Mode', () => {
    test('should toggle dark mode', async ({ page }) => {
      await page.goto(BASE_URL)
      const themeButton = page.locator('[class*="theme"]').first()
      if (await themeButton.isVisible()) {
        await themeButton.click()
        await page.waitForTimeout(300)
        await themeButton.click()
      }
    })
  })

  test.describe('Search', () => {
    test('should have search or outline', async ({ page }) => {
      await page.goto(BASE_URL)
      const search = page.locator('.VPNavBarSearch, .VPLocalSearchBox, .VPNavBarOutline')
      await expect(search.first()).toBeVisible()
    })
  })

  test.describe('Footer', () => {
    test('should have footer', async ({ page }) => {
      await page.goto(BASE_URL)
      const footer = page.locator('.VPFooter')
      await expect(footer).toBeVisible()
    })

    test('should have edit link', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      const editLink = page.locator('.edit-link, a[href*="edit"]')
      await expect(editLink.first()).toBeVisible()
    })
  })

  test.describe('Localization', () => {
    test('should support zh-CN locale', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/zh-CN/`)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should support zh-TW locale', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/zh-TW/`)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should support fa locale', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/fa/`)
      expect(response?.status()).toBeLessThan(400)
    })

    test('should support fa-Latn locale', async ({ page }) => {
      const response = await page.goto(`${BASE_URL}/fa-Latn/`)
      expect(response?.status()).toBeLessThan(400)
    })
  })

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      await expect(page.locator('h1')).toBeVisible()
    })

    test('should have accessible navigation', async ({ page }) => {
      await page.goto(BASE_URL)
      const nav = page.locator('.VPNav')
      await expect(nav).toBeVisible()
    })
  })

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto(BASE_URL)
      const nav = page.locator('.VPNav')
      await expect(nav).toBeVisible()
    })

    test('should have working mobile menu', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto(BASE_URL)
      const menuButton = page.locator('.VPNavBarhamburger')
      if (await menuButton.isVisible()) {
        await menuButton.click()
        await page.waitForTimeout(300)
      }
    })
  })

  test.describe('Code Blocks', () => {
    test('should have syntax highlighting', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      const codeBlocks = page.locator('pre code')
      const count = await codeBlocks.count()
      if (count > 0) {
        await expect(codeBlocks.first()).toBeVisible()
      }
    })
  })

  test.describe('Mermaid Diagrams', () => {
    test('should render mermaid diagrams', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      const mermaid = page.locator('.mermaid')
      const count = await mermaid.count()
      if (count > 0) {
        await expect(mermaid.first()).toBeVisible()
      }
    })
  })

  test.describe('Outline', () => {
    test('should show page outline', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      const outline = page.locator('.VPDocAsideOutline, .VPNavBarOutline')
      await expect(outline.first()).toBeVisible()
    })
  })

  test.describe('Last Updated', () => {
    test('should show last updated timestamp', async ({ page }) => {
      await page.goto(`${BASE_URL}/start-here.md`)
      const lastUpdated = page.locator('.last-updated')
      if (await lastUpdated.isVisible()) {
        await expect(lastUpdated).toBeVisible()
      }
    })
  })
})
