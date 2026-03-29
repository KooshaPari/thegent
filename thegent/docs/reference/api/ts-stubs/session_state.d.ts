// Auto-generated TypeScript declarations for session_state
// Source: generate-api-docs.py

export declare class SessionState {
  constructor(session_id: string, session_dir: any);
  delete(): void;
  list_sessions(): void;
  load(): void;
  save(state_data: Record<string, unknown>): void;
}

export declare function delete(): void;
export declare function list_sessions(): void;
export declare function load(): void;
export declare function save(state_data: Record<string, unknown>): void;
