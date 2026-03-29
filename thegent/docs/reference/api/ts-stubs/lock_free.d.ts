// Auto-generated TypeScript declarations for lock_free
// Source: generate-api-docs.py

export declare class AtomicState {
}

export declare class LockFreeStateManager {
  constructor();
  compare_and_swap(key: string, expected_version: number, new_value: any): void;
  get_state(key: string): void;
  set_state(key: string, value: any): void;
}

export declare function compare_and_swap(key: string, expected_version: number, new_value: any): void;
export declare function get_state(key: string): void;
export declare function set_state(key: string, value: any): void;
