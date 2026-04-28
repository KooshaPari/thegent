import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useDeployments } from '@/lib/hooks/use-deployments'
import { useDeploymentStore } from '@/lib/stores'

const fetchMock = vi.fn()
const jsonResponse = (body: unknown, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  statusText: status === 500 ? 'Internal Server Error' : 'OK',
  headers: { get: () => 'application/json' },
  json: async () => body,
  text: async () => JSON.stringify(body),
})

// Mock the API base URL
vi.mock('@/lib/config', () => ({
  API_BASE_URL: 'http://localhost:3000/api',
  getApiBaseUrl: () => 'http://localhost:3000/api',
  getDeploymentApiBaseUrl: () => 'http://localhost:3000/api'
}))

const mockDeployments = [
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
]

describe('useDeployments Hook', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock)
    vi.clearAllMocks()
    useDeploymentStore.setState(useDeploymentStore.getInitialState(), true)
  })

  it('should fetch deployments successfully', async () => {
    // Mock successful API response
    fetchMock.mockResolvedValue(jsonResponse({ deployments: mockDeployments, total: mockDeployments.length }))

    const { result } = renderHook(() => useDeployments())

    // Initially loading
    expect(result.current.isLoading).toBe(true)
    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBeNull()

    // Wait for the hook to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual(mockDeployments)
    expect(result.current.error).toBeNull()
  })

  it('should handle API errors', async () => {
    // Mock API error
    fetchMock.mockResolvedValue(jsonResponse({ message: 'Bad Request' }, 400))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Bad Request')
  })

  it('should handle network errors', async () => {
    // Mock network error
    fetchMock.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Network error')
  })

  it('should refetch deployments', async () => {
    // Mock successful API response
    fetchMock.mockResolvedValue(jsonResponse({ deployments: mockDeployments, total: mockDeployments.length }))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual(mockDeployments)

    // Call refetch
    await result.current.refresh()

    // Should call fetch again
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('should handle empty deployments array', async () => {
    // Mock empty response
    fetchMock.mockResolvedValue(jsonResponse({ deployments: [], total: 0 }))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should handle malformed JSON response', async () => {
    // Mock malformed JSON
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => {
        throw new Error('Invalid JSON')
      },
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Invalid JSON')
  })

  it('should make correct API call', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ deployments: mockDeployments, total: mockDeployments.length }))

    renderHook(() => useDeployments())

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:3000/api/deployments',
      expect.objectContaining({
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
    )
  })

  it('should handle different deployment statuses', async () => {
    const deploymentsWithDifferentStatuses = [
      { ...mockDeployments[0], status: 'deployed' },
      { ...mockDeployments[1], status: 'building' },
      { ...mockDeployments[0], id: '3', status: 'failed' },
      { ...mockDeployments[0], id: '4', status: 'paused' }
    ]

    fetchMock.mockResolvedValue(jsonResponse({ deployments: deploymentsWithDifferentStatuses, total: deploymentsWithDifferentStatuses.length }))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.deployments).toHaveLength(4)
    expect(result.current.deployments[0].status).toBe('deployed')
    expect(result.current.deployments[1].status).toBe('building')
    expect(result.current.deployments[2].status).toBe('failed')
    expect(result.current.deployments[3].status).toBe('paused')
  })
})
