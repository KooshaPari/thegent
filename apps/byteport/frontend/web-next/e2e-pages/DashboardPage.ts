import { Page, Locator, expect } from '@playwright/test'
import { BasePage } from './BasePage'

export class DashboardPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  /**
   * Dashboard-specific locators
   */
  get deploymentsList(): Locator {
    return this.page.locator('[data-testid="deployments-list"]')
  }

  get deploymentCards(): Locator {
    return this.page.locator('[data-testid="deployment-card"]')
  }

  get createDeploymentButton(): Locator {
    return this.page.locator('[data-testid="create-deployment-button"]')
  }

  get searchInput(): Locator {
    return this.page.locator('[data-testid="search-deployments"]')
  }

  get filterDropdown(): Locator {
    return this.page.locator('[data-testid="filter-deployments"]')
  }

  get statsCards(): Locator {
    return this.page.locator('[data-testid="stats-card"]')
  }

  get recentActivity(): Locator {
    return this.page.locator('[data-testid="recent-activity"]')
  }

  /**
   * Navigation to dashboard
   */
  async goto() {
    await super.goto('/dashboard')
    await this.waitForLoad()
  }

  /**
   * Dashboard-specific actions
   */
  async createNewDeployment() {
    await this.createDeploymentButton.click()
    await this.page.waitForURL('**/deployments/new')
  }

  async searchDeployments(query: string) {
    await this.searchInput.fill(query)
    // Wait for search results to update
    await this.page.waitForTimeout(500)
  }

  async filterDeploymentsByStatus(status: string) {
    await this.filterDropdown.click()
    await this.page.locator(`[data-value="${status}"]`).click()
    // Wait for filter to apply
    await this.page.waitForTimeout(500)
  }

  async getDeploymentCard(deploymentName: string): Promise<Locator> {
    return this.page.locator('[data-testid="deployment-card"]', { 
      has: this.page.locator(`text=${deploymentName}`) 
    })
  }

  async clickDeployment(deploymentName: string) {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    await deploymentCard.click()
    await this.page.waitForLoadState('networkidle')
  }

  async getDeploymentStatus(deploymentName: string): Promise<string> {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    const statusBadge = deploymentCard.locator('[data-testid="status-badge"]')
    return await statusBadge.textContent() || ''
  }

  async getDeploymentUrl(deploymentName: string): Promise<string> {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    const urlLink = deploymentCard.locator('[data-testid="deployment-url"]')
    return await urlLink.getAttribute('href') || ''
  }

  /**
   * Dashboard assertions
   */
  async expectDeploymentsLoaded() {
    await expect(this.deploymentsList).toBeVisible()
    await this.waitForNoLoading()
  }

  async expectDeploymentCount(count: number) {
    await expect(this.deploymentCards).toHaveCount(count)
  }

  async expectDeploymentVisible(deploymentName: string) {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    await expect(deploymentCard).toBeVisible()
  }

  async expectDeploymentNotVisible(deploymentName: string) {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    await expect(deploymentCard).not.toBeVisible()
  }

  async expectDeploymentStatus(deploymentName: string, status: string) {
    const actualStatus = await this.getDeploymentStatus(deploymentName)
    expect(actualStatus.toLowerCase()).toContain(status.toLowerCase())
  }

  async expectStatsCardsVisible() {
    await expect(this.statsCards).toHaveCount(3) // Assuming 3 stats cards
    await expect(this.statsCards.first()).toBeVisible()
  }

  async expectRecentActivityVisible() {
    await expect(this.recentActivity).toBeVisible()
  }

  /**
   * Wait for real-time updates
   */
  async waitForDeploymentStatusUpdate(deploymentName: string, expectedStatus: string) {
    const deploymentCard = await this.getDeploymentCard(deploymentName)
    const statusBadge = deploymentCard.locator('[data-testid="status-badge"]')
    
    await expect(statusBadge).toContainText(expectedStatus, { timeout: 30000 })
  }

  /**
   * Bulk actions
   */
  async selectMultipleDeployments(deploymentNames: string[]) {
    for (const name of deploymentNames) {
      const deploymentCard = await this.getDeploymentCard(name)
      const checkbox = deploymentCard.locator('[type="checkbox"]')
      await checkbox.check()
    }
  }

  async deleteSelectedDeployments() {
    await this.page.locator('[data-testid="delete-selected-button"]').click()
    
    // Confirm deletion in modal
    await this.page.locator('[data-testid="confirm-delete-button"]').click()
    
    await this.expectSuccessMessage('Deployments deleted successfully')
  }
}