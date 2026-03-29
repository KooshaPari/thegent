// Auto-generated TypeScript declarations for task_registry
// Source: generate-api-docs.py

export declare class AsyncTaskRegistry {
  constructor();
  cancel(task_id: string): {"task_id";
  cleanup(max_age_s: number): void;
  create(task: asyncio.Task<any>, task_id: any): void;
  list_tasks(): void;
  status(task_id: string): void;
  update_progress(task_id: string, progress: number, total: any, message: string): void;
}

export declare class _TaskEntry {
  constructor(task_id: string, task: asyncio.Task<any>);
}

export declare function cancel(task_id: string): {"task_id";
export declare function cleanup(max_age_s: number): void;
export declare function create(task: asyncio.Task<any>, task_id: any): void;
export declare function get_task_registry(): void;
export declare function list_tasks(): void;
export declare function status(task_id: string): void;
export declare function update_progress(task_id: string, progress: number, total: any, message: string): void;
