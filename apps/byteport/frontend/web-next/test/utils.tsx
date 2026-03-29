import React from 'react'
import { render as rtlRender, RenderOptions } from '@testing-library/react'
import { ThemeProvider } from 'next-themes'

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialTheme?: string
  // Add other provider props as needed
}

function CustomWrapper({ 
  children, 
  initialTheme = 'light' 
}: { 
  children: React.ReactNode
  initialTheme?: string 
}) {
  return (
    <ThemeProvider 
      attribute="class" 
      defaultTheme={initialTheme}
      enableSystem={false}
      disableTransitionOnChange
    >
      {children}
    </ThemeProvider>
  )
}

export function render(
  ui: React.ReactElement,
  { initialTheme, ...options }: CustomRenderOptions = {}
) {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <CustomWrapper initialTheme={initialTheme}>
      {children}
    </CustomWrapper>
  )

  return rtlRender(ui, { wrapper: Wrapper, ...options })
}

// Mock data factories
const defaultMockDeployment = {
  id: 'dep_test_123',
  name: 'My App',
  status: 'deployed' as const,
  url: 'https://test-app.vercel.app',
  provider: 'vercel',
  type: 'frontend' as const,
  framework: 'Next.js',
  runtime: 'Node 18',
  created_at: '2024-01-10T12:00:00Z',
  updated_at: '2024-01-10T12:05:00Z',
  error_message: undefined,
}

export const mockDeployment = (overrides: Partial<typeof defaultMockDeployment> = {}) => ({
  ...defaultMockDeployment,
  ...overrides,
  id: overrides.id || `dep_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
})

export const mockUser = {
  id: 'user_test_123',
  email: 'test@example.com',
  name: 'Test User',
}

export const mockDeployRequest = (overrides: any = {}) => ({
  name: 'New App',
  type: 'frontend' as const,
  provider: 'vercel' as const,
  git_url: 'https://github.com/user/repo',
  branch: 'main',
  env_vars: {},
  ...overrides,
})

export const createMockDeployment = mockDeployment

export const createMockUser = (overrides = {}) => ({
  ...mockUser,
  ...overrides,
  id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
})

// Test helpers
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))

// Mock fetch for components that might make direct API calls
export const mockFetch = (response: any, status = 200) => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(response),
      text: () => Promise.resolve(JSON.stringify(response)),
    })
  ) as any
}

// Reset mocks between tests
export const resetMocks = () => {
  vi.clearAllMocks()
  if (global.fetch && vi.isMockFunction(global.fetch)) {
    global.fetch.mockClear()
  }
}

// Re-export everything from React Testing Library
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'