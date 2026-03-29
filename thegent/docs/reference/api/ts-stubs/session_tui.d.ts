// Auto-generated TypeScript declarations for session_tui
// Source: generate-api-docs.py

export declare class SessionTUI {
  constructor(session_id: any);
  manage_session(session_id: string, action: string): void;
  render_session_view(session_id: string): void;
  render_sessions_list(): void;
  show(session_id: any): void;
  watch(session_id: any, interval: number): void;
}

export declare function manage_session(session_id: string, action: string): void;
export declare function render_session_view(session_id: string): void;
export declare function render_sessions_list(): void;
export declare function show(session_id: any): void;
export declare function watch(session_id: any, interval: number): void;
