// Auto-generated TypeScript declarations for router
// Source: generate-api-docs.py

export declare class DependencyRouter {
  constructor(dag: Mapping<(str, Iterable<str])>>);
  from_tasks(tasks: Array<Record<(str, Any)>>): void;
  get_ready_tasks(): void;
  is_finished(): void;
  mark_completed(task_id: string): void;
  mark_started(task_id: string): void;
}

export declare function from_tasks(tasks: Array<Record<(str, Any)>>): void;
export declare function get_ready_tasks(): void;
export declare function is_finished(): void;
export declare function mark_completed(task_id: string): void;
export declare function mark_started(task_id: string): void;
