// Auto-generated TypeScript declarations for overrides
// Source: generate-api-docs.py

export declare class OverrideManager {
  constructor(settings: any);
  apply_override(policy_id: string, reason: string, by: string, duration_minutes: number, metadata: any): void;
  cleanup_expired(): void;
  get_override(policy_id: string): void;
}

export declare class PolicyOverride {
  from_dict(data: Record<(str, Any)>): void;
  is_active(): void;
  to_dict(): void;
}

export declare function apply_override(policy_id: string, reason: string, by: string, duration_minutes: number, metadata: any): void;
export declare function cleanup_expired(): void;
export declare function from_dict(data: Record<(str, Any)>): void;
export declare function get_override(policy_id: string): void;
export declare function is_active(): void;
export declare function to_dict(): void;
