// Auto-generated TypeScript declarations for agileplus
// Source: generate-api-docs.py

export declare class AgilePlusLoop {
  constructor(project_dir: string, health_targets_path: string, health_threshold: number, max_tasks_per_cycle: number, max_rerolls: number, lifecycle_mode: string);
  cycle_id(): void;
  get_status(): void;
  request_shutdown(): void;
  run_continuous(interval_seconds: number, max_cycles: any): void;
  run_once(force: boolean): void;
  shutdown_requested(): void;
  state(): void;
}

export declare class CycleResult extends BaseModel {
}

export declare class CycleState extends StrEnum {
}

export declare function cycle_id(): void;
export declare function get_status(): void;
export declare function request_shutdown(): void;
export declare function run_continuous(interval_seconds: number, max_cycles: any): void;
export declare function run_once(force: boolean): void;
export declare function shutdown_requested(): void;
export declare function state(): void;
