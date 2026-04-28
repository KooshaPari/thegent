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
  type: 'production',
  created_at: '2024-01-01T00:00:00Z',
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
    expect(screen.getByText('myapp.example.com')).toBeInTheDocument()
    expect(screen.getByText(/2 hours ago/)).toBeInTheDocument()
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
    
    expect(screen.getByRole('button', { name: /open menu/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /view details/i })).toBeInTheDocument()
  })

  it('should handle view logs click', async () => {
    const onViewLogs = vi.fn()
    const user = userEvent.setup()
    
    render(<DeploymentCard deployment={mockDeployment} onViewLogs={onViewLogs} />)
    
    await user.click(screen.getByRole('button', { name: /open menu/i }))
    await user.click(await screen.findByText('View Logs'))
    expect(onViewLogs).toHaveBeenCalledWith(mockDeployment.id)
  })

  it('should handle more actions click', async () => {
    const user = userEvent.setup()
    
    render(<DeploymentCard deployment={mockDeployment} />)
    
    await user.click(screen.getByRole('button', { name: /open menu/i }))
    
    // Check that dropdown menu items are visible
    expect(screen.getByText('View Logs')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
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

  it('should render deployment framework metadata when provided', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    expect(screen.getByText('Production')).toBeInTheDocument()
  })

  it('should handle custom className', () => {
    render(<DeploymentCard deployment={mockDeployment} className="custom-class" />)
    
    const card = screen.getByRole('article')
    expect(card).toHaveClass('custom-class')
  })

  it('should handle action callbacks', async () => {
    const onViewLogs = vi.fn()
    const onSettings = vi.fn()
    const onDelete = vi.fn()
    const user = userEvent.setup()
    
    render(
      <DeploymentCard 
        deployment={mockDeployment}
        onViewLogs={onViewLogs}
        onSettings={onSettings}
        onDelete={onDelete}
      />
    )
    
    // Open dropdown menu
    await user.click(screen.getByRole('button', { name: /open menu/i }))
    
    await user.click(screen.getByText('View Logs'))
    expect(onViewLogs).toHaveBeenCalledWith(mockDeployment.id)
    
    await user.click(screen.getByRole('button', { name: /open menu/i }))
    await user.click(screen.getByText('Settings'))
    expect(onSettings).toHaveBeenCalledWith(mockDeployment.id)
    
    await user.click(screen.getByRole('button', { name: /open menu/i }))
    await user.click(screen.getByText('Delete'))
    expect(onDelete).toHaveBeenCalledWith(mockDeployment.id)
  })

  it('should render external link when URL is available', () => {
    render(<DeploymentCard deployment={mockDeployment} />)
    
    const externalLink = screen.getByRole('link', { name: /myapp.example.com/i })
    expect(externalLink).toBeInTheDocument()
    expect(externalLink).toHaveAttribute('href', 'https://myapp.example.com')
    expect(externalLink).toHaveAttribute('target', '_blank')
  })

  it('should render view details action', () => {
    const onView = vi.fn()
    render(<DeploymentCard deployment={mockDeployment} onView={onView} />)
    
    expect(screen.getByRole('button', { name: /view details/i })).toBeInTheDocument()
  })
})
