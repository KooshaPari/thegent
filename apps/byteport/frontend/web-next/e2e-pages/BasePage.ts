import { Page, Locator, expect } from '@playwright/test'

export abstract class BasePage {
  protected page: Page

  constructor(page: Page) {
    this.page = page
  }

  /**
   * Navigate to a specific path
   */
  async goto(path: string = '/') {
    await this.page.goto(path)
  }

  /**
   * Wait for the page to be loaded
   */
  async waitForLoad() {
    await this.page.waitForLoadState('networkidle')
  }

  /**
   * Take a screenshot for debugging
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `e2e-results/${name}.png` })
  }

  /**
   * Common elements that appear on most pages
   */
  get navigation(): Locator {
    return this.page.locator('nav[data-testid="main-nav"]')
  }

  get userProfile(): Locator {
    return this.page.locator('[data-testid="user-profile"]')
  }

  get loadingSpinner(): Locator {
    return this.page.locator('[data-testid="loading-spinner"]')
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="error-message"]')
  }

  get successMessage(): Locator {
    return this.page.locator('[data-testid="success-message"]')
  }

  /**
   * Common actions
   */
  async waitForNoLoading() {
    await expect(this.loadingSpinner).not.toBeVisible({ timeout: 10000 })
  }

  async expectSuccessMessage(text?: string) {
    await expect(this.successMessage).toBeVisible()
    if (text) {
      await expect(this.successMessage).toContainText(text)
    }
  }

  async expectErrorMessage(text?: string) {
    await expect(this.errorMessage).toBeVisible()
    if (text) {
      await expect(this.errorMessage).toContainText(text)
    }
  }

  /**
   * Click and wait for navigation
   */
  async clickAndWaitForNavigation(selector: string | Locator) {
    const locator = typeof selector === 'string' ? this.page.locator(selector) : selector
    
    await Promise.all([
      this.page.waitForLoadState('networkidle'),
      locator.click(),
    ])
  }

  /**
   * Fill form field and validate
   */
  async fillField(selector: string | Locator, value: string) {
    const locator = typeof selector === 'string' ? this.page.locator(selector) : selector
    
    await locator.fill(value)
    await expect(locator).toHaveValue(value)
  }

  /**
   * Select option from dropdown
   */
  async selectOption(selector: string | Locator, value: string) {
    const locator = typeof selector === 'string' ? this.page.locator(selector) : selector
    
    await locator.selectOption(value)
  }

  /**
   * Upload file to input
   */
  async uploadFile(selector: string | Locator, filePath: string) {
    const locator = typeof selector === 'string' ? this.page.locator(selector) : selector
    
    await locator.setInputFiles(filePath)
  }

  /**
   * Wait for element to be stable (useful for dynamic content)
   */
  async waitForStable(selector: string | Locator) {
    const locator = typeof selector === 'string' ? this.page.locator(selector) : selector
    
    await locator.waitFor({ state: 'visible' })
    
    // Wait for any animations or transitions to complete
    await this.page.waitForTimeout(500)
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      await this.userProfile.waitFor({ state: 'visible', timeout: 5000 })
      return true
    } catch {
      return false
    }
  }

  /**
   * Assert page title
   */
  async expectPageTitle(title: string) {
    await expect(this.page).toHaveTitle(title)
  }

  /**
   * Assert current URL
   */
  async expectURL(url: string | RegExp) {
    await expect(this.page).toHaveURL(url)
  }
}