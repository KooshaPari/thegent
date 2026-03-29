// Auto-generated TypeScript declarations for state_shm
// Source: generate-api-docs.py

export declare class CircuitBreakerShm {
  constructor(path: any, threshold: number, window_s: number, recovery_s: number);
  get_health_score(): void;
  is_native(): void;
  is_open(target: string, category: string): void;
  record_failure(target: string, category: string): void;
  record_success(target: string, category: string): void;
  set_health_score(score: number): void;
  should_allow(target: string, category: string): void;
  state_int(target: string, category: string): void;
}

export declare class XpTracker {
  constructor(path: any);
  award(amount: number): void;
  is_native(): void;
  level(): void;
  set_level(level: number): void;
  state(): void;
  total_xp(): void;
}

export declare class _PurePythonBreakerStore {
  constructor();
  clear(target: any): void;
  is_open(target: string, category: string, threshold: number, window_s: number, recovery_s: number): void;
  record_failure(target: string, category: string): void;
}

export declare class _PurePythonXpStore {
  constructor();
  award(amount: number): void;
  state(): void;
}

export declare function award(amount: number): void;
export declare function clear(target: any): void;
export declare function get_health_score(): void;
export declare function is_native(): void;
export declare function is_native_available(): void;
export declare function is_open(target: string, category: string): void;
export declare function level(): void;
export declare function open_shm(path: any): void;
export declare function record_failure(target: string, category: string): void;
export declare function record_success(target: string, category: string): void;
export declare function set_health_score(score: number): void;
export declare function set_level(level: number): void;
export declare function should_allow(target: string, category: string): void;
export declare function state(): void;
export declare function state_int(target: string, category: string): void;
export declare function total_xp(): void;
