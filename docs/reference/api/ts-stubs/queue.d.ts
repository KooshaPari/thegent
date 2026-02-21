// Auto-generated TypeScript declarations for queue
// Source: generate-api-docs.py

export declare class TaskQueue {
  constructor();
  complete(task_id: string): void;
  dequeue(): void;
  enqueue(task_id: string, task: Record<(str, Any)>): void;
}

export declare function complete(task_id: string): void;
export declare function dequeue(): void;
export declare function enqueue(task_id: string, task: Record<(str, Any)>): void;
