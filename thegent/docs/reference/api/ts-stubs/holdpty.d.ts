// Auto-generated TypeScript declarations for holdpty
// Source: generate-api-docs.py

export declare class PTYHolder {
  constructor(socket_path: string, cmd: Array<string>, cwd: any, env: any);
  start(): void;
  stop(): void;
}

export declare function start(): void;
export declare function stop(): void;
export declare function wrap_with_holdpty(cmd: Array<string>, session_id: string, socket_path: string): void;
