// Auto-generated TypeScript declarations for headless_manager
// Source: generate-api-docs.py

export declare class HeadlessLSPManager {
  constructor(cache_dir: any);
  ensure_server(language: string, auto_install: any): void;
  list_servers(): void;
  stop_all(): void;
  stop_server(language: string): void;
}

export declare class HeadlessLSPServer {
  constructor(language: string, config: Record<(str, Any)>);
  is_running(): void;
  start(): void;
  stop(): void;
}

export declare function ensure_server(language: string, auto_install: any): void;
export declare function is_running(): void;
export declare function list_servers(): void;
export declare function start(): void;
export declare function stop(): void;
export declare function stop_all(): void;
export declare function stop_server(language: string): void;
