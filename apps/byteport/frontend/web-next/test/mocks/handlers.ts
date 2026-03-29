import { http, HttpResponse } from 'msw'

// Mock deployment data
const mockDeployments = [
  {
    id: 'dep_123',
    name: 'My Next.js App',
    status: 'deployed',
    url: 'https://my-nextjs-app.vercel.app',
    provider: 'vercel',
    type: 'frontend',
    created_at: '2024-01-10T12:00:00Z',
    updated_at: '2024-01-10T12:05:00Z',
  },
  {
    id: 'dep_456',
    name: 'API Server',
    status: 'failed',
    url: '',
    provider: 'render',
    type: 'backend',
    created_at: '2024-01-11T14:00:00Z',
    updated_at: '2024-01-11T14:02:00Z',
  },
]

// API handlers for BytePort API
export const handlers = [
  // Get all deployments
  http.get('/api/v1/deployments', () => {
    return HttpResponse.json({
      deployments: mockDeployments,
      total: mockDeployments.length,
    })
  }),

  // Get specific deployment
  http.get('/api/v1/deployments/:id', ({ params }) => {
    const { id } = params
    const deployment = mockDeployments.find((dep) => dep.id === id)
    
    if (!deployment) {
      return new HttpResponse(
        JSON.stringify({ error: 'Deployment not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }
    
    return HttpResponse.json(deployment)
  }),

  // Create deployment
  http.post('/api/v1/deployments', async ({ request }) => {
    const body = await request.json() as any
    const newDeployment = {
      id: `dep_${Date.now()}`,
      name: body.name,
      type: body.type,
      provider: body.provider || 'vercel',
      status: 'deploying',
      url: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    // Simulate validation errors
    if (!body.name) {
      return new HttpResponse(
        JSON.stringify({ 
          error: 'Invalid request format',
          details: 'name is required'
        }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    if (!body.type) {
      return new HttpResponse(
        JSON.stringify({ 
          error: 'Invalid request format',
          details: 'type is required'
        }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return HttpResponse.json(newDeployment, { status: 201 })
  }),

  // Update deployment status
  http.patch('/api/v1/deployments/:id', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as any
    const deployment = mockDeployments.find((dep) => dep.id === id)
    
    if (!deployment) {
      return new HttpResponse(
        JSON.stringify({ error: 'Deployment not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    // Update deployment
    Object.assign(deployment, body, {
      updated_at: new Date().toISOString(),
    })
    
    return HttpResponse.json(deployment)
  }),

  // Delete deployment
  http.delete('/api/v1/deployments/:id', ({ params }) => {
    const { id } = params
    const deployment = mockDeployments.find((dep) => dep.id === id)
    
    if (!deployment) {
      return new HttpResponse(
        JSON.stringify({ error: 'Deployment not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return HttpResponse.json({
      message: 'Deployment terminated successfully',
      id,
    })
  }),

  // Get deployment logs
  http.get('/api/v1/deployments/:id/logs', ({ params }) => {
    const { id } = params
    const deployment = mockDeployments.find((dep) => dep.id === id)
    
    if (!deployment) {
      return new HttpResponse(
        JSON.stringify({ error: 'Deployment not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return HttpResponse.json({
      logs: [
        {
          timestamp: '2024-01-10T12:00:00Z',
          level: 'info',
          message: 'Starting deployment...',
        },
        {
          timestamp: '2024-01-10T12:01:00Z',
          level: 'info',
          message: 'Installing dependencies...',
        },
        {
          timestamp: '2024-01-10T12:03:00Z',
          level: 'info',
          message: 'Building application...',
        },
        {
          timestamp: '2024-01-10T12:05:00Z',
          level: 'success',
          message: 'Deployment complete!',
        },
      ],
    })
  }),

  // Health check
  http.get('/api/v1/health', () => {
    return HttpResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
    })
  }),

  // Authentication endpoints (mocked)
  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as any
    
    if (body.email === 'test@example.com' && body.password === 'password') {
      return HttpResponse.json({
        user: {
          id: 'user_123',
          email: 'test@example.com',
          name: 'Test User',
        },
        token: 'mock_jwt_token',
      })
    }

    return new HttpResponse(
      JSON.stringify({ error: 'Invalid credentials' }),
      { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json({ message: 'Logged out successfully' })
  }),

  // User profile
  http.get('/api/auth/me', ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new HttpResponse(
        JSON.stringify({ error: 'Unauthorized' }),
        { 
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return HttpResponse.json({
      id: 'user_123',
      email: 'test@example.com',
      name: 'Test User',
    })
  }),
]