// Auto-generated TypeScript declarations for task
// Source: generate-api-docs.py

export declare class Task {
  add_dependency(task_id: string): void;
  is_ready(completed_tasks: set<string>): void;
  mark_completed(result: any): void;
  mark_failed(error: string): void;
  mark_running(): void;
  remove_dependency(task_id: string): void;
}

export declare class TaskStatus extends StrEnum {
}

export declare function add_dependency(task_id: string): void;
export declare function is_ready(completed_tasks: set<string>): void;
export declare function mark_completed(result: any): void;
export declare function mark_failed(error: string): void;
export declare function mark_running(): void;
export declare function remove_dependency(task_id: string): void;
