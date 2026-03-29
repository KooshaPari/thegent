// Auto-generated TypeScript declarations for codex_proxy
// Source: generate-api-docs.py

export declare class CodexProxyRunner extends AgentRunner {
  constructor(agent_name: string, settings: any, model: string, use_litellm_router: any);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
  run_with_metadata(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
export declare function run_with_metadata(prompt: string, cwd: any, mode: string, timeout: number): void;
