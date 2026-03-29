import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

// Very simple component for testing
const SimpleComponent = ({ text }: { text: string }) => {
  return <div data-testid="simple-component">{text}</div>
}

describe('Simple Component', () => {
  it('should render with text', () => {
    render(<SimpleComponent text="Hello World" />)
    expect(screen.getByTestId('simple-component')).toBeInTheDocument()
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })

  it('should render with different text', () => {
    const { rerender } = render(<SimpleComponent text="First Text" />)
    expect(screen.getByText('First Text')).toBeInTheDocument()

    rerender(<SimpleComponent text="Second Text" />)
    expect(screen.getByText('Second Text')).toBeInTheDocument()
    expect(screen.queryByText('First Text')).not.toBeInTheDocument()
  })

  it('should render with empty text', () => {
    render(<SimpleComponent text="" />)
    expect(screen.getByTestId('simple-component')).toBeInTheDocument()
    expect(screen.getByTestId('simple-component')).toHaveTextContent('')
  })
})