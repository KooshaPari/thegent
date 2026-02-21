// Auto-generated TypeScript declarations for dex_flash_agents
// Source: generate-api-docs.py

export declare class DexFlashAgents {
  constructor();
  flash_execute(agent_name: string, command: string): void;
  register_flash_agent(name: string, agent: any): void;
}

export declare function flash_execute(agent_name: string, command: string): void;
export declare function register_flash_agent(name: string, agent: any): void;
