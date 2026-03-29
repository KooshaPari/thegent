// Auto-generated TypeScript declarations for subprocess_manager
// Source: generate-api-docs.py

export declare class SubprocessManager {
  constructor();
  popen(args: Array<string>, name: string): void;
  run(args: Array<string>, name: string, timeout: any): void;
}

export declare function get_subprocess_manager(): void;
export declare function popen(args: Array<string>, name: string): void;
export declare function run(args: Array<string>, name: string, timeout: any): void;
