import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth-token', 'mock-jwt-token')
    })
    
    // Mock user data
    await page.route('**/api/user', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          email: 'test@example.com',
          name: 'Test User'
        })
      })
    })
    
    await page.goto('/dashboard')
  })

  test('should display dashboard header', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('should display deployment cards', async ({ page }) => {
    // Mock deployments data
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            name: 'My App',
            status: 'deployed',
            url: 'https://myapp.example.com',
            createdAt: '2024-01-01T00:00:00Z'
          },
          {
            id: '2',
            name: 'Another App',
            status: 'building',
            url: null,
            createdAt: '2024-01-02T00:00:00Z'
          }
        ])
      })
    })

    await page.reload()
    
    // Check for deployment cards
    await expect(page.locator('[data-testid="deployment-card"]')).toHaveCount(2)
    await expect(page.locator('text=My App')).toBeVisible()
    await expect(page.locator('text=Another App')).toBeVisible()
  })

  test('should show empty state when no deployments', async ({ page }) => {
    // Mock empty deployments
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    await page.reload()
    
    // Check for empty state
    await expect(page.locator('text=No deployments yet')).toBeVisible()
    await expect(page.locator('text=Create your first deployment')).toBeVisible()
  })

  test('should navigate to create deployment page', async ({ page }) => {
    await page.click('[data-testid="create-deployment-button"]')
    await expect(page).toHaveURL('/deploy')
  })

  test('should display metrics cards', async ({ page }) => {
    // Mock metrics data
    await page.route('**/api/metrics', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          totalDeployments: 5,
          activeDeployments: 3,
          totalCost: 25.50,
          monthlyCost: 8.75
        })
      })
    })

    await page.reload()
    
    // Check for metrics cards
    await expect(page.locator('[data-testid="metric-card"]')).toHaveCount(4)
    await expect(page.locator('text=Total Deployments')).toBeVisible()
    await expect(page.locator('text=Active Deployments')).toBeVisible()
    await expect(page.locator('text=Total Cost')).toBeVisible()
    await expect(page.locator('text=Monthly Cost')).toBeVisible()
  })

  test('should handle loading states', async ({ page }) => {
    // Mock delayed response
    await page.route('**/api/deployments', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        })
      }, 1000)
    })

    await page.reload()
    
    // Check for loading state
    await expect(page.locator('[data-testid="loading-skeleton"]')).toBeVisible()
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })

    await page.reload()
    
    // Check for error message
    await expect(page.locator('text=Failed to load deployments')).toBeVisible()
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible()
  })

  test('should refresh data when retry button is clicked', async ({ page }) => {
    // Mock initial error
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })

    await page.reload()
    await expect(page.locator('text=Failed to load deployments')).toBeVisible()
    
    // Mock successful response for retry
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            name: 'My App',
            status: 'deployed',
            url: 'https://myapp.example.com',
            createdAt: '2024-01-01T00:00:00Z'
          }
        ])
      })
    })

    await page.click('[data-testid="retry-button"]')
    
    // Check that data loads successfully
    await expect(page.locator('[data-testid="deployment-card"]')).toBeVisible()
  })

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check that dashboard is responsive
    await expect(page.locator('[data-testid="dashboard-container"]')).toBeVisible()
    
    // Check that mobile menu is accessible
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
  })
})