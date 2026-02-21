// Auto-generated TypeScript declarations for plangent
// Source: generate-api-docs.py

export declare class Plan {
  done_ids(): void;
  failed_ids(): void;
  get_node(node_id: string): void;
  to_dict(): void;
}

export declare class PlanNode {
  is_ready(done_ids: set<string>): void;
  to_dict(): void;
}

export declare class PlangentExecutor {
  constructor(planner: any);
  execute(plan: Plan, runner: RunnerType): void;
}

export declare class PlangentPlanner {
  constructor();
  decompose(goal: string, max_depth: number): void;
  is_complete(plan: Plan): void;
  mark_done(plan: Plan, node_id: string, result: string): void;
  mark_failed(plan: Plan, node_id: string, error: string): void;
  next_ready_tasks(plan: Plan): void;
  to_work_stream_rows(plan: Plan): void;
}

export declare function decompose(goal: string, max_depth: number): void;
export declare function done_ids(): void;
export declare function execute(plan: Plan, runner: RunnerType): void;
export declare function failed_ids(): void;
export declare function get_node(node_id: string): void;
export declare function is_complete(plan: Plan): void;
export declare function is_ready(done_ids: set<string>): void;
export declare function mark_done(plan: Plan, node_id: string, result: string): void;
export declare function mark_failed(plan: Plan, node_id: string, error: string): void;
export declare function next_ready_tasks(plan: Plan): void;
export declare function to_dict(): void;
export declare function to_work_stream_rows(plan: Plan): void;
