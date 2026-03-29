import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Simple button component for testing
const SimpleButton = ({ 
  children, 
  onClick, 
  disabled = false, 
  className = '' 
}: {
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  className?: string
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      data-testid="simple-button"
    >
      {children}
    </button>
  )
}

describe('SimpleButton Component', () => {
  it('should render with children', () => {
    render(<SimpleButton>Click me</SimpleButton>)
    expect(screen.getByTestId('simple-button')).toBeInTheDocument()
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('should handle click events', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<SimpleButton onClick={handleClick}>Click me</SimpleButton>)
    
    await user.click(screen.getByTestId('simple-button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when disabled prop is true', () => {
    render(<SimpleButton disabled>Disabled</SimpleButton>)
    expect(screen.getByTestId('simple-button')).toBeDisabled()
  })

  it('should not call onClick when disabled', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<SimpleButton disabled onClick={handleClick}>Disabled</SimpleButton>)
    
    await user.click(screen.getByTestId('simple-button'))
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('should accept custom className', () => {
    render(<SimpleButton className="custom-class">Custom</SimpleButton>)
    expect(screen.getByTestId('simple-button')).toHaveClass('custom-class')
  })

  it('should handle keyboard events', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<SimpleButton onClick={handleClick}>Click me</SimpleButton>)
    
    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    await user.keyboard(' ')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })

  it('should have proper accessibility attributes', () => {
    render(<SimpleButton aria-label="Custom label">Button</SimpleButton>)
    expect(screen.getByTestId('simple-button')).toHaveAttribute('aria-label', 'Custom label')
  })

  it('should handle focus events', async () => {
    const handleFocus = vi.fn()
    const handleBlur = vi.fn()
    const user = userEvent.setup()
    
    render(
      <SimpleButton onFocus={handleFocus} onBlur={handleBlur}>
        Focus me
      </SimpleButton>
    )
    
    await user.tab()
    expect(handleFocus).toHaveBeenCalledTimes(1)
    
    await user.tab()
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })
})