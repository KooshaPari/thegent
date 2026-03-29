// Auto-generated TypeScript declarations for dag_prioritization
// Source: generate-api-docs.py

export declare class DagCycleError extends Exception {
}

export declare class DagPrioritizer {
  constructor();
  add_task(task: DagTask): void;
  compute_critical_path(): void;
  get_priority_score(task_id: string): void;
  ready_tasks(completed: set<string>): void;
  topological_sort(): void;
}

export declare class DagTask {
}

export declare function add_task(task: DagTask): void;
export declare function compute_critical_path(): void;
export declare function get_priority_score(task_id: string): void;
export declare function ready_tasks(completed: set<string>): void;
export declare function topological_sort(): void;
