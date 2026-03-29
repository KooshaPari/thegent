// Auto-generated TypeScript declarations for backlog
// Source: generate-api-docs.py

export declare class BacklogItem extends BaseModel {
}

export declare class BacklogManager {
  constructor(session_dir: string);
  add(finding_id: string, dimension: string, severity: number, description: string): void;
  backlog_path(): void;
  defer(item_id: string, reason: string): void;
  get_all(): void;
  get_pending(): void;
  increment_attempt(item_id: string): void;
  resolve(item_id: string): void;
  update_status(item_id: string, status: BacklogStatus, reason: any): void;
}

export declare class BacklogStatus extends StrEnum {
}

export declare function add(finding_id: string, dimension: string, severity: number, description: string): void;
export declare function backlog_path(): string;
export declare function defer(item_id: string, reason: string): void;
export declare function get_all(): void;
export declare function get_pending(): void;
export declare function increment_attempt(item_id: string): void;
export declare function resolve(item_id: string): void;
export declare function update_status(item_id: string, status: BacklogStatus, reason: any): void;
