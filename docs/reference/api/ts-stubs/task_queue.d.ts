// Auto-generated TypeScript declarations for task_queue
// Source: generate-api-docs.py

export declare class MaildirQueue {
  constructor(path: string);
  ack(task_id: string): void;
  dequeue(): void;
  enqueue(task: Record<(str, Any)>, priority: number): void;
  list_pending(): void;
  nack(task_id: string): void;
}

export declare function ack(task_id: string): void;
export declare function dequeue(): void;
export declare function enqueue(task: Record<(str, Any)>, priority: number): void;
export declare function list_pending(): void;
export declare function nack(task_id: string): void;
