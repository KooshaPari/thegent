import { test, expect } from '@playwright/test'

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth-token', 'mock-jwt-token')
    })
  })

  test('login page visual regression', async ({ page }) => {
    await page.goto('/auth/login')
    await page.waitForLoadState('networkidle')
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('login-page.png', {
      fullPage: true,
      threshold: 0.2
    })
  })

  test('dashboard page visual regression', async ({ page }) => {
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
    
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('dashboard-page.png', {
      fullPage: true,
      threshold: 0.2
    })
  })

  test('deployments page visual regression', async ({ page }) => {
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
            createdAt: '2024-01-01T00:00:00Z',
            provider: 'vercel'
          },
          {
            id: '2',
            name: 'Another App',
            status: 'building',
            url: null,
            createdAt: '2024-01-02T00:00:00Z',
            provider: 'netlify'
          }
        ])
      })
    })
    
    await page.goto('/deployments')
    await page.waitForLoadState('networkidle')
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('deployments-page.png', {
      fullPage: true,
      threshold: 0.2
    })
  })

  test('mobile responsive design', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    
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
          }
        ])
      })
    })
    
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Take mobile screenshot
    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      fullPage: true,
      threshold: 0.2
    })
  })

  test('tablet responsive design', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    
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
          }
        ])
      })
    })
    
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Take tablet screenshot
    await expect(page).toHaveScreenshot('dashboard-tablet.png', {
      fullPage: true,
      threshold: 0.2
    })
  })

  test('component states visual regression', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Test button states
    const button = await page.locator('button').first()
    if (await button.isVisible()) {
      // Normal state
      await expect(button).toHaveScreenshot('button-normal.png')
      
      // Hover state
      await button.hover()
      await expect(button).toHaveScreenshot('button-hover.png')
      
      // Focus state
      await button.focus()
      await expect(button).toHaveScreenshot('button-focus.png')
    }
    
    // Test input states
    const input = await page.locator('input').first()
    if (await input.isVisible()) {
      // Normal state
      await expect(input).toHaveScreenshot('input-normal.png')
      
      // Focus state
      await input.focus()
      await expect(input).toHaveScreenshot('input-focus.png')
      
      // Error state
      await input.fill('invalid')
      await input.blur()
      await expect(input).toHaveScreenshot('input-error.png')
    }
  })

  test('modal and dialog visual regression', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Open modal if available
    const modalTrigger = await page.locator('[data-testid="open-modal"]').first()
    if (await modalTrigger.isVisible()) {
      await modalTrigger.click()
      
      const modal = await page.locator('[role="dialog"]').first()
      await expect(modal).toHaveScreenshot('modal-open.png', {
        threshold: 0.2
      })
      
      // Test modal backdrop
      await expect(page.locator('[data-testid="modal-backdrop"]')).toHaveScreenshot('modal-backdrop.png')
    }
  })

  test('loading states visual regression', async ({ page }) => {
    await page.goto('/dashboard')
    
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
    
    // Test loading skeleton
    const loadingSkeleton = await page.locator('[data-testid="loading-skeleton"]').first()
    if (await loadingSkeleton.isVisible()) {
      await expect(loadingSkeleton).toHaveScreenshot('loading-skeleton.png')
    }
  })

  test('error states visual regression', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Mock API error
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })
    
    await page.reload()
    
    // Test error state
    const errorMessage = await page.locator('[data-testid="error-message"]').first()
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toHaveScreenshot('error-message.png')
    }
  })

  test('dark mode visual regression', async ({ page }) => {
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
          }
        ])
      })
    })
    
    await page.goto('/dashboard')
    
    // Switch to dark mode
    const themeToggle = await page.locator('[data-testid="theme-toggle"]').first()
    if (await themeToggle.isVisible()) {
      await themeToggle.click()
      await page.waitForTimeout(500) // Wait for theme transition
      
      // Take dark mode screenshot
      await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
        fullPage: true,
        threshold: 0.2
      })
    }
  })
})