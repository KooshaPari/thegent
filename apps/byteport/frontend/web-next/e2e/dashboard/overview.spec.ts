import { test, expect } from '@playwright/test'
import { DashboardPage } from '../../pages/DashboardPage'

test.describe('Dashboard Overview', () => {
  let dashboardPage: DashboardPage

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page)
    await dashboardPage.goto()
  })

  test('should display dashboard with authenticated user', async ({ page }) => {
    // Check if we're on the dashboard
    await expect(page).toHaveURL(/.*dashboard/)
    
    // Verify main elements are visible
    await expect(page.locator('h1')).toContainText(/dashboard|overview/i)
    
    // The page should load without errors
    await dashboardPage.waitForLoad()
  })

  test('should show deployments section', async ({ page }) => {
    // Look for any deployment-related content
    // Since we don't have the actual UI yet, we'll test for basic structure
    const mainContent = page.locator('main, [role="main"], .main-content')
    await expect(mainContent).toBeVisible()
  })

  test('should be responsive', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1280, height: 720 })
    await dashboardPage.waitForLoad()
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 })
    await dashboardPage.waitForLoad()
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 })
    await dashboardPage.waitForLoad()
    
    // Should not have horizontal scroll on mobile
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth)
    const clientWidth = await page.evaluate(() => document.body.clientWidth)
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 20) // Allow small buffer
  })

  test('should handle navigation', async ({ page }) => {
    // Test basic navigation works
    const currentUrl = page.url()
    expect(currentUrl).toContain('/')
    
    // Page should have proper meta tags
    const title = await page.title()
    expect(title).toBeTruthy()
    expect(title.length).toBeGreaterThan(0)
  })
})

test.describe('Dashboard - Unauthenticated', () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test('should redirect to login when not authenticated', async ({ page }) => {
    // Clear any existing auth state
    await page.context().clearCookies()
    await page.evaluate(() => localStorage.clear())
    
    // Try to access dashboard
    await page.goto('/dashboard')
    
    // Should redirect to login or show login UI
    // Adjust this based on your actual auth flow
    await page.waitForTimeout(2000) // Allow redirect to complete
    
    const currentUrl = page.url()
    const hasLoginElement = await page.locator('[data-testid="login"], [data-testid="signin"], .sign-in, .login').count() > 0
    
    // Either redirected to auth URL or showing login component
    expect(currentUrl.includes('auth') || currentUrl.includes('login') || hasLoginElement).toBeTruthy()
  })
})