import { vi } from 'vitest'

// Mock devtools middleware - just passes through the state creator
export const devtools = vi.fn((fn: any) => fn)

// Mock persist middleware
export const persist = vi.fn((fn: any) => fn)

// Mock subscribeWithSelector
export const subscribeWithSelector = vi.fn((fn: any) => fn)

export default { devtools, persist, subscribeWithSelector }
