import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { vi } from 'vitest'

// Mock React.act for React 19 compatibility
const mockAct = (callback: () => void) => {
  callback()
  return Promise.resolve()
}

// Override React.act if not available
if (typeof React.act === 'undefined') {
  // @ts-ignore
  React.act = mockAct
}

// Custom render function that handles React 19 compatibility
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  // Wrap the component to ensure React.act is available
  const Wrapper = ({ children }: { children: React.ReactNode }) => {
    return <>{children}</>
  }

  return render(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { customRender as render }

// Export mock functions for convenience
export const mockAct = mockAct