// Auto-generated TypeScript declarations for breakers
// Source: generate-api-docs.py

export declare class CircuitBreaker {
  constructor(session_dir: string);
  check_spike(current_batch_cost: number): void;
  is_tripped(): void;
  trip(reason: string, value: number): void;
}

export declare function check_spike(current_batch_cost: number): void;
export declare function is_tripped(): void;
export declare function trip(reason: string, value: number): void;
