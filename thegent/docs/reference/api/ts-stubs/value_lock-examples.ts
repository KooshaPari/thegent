// Auto-generated usage examples for value_lock
// Source: generate-api-docs.py

import { LockedPrinciple, ValueLock, lock_principle, validate_change } from "./value_lock";

// Create a LockedPrinciple instance
const lockedprinciple = new LockedPrinciple();

// Create a ValueLock instance
const valuelock = new ValueLock("example_lock_path");
valuelock.lock_principle("example_principle_id", "example_description");
valuelock.validate_change("example_principle_id", "example_new_description");

// Call lock_principle
lock_principle(undefined as unknown as any, "example_principle_id", "example_description");
// Call validate_change
validate_change(undefined as unknown as any, "example_principle_id", "example_new_description");
