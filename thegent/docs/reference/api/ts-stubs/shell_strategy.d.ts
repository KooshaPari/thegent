// Auto-generated TypeScript declarations for shell_strategy
// Source: generate-api-docs.py

export declare class DualShellStrategy {
  constructor();
  execute(command: string, capture_output: boolean): void;
  normalize_path(path: string): void;
}

export declare function execute(command: string, capture_output: boolean): void;
export declare function normalize_path(path: string): void;
