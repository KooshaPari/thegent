// Auto-generated TypeScript declarations for teammate_runner
// Source: generate-api-docs.py

export declare class TeammateRunner extends AgentRunner {
  constructor(teammate_id: string, settings: any);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
