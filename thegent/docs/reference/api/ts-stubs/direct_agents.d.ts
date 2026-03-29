// Auto-generated TypeScript declarations for direct_agents
// Source: generate-api-docs.py

export declare class DirectAgentRunner extends AgentRunner {
  constructor(agent_name: string, cli_cmd: any, default_model: string, use_litellm_router: any);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
