import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DeploymentCard } from '@/components/deployment-card'
import type { Deployment } from '@/lib/types'

// Mock the date-fns function
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 hours ago')
}))

// Mock the cn utility function
vi.mock('@/lib/utils', () => ({
  cn: (...classes: (string | undefined)[]) => classes.filter(Boolean).join(' ')
}))

// Mock the status indicator component
vi.mock('@/components/status-indicator', () => ({
  StatusIndicator: ({ status }: { status: string }) => (
    <div data-testid="status-indicator" data-status={status}>
      {status}
    </div>
  )
}))

// Mock the provider badge component
vi.mock('@/components/provider-badge', () => ({
  ProviderBadge: ({ provider }: { provider: string }) => (
    <div data-testid="provider-badge" data-provider={provider}>
      {provider}
    </div>
  )
}))

const mockDeployment: Deployment = {
  id: '1',
  name: 'My App',
  status: 'deployed',
  url: 'https://myapp.example.com',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T02:00:00Z',
  provider: 'vercel',
  region: 'us-east-1',
  environment: 'production',
  buildLogs: [],
  metrics: {
    cpu: 45,
    memory: 60,
    requests: 1000
  }
}

describe('DeploymentCard Component', () => {
  it('should render deployment information', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    expect(screen.getByText('My App')).toBeInTheDocument()
    expect(screen.getByText('https://myapp.example.com')).toBeInTheDocument()
    expect(screen.getByText('2 hours ago')).toBeInTheDocument()
  })

  it('should render status indicator', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    const statusIndicator = screen.getByTestId('status-indicator')
    expect(statusIndicator).toBeInTheDocument()
    expect(statusIndicator).toHaveAttribute('data-status', 'deployed')
  })

  it('should render provider badge', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    const providerBadge = screen.getByTestId('provider-badge')
    expect(providerBadge).toBeInTheDocument()
    expect(providerBadge).toHaveAttribute('data-provider', 'vercel')
  })

  it('should render action buttons', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    expect(screen.getByRole('button', { name: /view logs/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /more actions/i })).toBeInTheDocument()
  })

  it('should handle view logs click', async () => {
    const onViewLogs = vi.fn()
    const user = userEvent.setup()
    
    render(<DeploymentCard deployment={mockDeployment} onViewLogs={onViewLogs} />)
    
    await user.click(screen.getByRole('button', { name: /view logs/i }))
    expect(onViewLogs).toHaveBeenCalledWith(mockDeployment)
  })

  it('should handle more actions click', async () => {
    const user = userEvent.setup()
    
    render(<DeploymentCard deployment={mockDeployment} />)
    
    await user.click(screen.getByRole('button', { name: /more actions/i }))
    
    // Check that dropdown menu items are visible
    expect(screen.getByText('Redeploy')).toBeInTheDocument()
    expect(screen.getByText('Pause')).toBeInTheDocument()
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('should handle different deployment statuses', () => {
    const { rerender } = render(
      <DeploymentCard deployment={{ ...mockDeployment, status: 'building' }} />
    )
    
    expect(screen.getByTestId('status-indicator')).toHaveAttribute('data-status', 'building')
    
    rerender(
      <DeploymentCard deployment={{ ...mockDeployment, status: 'failed' }} />
    )
    
    expect(screen.getByTestId('status-indicator')).toHaveAttribute('data-status', 'failed')
  })

  it('should handle deployment without URL', () => {
    const deploymentWithoutUrl = { ...mockDeployment, url: null }
    render(<DeploymentCard deployment={deploymentWithoutUrl} />)
    
    expect(screen.getByText('My App')).toBeInTheDocument()
    expect(screen.queryByText('https://myapp.example.com')).not.toBeInTheDocument()
  })

  it('should render metrics when provided', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    expect(screen.getByText('CPU: 45%')).toBeInTheDocument()
    expect(screen.getByText('Memory: 60%')).toBeInTheDocument()
    expect(screen.getByText('Requests: 1000')).toBeInTheDocument()
  })

  it('should handle custom className', () => {
    render(<DeploymentCard deployment={mockDeployment} className="custom-class" />)
    
    const card = screen.getByRole('article')
    expect(card).toHaveClass('custom-class')
  })

  it('should handle action callbacks', async () => {
    const onRedeploy = vi.fn()
    const onPause = vi.fn()
    const onDelete = vi.fn()
    const user = userEvent.setup()
    
    render(
      <DeploymentCard 
        deployment={mockDeployment}
        onRedeploy={onRedeploy}
        onPause={onPause}
        onDelete={onDelete}
      />
    )
    
    // Open dropdown menu
    await user.click(screen.getByRole('button', { name: /more actions/i }))
    
    // Click redeploy
    await user.click(screen.getByText('Redeploy'))
    expect(onRedeploy).toHaveBeenCalledWith(mockDeployment)
    
    // Click pause
    await user.click(screen.getByText('Pause'))
    expect(onPause).toHaveBeenCalledWith(mockDeployment)
    
    // Click delete
    await user.click(screen.getByText('Delete'))
    expect(onDelete).toHaveBeenCalledWith(mockDeployment)
  })

  it('should render external link when URL is available', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    const externalLink = screen.getByRole('link', { name: /open in new tab/i })
    expect(externalLink).toBeInTheDocument()
    expect(externalLink).toHaveAttribute('href', 'https://myapp.example.com')
    expect(externalLink).toHaveAttribute('target', '_blank')
  })

  it('should handle loading state', () => {
    render(<DeploymentCard deployment={mockDeployment} isLoading />)
    
    // Check for loading indicators
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument()
  })
})