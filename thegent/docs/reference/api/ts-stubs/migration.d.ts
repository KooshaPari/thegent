// Auto-generated TypeScript declarations for migration
// Source: generate-api-docs.py

export declare class MigrationController {
  constructor(registry: any);
  evaluate_version(contract_id: string, version: string): void;
  get_preferred_version(contract_id: string): void;
  set_canary(percentage: number): void;
  set_dual_write(enabled: boolean): void;
  should_use_new_version(run_id: string): void;
}

export declare function evaluate_version(contract_id: string, version: string): void;
export declare function get_preferred_version(contract_id: string): void;
export declare function set_canary(percentage: number): void;
export declare function set_dual_write(enabled: boolean): void;
export declare function should_use_new_version(run_id: string): void;
