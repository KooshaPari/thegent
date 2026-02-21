// Auto-generated TypeScript declarations for client
// Source: generate-api-docs.py

export declare class ACPClientAdapter extends AgentRunner {
  constructor(acp_command: Array<string>, agent_name: string);
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function run(prompt: string, cwd: any, mode: string, timeout: number): void;
