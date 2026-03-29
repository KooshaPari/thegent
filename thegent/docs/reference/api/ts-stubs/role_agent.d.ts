// Auto-generated TypeScript declarations for role_agent
// Source: generate-api-docs.py

export declare class RoleAgentRunner extends AgentRunner {
  constructor(role: TaskRole, base_runner: AgentRunner);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
