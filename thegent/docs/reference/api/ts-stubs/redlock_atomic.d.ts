// Auto-generated TypeScript declarations for redlock_atomic
// Source: generate-api-docs.py

export declare class RedlockAcquireResult {
}

export declare class RedlockController {
  constructor(key: string, ttl_ms: number);
  acquire(): void;
  extend(lock_id: string, ttl_ms: number): void;
  is_available(): void;
  is_locked(): void;
  release(lock_id: string): void;
}

export declare class _InMemoryLockState {
  acquire(lock_id: string, ttl_ms: number): void;
  extend(lock_id: string, ttl_ms: number): void;
  is_locked(): void;
  release(lock_id: string): void;
}

export declare function acquire(): void;
export declare function extend(lock_id: string, ttl_ms: number): void;
export declare function is_available(): void;
export declare function is_locked(): void;
export declare function make_redlock_controller(key: string): void;
export declare function release(lock_id: string): void;
