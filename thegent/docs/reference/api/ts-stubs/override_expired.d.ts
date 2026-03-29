// Auto-generated TypeScript declarations for override_expired
// Source: generate-api-docs.py

export declare class OverrideExpirationHandler {
  constructor();
  check_expired(): void;
  emit_expired_event(override: Record<(str, Any)>): void;
  register_override(override_id: string, expires_at: datetime, policy: string): void;
}

export declare function check_expired(): void;
export declare function emit_expired_event(override: Record<(str, Any)>): void;
export declare function register_override(override_id: string, expires_at: datetime, policy: string): void;
