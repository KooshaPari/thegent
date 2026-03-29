import { test as setup, expect } from '@playwright/test'

const authFile = 'e2e/.auth/user.json'

setup('authenticate', async ({ page }) => {
  // Perform authentication steps
  await page.goto('/')
  
  // Check if we need to authenticate with WorkOS
  // This will depend on your actual auth flow
  
  // For now, we'll simulate a successful authentication state
  // In a real scenario, this would involve:
  // 1. Going to login page
  // 2. Filling in credentials
  // 3. Clicking sign in
  // 4. Waiting for redirect to dashboard
  
  // Example authentication flow (adjust based on your WorkOS setup):
  /*
  await page.click('[data-testid="login-button"]')
  await page.waitForURL('** /auth/login')
  
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')
  
  // Wait for successful authentication
  await page.waitForURL('/')
  await expect(page.locator('[data-testid="user-nav"]')).toBeVisible()
  */
  
  // For testing purposes, we'll create a mock authenticated state
  // This simulates being logged in with WorkOS AuthKit
  await page.addInitScript(() => {
    // Mock authenticated user data
    window.localStorage.setItem('workos-user', JSON.stringify({
      id: 'user_test_123',
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'User',
    }))
    
    // Mock auth token
    window.localStorage.setItem('workos-token', 'mock_jwt_token')
  })
  
  // Visit the main page to trigger auth initialization
  await page.goto('/')
  
  // Verify we're authenticated (adjust selector based on your UI)
  // await expect(page.locator('[data-testid="user-profile"]')).toBeVisible()
  
  // Save signed-in state to 'authFile'
  await page.context().storageState({ path: authFile })
})

setup.describe.configure({ mode: 'serial' })