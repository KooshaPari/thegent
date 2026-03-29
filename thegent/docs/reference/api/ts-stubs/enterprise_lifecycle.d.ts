// Auto-generated TypeScript declarations for enterprise_lifecycle
// Source: generate-api-docs.py

export declare class EnterpriseLifecycleManager {
  constructor();
  get_lifecycle_map(): void;
  get_stage_compliance(stage: string): void;
  register_compliance_check(stage: string, check: string): void;
}

export declare function get_lifecycle_map(): void;
export declare function get_stage_compliance(stage: string): void;
export declare function register_compliance_check(stage: string, check: string): void;
