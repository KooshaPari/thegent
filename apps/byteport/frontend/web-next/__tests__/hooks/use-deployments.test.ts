import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useDeployments } from '@/lib/hooks/use-deployments'

// Mock fetch globally
global.fetch = vi.fn()

// Mock the API base URL
vi.mock('@/lib/config', () => ({
  API_BASE_URL: 'http://localhost:3000/api'
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
    vi.clearAllMocks()
  })

  it('should fetch deployments successfully', async () => {
    // Mock successful API response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeployments
    })

    const { result } = renderHook(() => useDeployments())

    // Initially loading
    expect(result.current.loading).toBe(true)
    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBeNull()

    // Wait for the hook to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual(mockDeployments)
    expect(result.current.error).toBeNull()
  })

  it('should handle API errors', async () => {
    // Mock API error
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Failed to fetch deployments: 500 Internal Server Error')
  })

  it('should handle network errors', async () => {
    // Mock network error
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Failed to fetch deployments: Network error')
  })

  it('should refetch deployments', async () => {
    // Mock successful API response
    ;(global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockDeployments
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual(mockDeployments)

    // Call refetch
    await result.current.refetch()

    // Should call fetch again
    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('should handle empty deployments array', async () => {
    // Mock empty response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should handle malformed JSON response', async () => {
    // Mock malformed JSON
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => {
        throw new Error('Invalid JSON')
      }
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toEqual([])
    expect(result.current.error).toBe('Failed to fetch deployments: Invalid JSON')
  })

  it('should make correct API call', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeployments
    })

    renderHook(() => useDeployments())

    expect(global.fetch).toHaveBeenCalledWith(
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

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => deploymentsWithDifferentStatuses
    })

    const { result } = renderHook(() => useDeployments())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.deployments).toHaveLength(4)
    expect(result.current.deployments[0].status).toBe('deployed')
    expect(result.current.deployments[1].status).toBe('building')
    expect(result.current.deployments[2].status).toBe('failed')
    expect(result.current.deployments[3].status).toBe('paused')
  })
})