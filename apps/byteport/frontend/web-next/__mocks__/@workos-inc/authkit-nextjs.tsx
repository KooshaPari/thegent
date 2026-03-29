import { vi } from 'vitest'

// Mock WorkOS AuthKit for testing
export const getUser = vi.fn(() => ({
  id: 'user_test_123',
  email: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
}))

export const withAuth = vi.fn((component: any) => component)

export const AuthKitProvider = vi.fn(({ children }: any) => children)

export const useAuth = vi.fn(() => ({
  user: {
    id: 'user_test_123',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
  },
  isLoading: false,
  signUp: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}))

export const SignIn = vi.fn(() => <div data-testid="signin">Sign In Component</div>)
export const SignUp = vi.fn(() => <div data-testid="signup">Sign Up Component</div>)