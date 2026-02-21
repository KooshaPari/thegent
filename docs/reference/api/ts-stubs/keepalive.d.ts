// Auto-generated TypeScript declarations for keepalive
// Source: generate-api-docs.py

export declare class KeepaliveConfig {
}

export declare class TerminalKeepalive {
  constructor(config: any);
  start(): void;
  stop(): void;
}

export declare function keepalive(interval_s: number, message: string): void;
export declare function start(): void;
export declare function stop(): void;
