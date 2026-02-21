// Auto-generated TypeScript declarations for storage
// Source: generate-api-docs.py

export declare class PromptQueue {
  constructor(session_dir: string);
  append(prompt: string, project: string, agent: any): void;
  claim(claimer_id: string, lease_seconds: number, project: any): void;
  done(item_id: number): void;
  edit(item_id: number, prompt: string): void;
  extend_lease(item_id: number, lease_seconds: number): void;
  get_pending_count(): void;
  list_all(include_done: boolean, include_expired: boolean, limit: any): void;
  list_pending(): void;
  release(item_id: number): void;
}

export declare function append(prompt: string, project: string, agent: any): void;
export declare function claim(claimer_id: string, lease_seconds: number, project: any): void;
export declare function done(item_id: number): void;
export declare function edit(item_id: number, prompt: string): void;
export declare function extend_lease(item_id: number, lease_seconds: number): void;
export declare function get_pending_count(): void;
export declare function list_all(include_done: boolean, include_expired: boolean, limit: any): void;
export declare function list_pending(): void;
export declare function release(item_id: number): void;
