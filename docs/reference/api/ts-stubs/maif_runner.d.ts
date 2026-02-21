// Auto-generated TypeScript declarations for maif_runner
// Source: generate-api-docs.py

export declare class MAIFAgentRunner extends AgentRunner {
  constructor(runner: AgentRunner, engine: ExecutionEngine | null);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): void;
