// Auto-generated TypeScript declarations for health_check
// Source: generate-api-docs.py

export declare class HealthChecker {
  constructor();
  register_check(name: string, check_fn: callable): void;
  run_checks(): void;
}

export declare function register_check(name: string, check_fn: callable): void;
export declare function run_checks(): void;
