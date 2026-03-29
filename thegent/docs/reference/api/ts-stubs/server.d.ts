// Auto-generated TypeScript declarations for server
// Source: generate-api-docs.py

export declare class ACPServerAdapter {
  constructor();
}

export declare class AgentSession {
  constructor(agent_id: string, runner: AgentRunner, cwd: any);
  add_message(role: string, content: string): void;
  stop(): void;
}

export declare function add_message(role: string, content: string): void;
export declare function stop(): void;
