// Auto-generated TypeScript declarations for acp_server
// Source: generate-api-docs.py

export declare class ACPServerAdapter {
  constructor(session_endpoints: any);
  build_starlette_app(): void;
  run_http(host: string, port: number): void;
}

export declare class AgentSession {
  constructor(session_id: string, runner: AgentRunner, cwd: any);
  add_message(role: string, content: string): void;
  stop(): void;
}

export declare class SessionEndpoints {
  constructor(backend: any);
  attach(session_name: string): void;
  get_or_resolve_backend(): void;
  inspect(session_id: string, last_lines: number): void;
  send(session_id: string, text: string): void;
}

export declare function add_message(role: string, content: string): void;
export declare function attach(session_name: string): void;
export declare function build_starlette_app(): void;
export declare function cli(http: boolean, host: string, port: number, log_level: string): void;
export declare function get_or_resolve_backend(): void;
export declare function inspect(session_id: string, last_lines: number): void;
export declare function main(): void;
export declare function run_http(host: string, port: number): void;
export declare function send(session_id: string, text: string): void;
export declare function stop(): void;
