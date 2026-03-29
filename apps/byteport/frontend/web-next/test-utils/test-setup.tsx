import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { vi } from 'vitest'

// Mock React.act for React 19 compatibility
const mockAct = (callback: () => void) => {
  callback()
  return Promise.resolve()
}

// Override React.act globally
if (typeof React.act === 'undefined') {
  // @ts-ignore
  React.act = mockAct
}

// Mock react-dom/test-utils
vi.mock('react-dom/test-utils', () => ({
  act: mockAct,
}))

// Custom render function with providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }