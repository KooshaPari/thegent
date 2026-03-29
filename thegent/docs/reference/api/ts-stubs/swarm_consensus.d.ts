// Auto-generated TypeScript declarations for swarm_consensus
// Source: generate-api-docs.py

export declare class SwarmConsensus {
  constructor(task_id: string, threshold: number);
  evaluate_consensus(total_agents: number): void;
  get_audit_trail(): void;
  record_vote(agent_id: string, vote: any, signature: string): void;
}

export declare class SwarmVote extends BaseModel {
}

export declare function evaluate_consensus(total_agents: number): void;
export declare function get_audit_trail(): void;
export declare function record_vote(agent_id: string, vote: any, signature: string): void;
