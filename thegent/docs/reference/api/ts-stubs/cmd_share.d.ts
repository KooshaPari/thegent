// Auto-generated TypeScript declarations for cmd_share
// Source: generate-api-docs.py

export declare class CommandSharer {
  constructor(session_dir: string);
  execute_shared(command: Array<string>, cwd: string, env: any): void;
}

export declare function execute_shared(command: Array<string>, cwd: string, env: any): void;
