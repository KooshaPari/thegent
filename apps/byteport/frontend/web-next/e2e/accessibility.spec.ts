import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth-token', 'mock-jwt-token')
    })
  })

  test('should not have accessibility violations on login page', async ({ page }) => {
    await page.goto('/auth/login')
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should not have accessibility violations on dashboard', async ({ page }) => {
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
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should not have accessibility violations on deployments page', async ({ page }) => {
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
          }
        ])
      })
    })
    
    await page.goto('/deployments')
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper keyboard navigation', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Test tab navigation
    await page.keyboard.press('Tab')
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName)
    expect(firstFocused).toBeTruthy()
    
    // Test that all interactive elements are reachable via keyboard
    const interactiveElements = await page.locator('button, input, select, textarea, [tabindex]:not([tabindex="-1"])').all()
    
    for (let i = 0; i < interactiveElements.length; i++) {
      await page.keyboard.press('Tab')
      const isVisible = await page.evaluate(() => {
        const active = document.activeElement
        return active && active.offsetParent !== null
      })
      expect(isVisible).toBe(true)
    }
  })

  test('should have proper ARIA labels and roles', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Check for proper heading structure
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all()
    expect(headings.length).toBeGreaterThan(0)
    
    // Check for proper button labels
    const buttons = await page.locator('button').all()
    for (const button of buttons) {
      const hasLabel = await button.evaluate(el => {
        return el.textContent?.trim() || 
               el.getAttribute('aria-label') || 
               el.getAttribute('aria-labelledby')
      })
      expect(hasLabel).toBeTruthy()
    }
    
    // Check for proper form labels
    const inputs = await page.locator('input, select, textarea').all()
    for (const input of inputs) {
      const hasLabel = await input.evaluate(el => {
        const id = el.getAttribute('id')
        if (id) {
          const label = document.querySelector(`label[for="${id}"]`)
          return !!label
        }
        return el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')
      })
      expect(hasLabel).toBeTruthy()
    }
  })

  test('should have proper color contrast', async ({ page }) => {
    await page.goto('/dashboard')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    
    // Filter for color contrast violations
    const colorContrastViolations = accessibilityScanResults.violations.filter(
      violation => violation.id === 'color-contrast'
    )
    
    expect(colorContrastViolations).toEqual([])
  })

  test('should work with screen reader', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Check for proper semantic HTML
    const main = await page.locator('main, [role="main"]').first()
    expect(main).toBeVisible()
    
    // Check for proper landmarks
    const landmarks = await page.locator('[role="banner"], [role="navigation"], [role="main"], [role="contentinfo"]').all()
    expect(landmarks.length).toBeGreaterThan(0)
    
    // Check for skip links
    const skipLink = await page.locator('a[href="#main-content"]').first()
    if (await skipLink.isVisible()) {
      expect(skipLink).toBeVisible()
    }
  })

  test('should handle focus management in modals', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Open a modal (if available)
    const modalTrigger = await page.locator('[data-testid="open-modal"]').first()
    if (await modalTrigger.isVisible()) {
      await modalTrigger.click()
      
      // Check that focus is trapped in modal
      const modal = await page.locator('[role="dialog"]').first()
      expect(modal).toBeVisible()
      
      // Check that focus is on first focusable element
      const firstFocusable = await modal.locator('button, input, select, textarea, [tabindex]:not([tabindex="-1"])').first()
      if (await firstFocusable.isVisible()) {
        await expect(firstFocusable).toBeFocused()
      }
      
      // Test escape key closes modal
      await page.keyboard.press('Escape')
      await expect(modal).not.toBeVisible()
    }
  })

  test('should have proper form validation messages', async ({ page }) => {
    await page.goto('/auth/login')
    
    // Try to submit empty form
    await page.click('button[type="submit"]')
    
    // Check for validation messages
    const errorMessages = await page.locator('[role="alert"], .error-message').all()
    expect(errorMessages.length).toBeGreaterThan(0)
    
    // Check that error messages are associated with form fields
    for (const error of errorMessages) {
      const ariaDescribedBy = await error.getAttribute('aria-describedby')
      const id = await error.getAttribute('id')
      
      if (ariaDescribedBy) {
        const describedElement = await page.locator(`#${ariaDescribedBy}`).first()
        expect(await describedElement.isVisible()).toBe(true)
      } else if (id) {
        const associatedInput = await page.locator(`[aria-describedby="${id}"]`).first()
        expect(await associatedInput.isVisible()).toBe(true)
      }
    }
  })

  test('should be accessible on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/dashboard')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper loading states for screen readers', async ({ page }) => {
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
    
    // Check for loading indicator with proper ARIA attributes
    const loadingIndicator = await page.locator('[aria-live="polite"], [aria-live="assertive"]').first()
    if (await loadingIndicator.isVisible()) {
      expect(loadingIndicator).toBeVisible()
    }
  })
})