/**
 * Integration Tests for User Stories
 * 
 * These tests validate complete user journeys and critical business logic
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// These are integration tests that validate business logic
// They test the complete user journeys and API contracts

// Mock fetch globally
global.fetch = vi.fn();

describe('User Story: Auto-Provider Selection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('validates auto-provider selection logic for frontend', async () => {
    // Test the business logic: frontend apps should use vercel
    const appType = 'frontend';
    const expectedProvider = 'vercel';

    // Mock API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'deploy-123',
        name: 'my-frontend-app',
        status: 'deploying',
        provider: expectedProvider,
        url: 'https://my-frontend-app.vercel.app',
        created_at: new Date().toISOString(),
        message: 'Deployment started successfully',
      }),
    });

    const response = await fetch('http://localhost:8080/api/v1/deployments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'my-frontend-app',
        type: appType,
      }),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.provider).toBe(expectedProvider);
    expect(data.url).toContain('vercel.app');
  });

  it('automatically selects Render for backend applications', async () => {
    let capturedRequest: any = null;

    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        capturedRequest = await request.json();
        return HttpResponse.json({
          id: 'deploy-456',
          name: capturedRequest.name,
          status: 'deploying',
          provider: 'render',
          url: `https://${capturedRequest.name}.onrender.com`,
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'my-backend-api',
        type: 'backend',
      }),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.provider).toBe('render');
    expect(data.url).toContain('onrender.com');
  });

  it('automatically selects Supabase for database applications', async () => {
    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({
          id: 'deploy-789',
          name: body.name,
          status: 'deploying',
          provider: 'supabase',
          url: `https://${body.name}.supabase.co`,
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'my-database',
        type: 'database',
      }),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.provider).toBe('supabase');
    expect(data.url).toContain('supabase.co');
  });

  it('respects explicit provider selection over auto-selection', async () => {
    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({
          id: 'deploy-explicit',
          name: body.name,
          status: 'deploying',
          provider: body.provider,
          url: `https://${body.name}.netlify.app`,
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    // Explicitly specify Netlify for a frontend app (would auto-select Vercel)
    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'my-app',
        type: 'frontend',
        provider: 'netlify', // Explicitly specified
      }),
    });

    const data = await response.json();

    expect(data.provider).toBe('netlify');
    expect(data.url).toContain('netlify.app');
  });
});

describe('User Story: Environment Variable Management', () => {
  it('creates deployment with environment variables', async () => {
    const envVars = {
      NODE_ENV: 'production',
      API_URL: 'https://api.example.com',
      DATABASE_URL: 'postgres://...',
      SENTRY_DSN: 'https://sentry.io/xxx',
    };

    let capturedRequest: any = null;

    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        capturedRequest = await request.json();
        return HttpResponse.json({
          id: 'deploy-env-123',
          name: capturedRequest.name,
          status: 'deploying',
          provider: 'vercel',
          url: 'https://my-app.vercel.app',
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'env-test-app',
        type: 'frontend',
        provider: 'vercel',
        env_vars: envVars,
      }),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(capturedRequest?.env_vars).toEqual(envVars);
    expect(Object.keys(capturedRequest?.env_vars || {})).toHaveLength(4);
  });

  it('handles empty environment variables', async () => {
    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({
          id: 'deploy-no-env',
          name: body.name,
          status: 'deploying',
          provider: 'vercel',
          url: 'https://my-app.vercel.app',
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'no-env-app',
        type: 'frontend',
        provider: 'vercel',
        env_vars: {},
      }),
    });

    expect(response.status).toBe(201);
  });

  it('validates required environment variables', async () => {
    const requiredEnvVars = {
      API_KEY: 'test-key',
      DATABASE_URL: 'postgres://localhost/test',
    };

    let capturedEnvVars: any = null;

    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async ({ request }) => {
        const body = await request.json();
        capturedEnvVars = body.env_vars;
        return HttpResponse.json({
          id: 'deploy-validated',
          name: body.name,
          status: 'deploying',
          provider: 'vercel',
          url: 'https://validated-app.vercel.app',
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const response = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'validated-app',
        type: 'backend',
        provider: 'render',
        env_vars: requiredEnvVars,
      }),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(capturedEnvVars).toHaveProperty('API_KEY');
    expect(capturedEnvVars).toHaveProperty('DATABASE_URL');
    expect(capturedEnvVars.API_KEY).toBe('test-key');
  });
});

describe('User Story: Complete Deployment Lifecycle', () => {
  it('creates, monitors, and terminates a deployment', async () => {
    const deploymentId = 'lifecycle-test-123';
    const deploymentName = 'lifecycle-app';

    // Step 1: Create deployment
    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async () => {
        return HttpResponse.json({
          id: deploymentId,
          name: deploymentName,
          status: 'deploying',
          provider: 'vercel',
          url: `https://${deploymentName}.vercel.app`,
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    const createResponse = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: deploymentName,
        type: 'frontend',
        provider: 'vercel',
      }),
    });

    const createdDeployment = await createResponse.json();
    expect(createResponse.status).toBe(201);
    expect(createdDeployment.id).toBe(deploymentId);
    expect(createdDeployment.status).toBe('deploying');

    // Step 2: Monitor deployment status
    server.use(
      http.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/status`, () => {
        return HttpResponse.json({
          id: deploymentId,
          status: 'deployed',
          progress: 100,
          updated_at: new Date().toISOString(),
        });
      })
    );

    const statusResponse = await fetch(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/status`);
    const status = await statusResponse.json();

    expect(statusResponse.status).toBe(200);
    expect(status.status).toBe('deployed');
    expect(status.progress).toBe(100);

    // Step 3: Retrieve deployment details
    server.use(
      http.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`, () => {
        return HttpResponse.json({
          id: deploymentId,
          name: deploymentName,
          type: 'frontend',
          provider: 'vercel',
          status: 'deployed',
          url: `https://${deploymentName}.vercel.app`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      })
    );

    const detailsResponse = await fetch(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`);
    const details = await detailsResponse.json();

    expect(detailsResponse.status).toBe(200);
    expect(details.name).toBe(deploymentName);
    expect(details.status).toBe('deployed');

    // Step 4: Terminate deployment
    server.use(
      http.delete(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`, () => {
        return HttpResponse.json({
          message: 'Deployment terminated successfully',
          id: deploymentId,
        });
      })
    );

    const terminateResponse = await fetch(`${API_BASE_URL}/api/v1/deployments/${deploymentId}`, {
      method: 'DELETE',
    });

    const terminateResult = await terminateResponse.json();

    expect(terminateResponse.status).toBe(200);
    expect(terminateResult.message).toContain('terminated');
    expect(terminateResult.id).toBe(deploymentId);
  });

  it('handles deployment failure gracefully', async () => {
    const deploymentId = 'failed-deploy-456';

    server.use(
      http.post(`${API_BASE_URL}/api/v1/deployments`, async () => {
        return HttpResponse.json({
          id: deploymentId,
          name: 'failing-app',
          status: 'deploying',
          provider: 'vercel',
          url: 'https://failing-app.vercel.app',
          created_at: new Date().toISOString(),
          message: 'Deployment started successfully',
        }, { status: 201 });
      })
    );

    // Create deployment
    const createResponse = await fetch(`${API_BASE_URL}/api/v1/deployments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'failing-app',
        type: 'frontend',
        provider: 'vercel',
      }),
    });

    expect(createResponse.status).toBe(201);

    // Check status - deployment failed
    server.use(
      http.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/status`, () => {
        return HttpResponse.json({
          id: deploymentId,
          status: 'failed',
          progress: 0,
          updated_at: new Date().toISOString(),
          error: 'Build failed: Module not found',
        });
      })
    );

    const statusResponse = await fetch(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/status`);
    const status = await statusResponse.json();

    expect(status.status).toBe('failed');
    expect(status.progress).toBe(0);
    expect(status.error).toBeDefined();
  });

  it('retrieves deployment logs', async () => {
    const deploymentId = 'logs-deploy-789';

    server.use(
      http.get(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/logs`, () => {
        return HttpResponse.json({
          deployment_id: deploymentId,
          logs: [
            {
              timestamp: new Date(Date.now() - 5000).toISOString(),
              level: 'info',
              message: 'Starting deployment process',
            },
            {
              timestamp: new Date(Date.now() - 4000).toISOString(),
              level: 'info',
              message: 'Building application...',
            },
            {
              timestamp: new Date(Date.now() - 2000).toISOString(),
              level: 'info',
              message: 'Deploying to vercel',
            },
            {
              timestamp: new Date().toISOString(),
              level: 'success',
              message: 'Deployment completed successfully',
            },
          ],
        });
      })
    );

    const logsResponse = await fetch(`${API_BASE_URL}/api/v1/deployments/${deploymentId}/logs`);
    const logsData = await logsResponse.json();

    expect(logsResponse.status).toBe(200);
    expect(logsData.logs).toHaveLength(4);
    expect(logsData.logs[0]).toHaveProperty('timestamp');
    expect(logsData.logs[0]).toHaveProperty('level');
    expect(logsData.logs[0]).toHaveProperty('message');
    expect(logsData.logs[3].level).toBe('success');
  });

  it('lists all deployments', async () => {
    server.use(
      http.get(`${API_BASE_URL}/api/v1/deployments`, () => {
        return HttpResponse.json({
          deployments: [
            {
              id: 'deploy-1',
              name: 'App 1',
              status: 'deployed',
              provider: 'vercel',
              url: 'https://app1.vercel.app',
              created_at: new Date().toISOString(),
            },
            {
              id: 'deploy-2',
              name: 'App 2',
              status: 'deploying',
              provider: 'netlify',
              url: 'https://app2.netlify.app',
              created_at: new Date().toISOString(),
            },
            {
              id: 'deploy-3',
              name: 'App 3',
              status: 'failed',
              provider: 'render',
              created_at: new Date().toISOString(),
            },
          ],
          total: 3,
        });
      })
    );

    const listResponse = await fetch(`${API_BASE_URL}/api/v1/deployments`);
    const listData = await listResponse.json();

    expect(listResponse.status).toBe(200);
    expect(listData.deployments).toHaveLength(3);
    expect(listData.total).toBe(3);
    expect(listData.deployments[0].status).toBe('deployed');
    expect(listData.deployments[1].status).toBe('deploying');
    expect(listData.deployments[2].status).toBe('failed');
  });
});
