// Auto-generated TypeScript declarations for tracker
// Source: generate-api-docs.py

export declare class CostEntry {
  to_dict(): void;
}

export declare class RunCostTracker {
  constructor(cost_dir: any);
  end_run(): void;
  record_entry(entry: CostEntry): void;
  start_run(run_id: string): void;
}

export declare function end_run(): void;
export declare function get_run_cost_tracker(): void;
export declare function record_entry(entry: CostEntry): void;
export declare function start_run(run_id: string): void;
export declare function to_dict(): void;
