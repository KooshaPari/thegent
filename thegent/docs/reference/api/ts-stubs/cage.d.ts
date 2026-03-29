// Auto-generated TypeScript declarations for cage
// Source: generate-api-docs.py

export declare class AgentCage {
  constructor(cage_id: string, base_dir: string);
  cleanup(): void;
  run_command(cmd: Array<string>): void;
  setup(allowed_files: Array<string>): void;
}

export declare function cleanup(): void;
export declare function run_command(cmd: Array<string>): void;
export declare function setup(allowed_files: Array<string>): void;
