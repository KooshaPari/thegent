import { test, expect } from '@playwright/test'

// @trace FR-DOC-001
test.describe('thegent docsite', () => {
  test('homepage loads with hero title', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/thegent/)
    await expect(page.locator('.VPHero .name')).toContainText('thegent')
  })

  test('homepage Get Started action link navigates to guide', async ({ page }) => {
    await page.goto('/')
    const getStarted = page.locator('.VPHero .VPButton', { hasText: 'Get Started' })
    await expect(getStarted).toBeVisible()
    await getStarted.click()
    await expect(page).toHaveURL(/guide\//)
  })

  test('guide sidebar renders core pages', async ({ page }) => {
    await page.goto('/guide/getting-started')
    const sidebar = page.locator('.VPSidebar')
    await expect(sidebar).toBeVisible()
    await expect(sidebar.locator('text=Getting Started')).toBeVisible()
    await expect(sidebar.locator('text=CLI Reference')).toBeVisible()
    await expect(sidebar.locator('text=Providers')).toBeVisible()
    await expect(sidebar.locator('text=Architecture')).toBeVisible()
    await expect(sidebar.locator('text=Governance')).toBeVisible()
  })

  test('sidebar navigation links to installation guide', async ({ page }) => {
    await page.goto('/guide/getting-started')
    const installLink = page.locator('.VPSidebar a', { hasText: 'Installation' })
    await expect(installLink).toBeVisible()
    await installLink.click()
    await expect(page).toHaveURL(/guide\/installation/)
  })

  test('local search button is visible', async ({ page }) => {
    await page.goto('/')
    const searchButton = page.locator('.VPNavBarSearch button, .DocSearch')
    await expect(searchButton.first()).toBeVisible()
  })

  test('nav bar renders IA section links', async ({ page }) => {
    await page.goto('/')
    const nav = page.locator('.VPNavBar')
    await expect(nav.locator('a', { hasText: 'Guide' })).toBeVisible()
    await expect(nav.locator('a', { hasText: 'Operations' })).toBeVisible()
    await expect(nav.locator('a', { hasText: 'Reference' })).toBeVisible()
    await expect(nav.locator('a', { hasText: 'API' })).toBeVisible()
    await expect(nav.locator('a', { hasText: 'GitHub' })).toBeVisible()
  })

  test('providers page renders examples', async ({ page }) => {
    await page.goto('/guide/providers')
    await expect(page.locator('h1', { hasText: 'Providers' })).toBeVisible()
    await expect(page.locator('code', { hasText: '--provider claude' })).toBeVisible()
  })

  test('operations and reference landing pages load', async ({ page }) => {
    await page.goto('/operations/')
    await expect(page.locator('h1', { hasText: 'Operations' })).toBeVisible()

    await page.goto('/reference/')
    await expect(page.locator('h1', { hasText: 'Reference' })).toBeVisible()
  })
})
