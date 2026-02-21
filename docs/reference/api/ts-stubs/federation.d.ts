// Auto-generated TypeScript declarations for federation
// Source: generate-api-docs.py

export declare class FederatedPolicyManager {
  constructor(base_dir: string);
  apply_jurisdiction_constraints(policy: Record<(str, Any)>, region: string): void;
  arbitrate_conflict(policies: Array<Record<(str, Any)>>): void;
  get_federation_health(): void;
  join_namespace(ns_str: string): void;
  leave_namespace(ns_str: string): void;
  relay_consent(ns1: PolicyNamespace, ns2: PolicyNamespace, run_id: string, approver: string): void;
  resolve_policy(ns: PolicyNamespace, policy_id: string): void;
}

export declare class FederationManager {
  constructor(session_dir: string);
  get_effective_policy(policy_id: string): void;
  sync_policies(peer_id: string): void;
}

export declare class PolicyNamespace {
  constructor(org: string, project: string, environment: string);
  get_hierarchy(): void;
}

export declare function apply_jurisdiction_constraints(policy: Record<(str, Any)>, region: string): void;
export declare function arbitrate_conflict(policies: Array<Record<(str, Any)>>): void;
export declare function get_effective_policy(policy_id: string): void;
export declare function get_federation_health(): void;
export declare function get_hierarchy(): void;
export declare function join_namespace(ns_str: string): void;
export declare function leave_namespace(ns_str: string): void;
export declare function relay_consent(ns1: PolicyNamespace, ns2: PolicyNamespace, run_id: string, approver: string): void;
export declare function resolve_policy(ns: PolicyNamespace, policy_id: string): void;
export declare function sync_policies(peer_id: string): void;
