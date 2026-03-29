// Auto-generated TypeScript declarations for breaker
// Source: generate-api-docs.py

export declare class BreakerSubcommands {
  constructor();
  check(breaker_id: string): void;
  record(breaker_id: string, success: boolean): void;
  reset(breaker_id: string): void;
}

export declare function check(breaker_id: string): void;
export declare function record(breaker_id: string, success: boolean): void;
export declare function reset(breaker_id: string): void;
