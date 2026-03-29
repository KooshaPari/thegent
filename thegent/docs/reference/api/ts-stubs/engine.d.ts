// Auto-generated TypeScript declarations for engine
// Source: generate-api-docs.py

export declare class ExecutionEngine {
  constructor(settings: any);
  execute(runner: AgentRunner, run_meta: RunMeta, cwd: any, mode: string, timeout: number): void;
}

export declare function execute(runner: AgentRunner, run_meta: RunMeta, cwd: any, mode: string, timeout: number): void;
