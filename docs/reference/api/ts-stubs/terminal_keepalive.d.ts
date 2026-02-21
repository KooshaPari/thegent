// Auto-generated TypeScript declarations for terminal_keepalive
// Source: generate-api-docs.py

export declare class TerminalKeepalive {
  constructor(interval: number, enabled: boolean, max_failures: number);
  get_stats(): void;
  should_enable(): void;
  start(): void;
  stop(): void;
}

export declare function create_keepalive(interval: number, enabled: boolean, max_failures: number): void;
export declare function get_stats(): void;
export declare function should_enable(): void;
export declare function start(): void;
export declare function stop(): void;
