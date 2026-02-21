// Auto-generated TypeScript declarations for omega_safety
// Source: generate-api-docs.py

export declare class OmegaInvariantViolation extends BaseModel {
}

export declare class OmegaSafetyGuard {
  constructor();
  is_safe(action_id: string, action_data: Record<(str, Any)>): void;
  verify_action(action_id: string, action_data: Record<(str, Any)>): void;
}

export declare function is_safe(action_id: string, action_data: Record<(str, Any)>): void;
export declare function verify_action(action_id: string, action_data: Record<(str, Any)>): void;
