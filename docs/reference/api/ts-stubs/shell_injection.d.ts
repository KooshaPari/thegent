// Auto-generated TypeScript declarations for shell_injection
// Source: generate-api-docs.py

export declare class AgentReadinessDetector {
  get_agent_state(pid: number): void;
}

export declare class TmuxInjector {
  constructor(session_prefix: string);
  inject_command(session_id: string, command: string, wait_for_readiness: boolean): void;
  is_ready(session_id: string): void;
  list_agent_sessions(): void;
  wait_for_ready(session_id: string, timeout: number): void;
}

export declare function get_agent_state(pid: number): void;
export declare function inject_command(session_id: string, command: string, wait_for_readiness: boolean): void;
export declare function is_ready(session_id: string): void;
export declare function list_agent_sessions(): void;
export declare function wait_for_ready(session_id: string, timeout: number): void;
