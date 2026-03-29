import { vi } from 'vitest'
import { act } from '@testing-library/react'

// Mock implementation of zustand store
const storeResetFns = new Set<() => void>()

// Mock create function
export const create = vi.fn((createState: any) => {
  let state: any
  const setState = vi.fn((partial: any, replace?: boolean) => {
    const nextState = typeof partial === 'function' ? partial(state) : partial
    state = replace ? nextState : { ...state, ...nextState }
  })
  
  const getState = vi.fn(() => state)
  const subscribe = vi.fn()
  const destroy = vi.fn()
  
  const store = (selector?: any, equalityFn?: any) => {
    if (!selector) return state
    return selector(state)
  }
  
  // Initialize state
  state = createState(setState, getState, store)
  
  // Add reset functionality for testing
  const reset = () => {
    state = createState(setState, getState, store)
  }
  
  storeResetFns.add(reset)
  
  Object.assign(store, {
    setState,
    getState,
    subscribe,
    destroy,
    reset,
  })
  
  return store
})

// Reset all stores between tests
export const resetAllStores = () => {
  act(() => {
    storeResetFns.forEach((resetFn) => {
      resetFn()
    })
  })
}

// Mock subscribeWithSelector
export const subscribeWithSelector = vi.fn((fn: any) => fn)

// Mock devtools middleware
export const devtools = vi.fn((fn: any) => fn)

export default { create, subscribeWithSelector, devtools }
