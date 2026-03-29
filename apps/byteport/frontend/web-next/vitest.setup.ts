import React from 'react'
import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

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

// Setup MSW (Mock Service Worker) if available
let server: any
try {
  const { server: mswServer } = await import('./test/mocks/server')
  server = mswServer
  
  beforeAll(() => {
    server.listen({
      onUnhandledRequest: 'error',
    })
  })

  afterEach(() => {
    // Clean up React Testing Library
    cleanup()
    
    // Reset MSW handlers
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })
} catch (error) {
  // MSW not available, continue without it
  console.warn('MSW not available, continuing without mock server')
}

// Suppress console.error during tests unless explicitly needed
const originalConsoleError = console.error
beforeAll(() => {
  console.error = (...args) => {
    // Allow specific error patterns that we want to see
    const message = args[0]
    if (
      typeof message === 'string' &&
      (message.includes('Warning:') ||
        message.includes('Error:') ||
        message.includes('ReactDOMTestUtils'))
    ) {
      return
    }
    originalConsoleError(...args)
  }
})

afterAll(() => {
  console.error = originalConsoleError
})

// Mock window.matchMedia (required for many UI libraries)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock fetch globally
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
})