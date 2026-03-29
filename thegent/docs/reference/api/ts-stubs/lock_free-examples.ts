// Auto-generated usage examples for lock_free
// Source: generate-api-docs.py

import { AtomicState, LockFreeStateManager, compare_and_swap, get_state, set_state } from "./lock_free";

// Create a AtomicState instance
const atomicstate = new AtomicState();

// Create a LockFreeStateManager instance
const lockfreestatemanager = new LockFreeStateManager();
lockfreestatemanager.compare_and_swap("example_key", 0, undefined as unknown as any);
lockfreestatemanager.get_state("example_key");
lockfreestatemanager.set_state("example_key", undefined as unknown as any);

// Call compare_and_swap
compare_and_swap(undefined as unknown as any, "example_key", 0, undefined as unknown as any);
// Call get_state
get_state(undefined as unknown as any, "example_key");
// Call set_state
set_state(undefined as unknown as any, "example_key", undefined as unknown as any);
