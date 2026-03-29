import { Page, Locator, expect } from '@playwright/test'
import { BasePage } from './BasePage'

export class DeploymentPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  /**
   * Deployment creation form locators
   */
  get nameInput(): Locator {
    return this.page.locator('[name="name"]')
  }

  get typeSelect(): Locator {
    return this.page.locator('[name="type"]')
  }

  get providerSelect(): Locator {
    return this.page.locator('[name="provider"]')
  }

  get gitUrlInput(): Locator {
    return this.page.locator('[name="git_url"]')
  }

  get branchInput(): Locator {
    return this.page.locator('[name="branch"]')
  }

  get envVarsSection(): Locator {
    return this.page.locator('[data-testid="env-vars-section"]')
  }

  get addEnvVarButton(): Locator {
    return this.page.locator('[data-testid="add-env-var"]')
  }

  get submitButton(): Locator {
    return this.page.locator('[type="submit"]')
  }

  get cancelButton(): Locator {
    return this.page.locator('[data-testid="cancel-button"]')
  }

  /**
   * Deployment details page locators
   */
  get deploymentHeader(): Locator {
    return this.page.locator('[data-testid="deployment-header"]')
  }

  get statusBadge(): Locator {
    return this.page.locator('[data-testid="status-badge"]')
  }

  get deploymentUrl(): Locator {
    return this.page.locator('[data-testid="deployment-url"]')
  }

  get logsSection(): Locator {
    return this.page.locator('[data-testid="logs-section"]')
  }

  get metricsSection(): Locator {
    return this.page.locator('[data-testid="metrics-section"]')
  }

  get settingsTab(): Locator {
    return this.page.locator('[data-testid="settings-tab"]')
  }

  get terminateButton(): Locator {
    return this.page.locator('[data-testid="terminate-deployment"]')
  }

  get redeployButton(): Locator {
    return this.page.locator('[data-testid="redeploy-button"]')
  }

  /**
   * Navigation methods
   */
  async gotoNewDeployment() {
    await super.goto('/deployments/new')
    await this.waitForLoad()
  }

  async gotoDeployment(deploymentId: string) {
    await super.goto(`/deployments/${deploymentId}`)
    await this.waitForLoad()
  }

  /**
   * Deployment creation actions
   */
  async fillBasicInfo(data: {
    name: string
    type: 'frontend' | 'backend' | 'fullstack'
    provider?: string
    gitUrl?: string
    branch?: string
  }) {
    await this.fillField(this.nameInput, data.name)
    
    await this.typeSelect.click()
    await this.page.locator(`[data-value="${data.type}"]`).click()
    
    if (data.provider) {
      await this.providerSelect.click()
      await this.page.locator(`[data-value="${data.provider}"]`).click()
    }
    
    if (data.gitUrl) {
      await this.fillField(this.gitUrlInput, data.gitUrl)
    }
    
    if (data.branch) {
      await this.fillField(this.branchInput, data.branch)
    }
  }

  async addEnvironmentVariable(key: string, value: string) {
    await this.addEnvVarButton.click()
    
    const envVarRows = this.page.locator('[data-testid="env-var-row"]')
    const lastRow = envVarRows.last()
    
    await lastRow.locator('[name="key"]').fill(key)
    await lastRow.locator('[name="value"]').fill(value)
  }

  async addMultipleEnvironmentVariables(envVars: Record<string, string>) {
    for (const [key, value] of Object.entries(envVars)) {
      await this.addEnvironmentVariable(key, value)
    }
  }

  async removeEnvironmentVariable(key: string) {
    const envVarRow = this.page.locator('[data-testid="env-var-row"]', {
      has: this.page.locator(`[value="${key}"]`)
    })
    
    await envVarRow.locator('[data-testid="remove-env-var"]').click()
  }

  async submitDeployment() {
    await this.submitButton.click()
    
    // Wait for deployment to be created and redirect
    await this.page.waitForURL('**/deployments/**')
    await this.waitForLoad()
  }

  async cancelDeployment() {
    await this.cancelButton.click()
    await this.page.waitForURL('**/dashboard')
  }

  /**
   * Deployment details actions
   */
  async visitDeploymentUrl() {
    const url = await this.deploymentUrl.getAttribute('href')
    if (url) {
      await this.page.goto(url)
    }
  }

  async switchToLogsTab() {
    await this.page.locator('[data-testid="logs-tab"]').click()
    await expect(this.logsSection).toBeVisible()
  }

  async switchToMetricsTab() {
    await this.page.locator('[data-testid="metrics-tab"]').click()
    await expect(this.metricsSection).toBeVisible()
  }

  async switchToSettingsTab() {
    await this.settingsTab.click()
    await this.page.waitForLoadState('networkidle')
  }

  async redeployment() {
    await this.redeployButton.click()
    
    // Confirm redeploy in modal
    await this.page.locator('[data-testid="confirm-redeploy"]').click()
    
    await this.expectSuccessMessage('Redeployment started')
  }

  async terminateDeployment() {
    await this.terminateButton.click()
    
    // Confirm termination in modal
    await this.page.locator('[data-testid="confirm-terminate"]').click()
    
    await this.expectSuccessMessage('Deployment terminated')
  }

  /**
   * Logs-specific actions
   */
  async waitForLogEntry(text: string) {
    const logEntry = this.page.locator('[data-testid="log-entry"]', {
      has: this.page.locator(`text=${text}`)
    })
    
    await expect(logEntry).toBeVisible({ timeout: 30000 })
  }

  async downloadLogs() {
    const downloadPromise = this.page.waitForEvent('download')
    await this.page.locator('[data-testid="download-logs"]').click()
    const download = await downloadPromise
    
    return download
  }

  async filterLogsByLevel(level: 'info' | 'warning' | 'error') {
    await this.page.locator('[data-testid="log-level-filter"]').click()
    await this.page.locator(`[data-value="${level}"]`).click()
    
    // Wait for filter to apply
    await this.page.waitForTimeout(500)
  }

  /**
   * Form validation assertions
   */
  async expectValidationError(field: string, message: string) {
    const errorElement = this.page.locator(`[data-testid="${field}-error"]`)
    await expect(errorElement).toBeVisible()
    await expect(errorElement).toContainText(message)
  }

  async expectFormValid() {
    await expect(this.submitButton).toBeEnabled()
  }

  async expectFormInvalid() {
    await expect(this.submitButton).toBeDisabled()
  }

  /**
   * Deployment status assertions
   */
  async expectStatus(status: string) {
    await expect(this.statusBadge).toContainText(status)
  }

  async expectDeploymentUrl(url: string) {
    await expect(this.deploymentUrl).toHaveAttribute('href', url)
  }

  async waitForStatusChange(expectedStatus: string) {
    await expect(this.statusBadge).toContainText(expectedStatus, { timeout: 60000 })
  }

  /**
   * Environment variables assertions
   */
  async expectEnvironmentVariable(key: string, value: string) {
    const envVarRow = this.page.locator('[data-testid="env-var-row"]', {
      has: this.page.locator(`[value="${key}"]`)
    })
    
    const valueInput = envVarRow.locator('[name="value"]')
    await expect(valueInput).toHaveValue(value)
  }

  async expectEnvironmentVariableCount(count: number) {
    await expect(this.page.locator('[data-testid="env-var-row"]')).toHaveCount(count)
  }
}