// Auto-generated TypeScript declarations for zmx_session
// Source: generate-api-docs.py

export declare class ZmxSessionConfig {
  from_env(): void;
  from_settings(): void;
}

export declare class ZmxSessionManager {
  constructor(config: any);
  attach_session(session_name: string): void;
  capture_output(session_name: string, lines: number): void;
  create_session(session_id: string, command: Array<string>): void;
  destroy_session(session_name: string): void;
  is_available(): void;
  list_sessions(): void;
  send_input(session_name: string, text: string): void;
}

export declare function attach_session(session_name: string): void;
export declare function capture_output(session_name: string, lines: number): void;
export declare function create_session(session_id: string, command: Array<string>): void;
export declare function destroy_session(session_name: string): void;
export declare function from_env(): void;
export declare function from_settings(): void;
export declare function is_available(): void;
export declare function list_sessions(): void;
export declare function make_zmx_session_manager(config: any): void;
export declare function send_input(session_name: string, text: string): void;
