// Auto-generated TypeScript declarations for economic_governance
// Source: generate-api-docs.py

export declare class EconomicGovernance {
  constructor();
  check_budget(tenant_id: string, cost: number): void;
  route_with_governance(tenant_id: string, options: Array<Record<(str, Any)>>): void;
  set_budget_limit(tenant_id: string, limit: number): void;
}

export declare function check_budget(tenant_id: string, cost: number): void;
export declare function route_with_governance(tenant_id: string, options: Array<Record<(str, Any)>>): void;
export declare function set_budget_limit(tenant_id: string, limit: number): void;
