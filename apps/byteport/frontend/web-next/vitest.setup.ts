import React from 'react'
import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from './test/mocks/server'

vi.stubGlobal('server', server)
vi.stubGlobal('http', http)
vi.stubGlobal('HttpResponse', HttpResponse)
vi.stubGlobal('API_BASE_URL', 'http://localhost:8080')

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

beforeAll(() => {
  server.listen({
    onUnhandledRequest: 'bypass',
  })
})

afterEach(() => {
  cleanup()
  server.resetHandlers()
})

afterAll(() => {
  server.close()
})

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
class MockResizeObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}

global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver
window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver

// Radix Select expects pointer-capture APIs that jsdom does not implement.
if (!HTMLElement.prototype.hasPointerCapture) {
  HTMLElement.prototype.hasPointerCapture = vi.fn(() => false)
}
if (!HTMLElement.prototype.setPointerCapture) {
  HTMLElement.prototype.setPointerCapture = vi.fn()
}
if (!HTMLElement.prototype.releasePointerCapture) {
  HTMLElement.prototype.releasePointerCapture = vi.fn()
}
if (!HTMLElement.prototype.scrollIntoView) {
  HTMLElement.prototype.scrollIntoView = vi.fn()
}

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
