// Auto-generated usage examples for redlock_atomic
// Source: generate-api-docs.py

import { RedlockAcquireResult, RedlockController, _InMemoryLockState, acquire, extend, is_available, is_locked, make_redlock_controller, release } from "./redlock_atomic";

// Create a RedlockAcquireResult instance
const redlockacquireresult = new RedlockAcquireResult();

// Create a RedlockController instance
const redlockcontroller = new RedlockController("example_key", 0);
redlockcontroller.acquire();
redlockcontroller.extend("example_lock_id", 0);
redlockcontroller.is_available();
redlockcontroller.is_locked();
redlockcontroller.release("example_lock_id");

// Create a _InMemoryLockState instance
const _inmemorylockstate = new _InMemoryLockState();
_inmemorylockstate.acquire("example_lock_id", 0);
_inmemorylockstate.extend("example_lock_id", 0);
_inmemorylockstate.is_locked();
_inmemorylockstate.release("example_lock_id");

// Call acquire
acquire(undefined as unknown as any);
// Call extend
extend(undefined as unknown as any, "example_lock_id", 0);
// Call is_available
is_available(undefined as unknown as any);
// Call is_locked
is_locked(undefined as unknown as any);
// Call make_redlock_controller
make_redlock_controller("example_key");
// Call release
release(undefined as unknown as any, "example_lock_id");
