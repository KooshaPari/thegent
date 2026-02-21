// Auto-generated TypeScript declarations for policy_federation
// Source: generate-api-docs.py

export declare class FederatedPolicyEngine {
  constructor(namespace: string);
  evaluate(tenant_id: string, action: string, context: Record<(str, Any)>): void;
  get_federation_status(): void;
  get_policy(key: string): void;
  is_allowed(action: string, context: Record<(str, Any)>): void;
  register_tenant(tenant_id: string, policy: Record<(str, Any)>): void;
  resolve_policy(namespace: string, policy_key: string): void;
  set_policy(key: string, value: any): void;
}

export declare class PolicyConflictResolver {
  resolve(policies: Array<Record<(str, Any)>>, target_namespace: string): void;
}

export declare function evaluate(tenant_id: string, action: string, context: Record<(str, Any)>): void;
export declare function get_federation_status(): void;
export declare function get_policy(key: string): void;
export declare function is_allowed(action: string, context: Record<(str, Any)>): void;
export declare function register_tenant(tenant_id: string, policy: Record<(str, Any)>): void;
export declare function resolve(policies: Array<Record<(str, Any)>>, target_namespace: string): void;
export declare function resolve_policy(namespace: string, policy_key: string): void;
export declare function set_policy(key: string, value: any): void;
export declare function specificity(p: Record<(str, Any)>): number;
