// Auto-generated TypeScript declarations for federated_policy
// Source: generate-api-docs.py

export declare class FederatedPolicyEngine {
  constructor(default_namespace: string);
  evaluate(namespace: string, context: Record<(str, Any)>): void;
  load_from_file(path: string, namespace: string): void;
  merge(other: FederatedPolicyEngine): void;
  register(rule: PolicyRule): void;
  resolve_policies(namespace: string): void;
}

export declare class PolicyRule {
  create(rule_id: string, scope: PolicyScope, condition: string, action: string, priority: number, namespace: string): void;
}

export declare class PolicyScope extends Enum {
}

export declare function create(rule_id: string, scope: PolicyScope, condition: string, action: string, priority: number, namespace: string): void;
export declare function evaluate(namespace: string, context: Record<(str, Any)>): void;
export declare function load_from_file(path: string, namespace: string): void;
export declare function merge(other: FederatedPolicyEngine): void;
export declare function register(rule: PolicyRule): void;
export declare function resolve_policies(namespace: string): void;
