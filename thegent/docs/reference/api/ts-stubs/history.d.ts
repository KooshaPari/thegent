// Auto-generated TypeScript declarations for history
// Source: generate-api-docs.py

export declare class ContextHistory {
  constructor(db_path: any);
  get_task_sequence(task_id: string): void;
  record(entry: HistoryEntry): void;
  search(query: any, task_id: any, cwd: any, limit: number): void;
}

export declare class HistoryEntry extends BaseModel {
}

export declare function get_task_sequence(task_id: string): void;
export declare function record(entry: HistoryEntry): void;
export declare function search(query: any, task_id: any, cwd: any, limit: number): void;
