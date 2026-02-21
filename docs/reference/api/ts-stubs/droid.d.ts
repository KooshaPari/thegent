// Auto-generated TypeScript declarations for droid
// Source: generate-api-docs.py

export declare class CodexRunner extends AgentRunner {
  constructor(droid_name: string, droids_dir: string, codex_cmd: string, model: string, use_litellm_router: any);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare class CustomCliRunner extends AgentRunner {
  constructor(droid_name: string, droids_dir: string, custom_cmd: string, model: string);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare class DroidRunner extends AgentRunner {
  constructor(droid_name: string, droids_dir: string, droid_cmd: string, model: string, use_litellm_router: any);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function get_droid_runner(backend: string, droid_name: string, droids_dir: string): void;
export declare function run(prompt: string, cwd: any, mode: string, timeout: number): void;
