import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// Test that our setup is working
describe('Test Setup', () => {
  it('should render a simple component', () => {
    const TestComponent = () => <div>Test Component</div>
    render(<TestComponent />)
    expect(screen.getByText('Test Component')).toBeInTheDocument()
  })

  it('should have React.act available', () => {
    expect(typeof React.act).toBe('function')
  })

  it('should have vi available', () => {
    expect(typeof vi.fn).toBe('function')
  })
})