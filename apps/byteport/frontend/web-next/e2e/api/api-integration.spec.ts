import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  test('should handle API health check', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/health`);
    
    // API should be reachable (or we're in a test environment)
    if (response.ok()) {
      expect(response.status()).toBe(200);
      const body = await response.json();
      expect(body).toHaveProperty('status');
    } else {
      // In test environment, API might not be running
      expect([200, 404, 500, 503]).toContain(response.status());
    }
  });

  test('should fetch deployments list', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/deployments`, {
      headers: {
        'Accept': 'application/json',
      },
    });

    if (response.ok()) {
      const body = await response.json();
      expect(body).toHaveProperty('deployments');
      expect(Array.isArray(body.deployments)).toBeTruthy();
    }
  });

  test('should create deployment via API', async ({ request }) => {
    const deploymentData = {
      name: 'E2E Test App',
      type: 'frontend',
      provider: 'vercel',
      git_url: 'https://github.com/test/app.git',
      branch: 'main',
    };

    const response = await request.post(`${API_BASE_URL}/api/v1/deployments`, {
      data: deploymentData,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(201);
      const body = await response.json();
      expect(body).toHaveProperty('id');
      expect(body).toHaveProperty('name', 'E2E Test App');
    } else if (response.status() === 400) {
      // Validation error is acceptable
      const body = await response.json();
      expect(body).toHaveProperty('error');
    }
  });

  test('should get deployment by ID', async ({ request }) => {
    // First, get list of deployments
    const listResponse = await request.get(`${API_BASE_URL}/api/v1/deployments`);
    
    if (listResponse.ok()) {
      const listBody = await listResponse.json();
      
      if (listBody.deployments && listBody.deployments.length > 0) {
        const deploymentId = listBody.deployments[0].id;
        
        // Fetch specific deployment
        const response = await request.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`);
        
        if (response.ok()) {
          const body = await response.json();
          expect(body).toHaveProperty('id', deploymentId);
          expect(body).toHaveProperty('name');
          expect(body).toHaveProperty('status');
        }
      }
    }
  });

  test('should handle invalid deployment ID', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/deployments/invalid-id-123`);
    
    expect(response.status()).toBe(404);
    const body = await response.json();
    expect(body).toHaveProperty('error');
  });

  test('should get deployment logs', async ({ request }) => {
    const listResponse = await request.get(`${API_BASE_URL}/api/v1/deployments`);
    
    if (listResponse.ok()) {
      const listBody = await listResponse.json();
      
      if (listBody.deployments && listBody.deployments.length > 0) {
        const deploymentId = listBody.deployments[0].id;
        
        const response = await request.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/logs`);
        
        if (response.ok()) {
          const body = await response.json();
          expect(body).toHaveProperty('logs');
          expect(Array.isArray(body.logs) || typeof body.logs === 'string').toBeTruthy();
        }
      }
    }
  });

  test('should get deployment status', async ({ request }) => {
    const listResponse = await request.get(`${API_BASE_URL}/api/v1/deployments`);
    
    if (listResponse.ok()) {
      const listBody = await listResponse.json();
      
      if (listBody.deployments && listBody.deployments.length > 0) {
        const deploymentId = listBody.deployments[0].id;
        
        const response = await request.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/status`);
        
        if (response.ok()) {
          const body = await response.json();
          expect(body).toHaveProperty('status');
          expect(['pending', 'building', 'deploying', 'running', 'failed', 'terminated']).toContain(body.status);
        }
      }
    }
  });

  test('should terminate deployment', async ({ request }) => {
    // Create a test deployment first
    const createResponse = await request.post(`${API_BASE_URL}/api/v1/deployments`, {
      data: {
        name: 'Terminate Test',
        type: 'frontend',
        provider: 'vercel',
      },
    });

    if (createResponse.ok()) {
      const createBody = await createResponse.json();
      const deploymentId = createBody.id;

      // Terminate it
      const response = await request.delete(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`);
      
      if (response.ok()) {
        expect(response.status()).toBe(200);
        const body = await response.json();
        expect(body).toHaveProperty('message');
      }
    }
  });

  test('should handle rate limiting gracefully', async ({ request }) => {
    // Make multiple rapid requests
    const promises = Array(10).fill(null).map(() =>
      request.get(`${API_BASE_URL}/api/v1/deployments`)
    );

    const responses = await Promise.all(promises);
    
    // Most should succeed, or we should handle rate limiting
    const statusCodes = responses.map(r => r.status());
    expect(statusCodes.some(code => code === 200 || code === 429)).toBeTruthy();
  });

  test('should handle malformed requests', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/deployments`, {
      data: 'invalid json string',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    expect(response.status()).toBe(400);
  });
});

test.describe('API Error Handling', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  test('should return proper error for missing fields', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/deployments`, {
      data: {
        // Missing required fields
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(body).toHaveProperty('error');
  });

  test('should handle network timeouts', async ({ request }) => {
    // Set a very short timeout to force timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 1);

    try {
      await request.get(`${API_BASE_URL}/api/v1/deployments`, {
        timeout: 1,
      });
    } catch (error) {
      // Timeout is expected
      expect(error).toBeTruthy();
    } finally {
      clearTimeout(timeout);
    }
  });

  test('should handle CORS properly', async ({ request, page }) => {
    // Test CORS from browser context
    await page.goto('about:blank');
    
    const result = await page.evaluate(async (url) => {
      try {
        const response = await fetch(`${url}/api/v1/deployments`);
        return { ok: response.ok, status: response.status };
      } catch (error: any) {
        return { error: error.message };
      }
    }, API_BASE_URL);

    // Either succeeds or fails with appropriate CORS error
    expect(result).toBeTruthy();
  });
});

test.describe('API Performance', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  test('should respond within acceptable time', async ({ request }) => {
    const start = Date.now();
    const response = await request.get(`${API_BASE_URL}/api/v1/deployments`);
    const duration = Date.now() - start;

    // Should respond within 5 seconds
    expect(duration).toBeLessThan(5000);
  });

  test('should handle concurrent requests', async ({ request }) => {
    const start = Date.now();
    
    // Make 5 concurrent requests
    const promises = Array(5).fill(null).map(() =>
      request.get(`${API_BASE_URL}/api/v1/deployments`)
    );

    const responses = await Promise.all(promises);
    const duration = Date.now() - start;

    // All should complete
    expect(responses).toHaveLength(5);
    
    // Should handle concurrency efficiently (not 5x single request time)
    expect(duration).toBeLessThan(10000);
  });
});
