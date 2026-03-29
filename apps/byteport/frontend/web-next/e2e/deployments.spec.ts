import { test, expect } from '@playwright/test'

test.describe('Deployments', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth-token', 'mock-jwt-token')
    })
    
    await page.goto('/deployments')
  })

  test('should display deployments list', async ({ page }) => {
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

    await page.reload()
    
    // Check for deployments table/list
    await expect(page.locator('[data-testid="deployments-table"]')).toBeVisible()
    await expect(page.locator('text=My App')).toBeVisible()
    await expect(page.locator('text=Another App')).toBeVisible()
  })

  test('should filter deployments by status', async ({ page }) => {
    // Mock deployments data
    await page.route('**/api/deployments', route => {
      const url = new URL(route.request().url())
      const status = url.searchParams.get('status')
      
      const deployments = [
        {
          id: '1',
          name: 'Deployed App',
          status: 'deployed',
          url: 'https://deployed.example.com',
          createdAt: '2024-01-01T00:00:00Z',
          provider: 'vercel'
        },
        {
          id: '2',
          name: 'Building App',
          status: 'building',
          url: null,
          createdAt: '2024-01-02T00:00:00Z',
          provider: 'netlify'
        }
      ]
      
      const filtered = status ? deployments.filter(d => d.status === status) : deployments
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filtered)
      })
    })

    await page.reload()
    
    // Filter by deployed status
    await page.selectOption('[data-testid="status-filter"]', 'deployed')
    await expect(page.locator('text=Deployed App')).toBeVisible()
    await expect(page.locator('text=Building App')).not.toBeVisible()
    
    // Filter by building status
    await page.selectOption('[data-testid="status-filter"]', 'building')
    await expect(page.locator('text=Building App')).toBeVisible()
    await expect(page.locator('text=Deployed App')).not.toBeVisible()
  })

  test('should search deployments by name', async ({ page }) => {
    // Mock deployments data
    await page.route('**/api/deployments', route => {
      const url = new URL(route.request().url())
      const search = url.searchParams.get('search')
      
      const deployments = [
        {
          id: '1',
          name: 'My React App',
          status: 'deployed',
          url: 'https://react.example.com',
          createdAt: '2024-01-01T00:00:00Z',
          provider: 'vercel'
        },
        {
          id: '2',
          name: 'My Vue App',
          status: 'deployed',
          url: 'https://vue.example.com',
          createdAt: '2024-01-02T00:00:00Z',
          provider: 'netlify'
        }
      ]
      
      const filtered = search ? deployments.filter(d => d.name.toLowerCase().includes(search.toLowerCase())) : deployments
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(filtered)
      })
    })

    await page.reload()
    
    // Search for React app
    await page.fill('[data-testid="search-input"]', 'React')
    await page.keyboard.press('Enter')
    
    await expect(page.locator('text=My React App')).toBeVisible()
    await expect(page.locator('text=My Vue App')).not.toBeVisible()
  })

  test('should view deployment details', async ({ page }) => {
    // Mock deployment details
    await page.route('**/api/deployments/1', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          name: 'My App',
          status: 'deployed',
          url: 'https://myapp.example.com',
          createdAt: '2024-01-01T00:00:00Z',
          provider: 'vercel',
          logs: [
            {
              id: '1',
              timestamp: '2024-01-01T00:00:00Z',
              level: 'info',
              message: 'Deployment started'
            }
          ]
        })
      })
    })

    // Mock deployments list
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

    await page.reload()
    
    // Click on deployment to view details
    await page.click('[data-testid="deployment-row-1"]')
    
    // Check for deployment details modal/page
    await expect(page.locator('[data-testid="deployment-details"]')).toBeVisible()
    await expect(page.locator('text=My App')).toBeVisible()
    await expect(page.locator('text=https://myapp.example.com')).toBeVisible()
  })

  test('should delete deployment', async ({ page }) => {
    // Mock delete endpoint
    await page.route('**/api/deployments/1', route => {
      if (route.request().method() === 'DELETE') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        })
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: '1',
            name: 'My App',
            status: 'deployed',
            url: 'https://myapp.example.com',
            createdAt: '2024-01-01T00:00:00Z',
            provider: 'vercel'
          })
        })
      }
    })

    // Mock deployments list
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

    await page.reload()
    
    // Click delete button
    await page.click('[data-testid="delete-deployment-1"]')
    
    // Confirm deletion
    await page.click('[data-testid="confirm-delete"]')
    
    // Check that deployment is removed
    await expect(page.locator('text=My App')).not.toBeVisible()
  })

  test('should handle pagination', async ({ page }) => {
    // Mock paginated deployments
    await page.route('**/api/deployments', route => {
      const url = new URL(route.request().url())
      const page = parseInt(url.searchParams.get('page') || '1')
      const limit = parseInt(url.searchParams.get('limit') || '10')
      
      const allDeployments = Array.from({ length: 25 }, (_, i) => ({
        id: `${i + 1}`,
        name: `App ${i + 1}`,
        status: 'deployed',
        url: `https://app${i + 1}.example.com`,
        createdAt: new Date(2024, 0, i + 1).toISOString(),
        provider: 'vercel'
      }))
      
      const start = (page - 1) * limit
      const end = start + limit
      const deployments = allDeployments.slice(start, end)
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: deployments,
          pagination: {
            page,
            limit,
            total: 25,
            totalPages: 3
          }
        })
      })
    })

    await page.reload()
    
    // Check pagination controls
    await expect(page.locator('[data-testid="pagination"]')).toBeVisible()
    await expect(page.locator('text=Page 1 of 3')).toBeVisible()
    
    // Navigate to next page
    await page.click('[data-testid="next-page"]')
    await expect(page.locator('text=Page 2 of 3')).toBeVisible()
  })

  test('should handle loading and error states', async ({ page }) => {
    // Test loading state
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
    await expect(page.locator('[data-testid="loading-skeleton"]')).toBeVisible()
    
    // Test error state
    await page.route('**/api/deployments', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })

    await page.reload()
    await expect(page.locator('text=Failed to load deployments')).toBeVisible()
  })
})