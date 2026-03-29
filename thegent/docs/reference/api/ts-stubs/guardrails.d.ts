// Auto-generated TypeScript declarations for guardrails
// Source: generate-api-docs.py

export declare class CommandValidator {
  sanitize_path(path: string): void;
  validate_command(cmd: any): void;
}

export declare class Guardrails {
  constructor();
  check_invariant(invariant_name: string, value: any): void;
  optimize_context(context: string, max_tokens: any): void;
  validate_and_sanitize_command(cmd: any, operation_type: string): void;
}

export declare class RateLimit {
  check(): void;
  reset(): void;
}

export declare class RateLimiter {
  constructor();
  add_limit(key: string, max_calls: number, window_seconds: number): void;
  check(key: string): void;
  reset(key: string): void;
}

export declare class SecretManager {
  get_secret(name: string, default: any): void;
  mask_secret(value: string): void;
  validate_secret_present(name: string): void;
}

export declare class SecurityInvariant {
}

export declare class TokenOptimizer {
  compress_context(context: string, max_tokens: number): void;
  estimate_tokens(text: string): void;
  optimize_prompt(prompt: string, max_tokens: any): void;
  remove_secrets(text: string): void;
}

export declare function add_limit(key: string, max_calls: number, window_seconds: number): void;
export declare function check(key: string): void;
export declare function check_invariant(invariant_name: string, value: any): void;
export declare function check_rate_limit(operation_type: string): void;
export declare function compress_context(context: string, max_tokens: number): void;
export declare function estimate_tokens(text: string): void;
export declare function get_secret(name: string, default: any): void;
export declare function mask_secret(value: string): void;
export declare function optimize_context(context: string, max_tokens: any): void;
export declare function optimize_prompt(prompt: string, max_tokens: any): void;
export declare function remove_secrets(text: string): void;
export declare function reset(key: string): void;
export declare function sanitize_path(path: string): void;
export declare function validate_and_sanitize_command(cmd: any, operation_type: string): void;
export declare function validate_command(cmd: any): void;
export declare function validate_secret_present(name: string): void;
