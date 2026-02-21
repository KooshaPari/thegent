// Auto-generated TypeScript declarations for consensus
// Source: generate-api-docs.py

export declare class CausalInfluenceTracker {
  constructor(mesh_root: string);
  record_influence(agent_id: string, action_id: string, contribution: number): void;
}

export declare class ConsensusProtocol {
  constructor(mesh_root: string);
  cast_vote(proposal_id: string, agent_id: string, vote: boolean, confidence: number): void;
  draft(proposal_id: string, agent_id: string, refinement: Record<string, unknown>): void;
  get_consensus(proposal_id: string, required_majority: number): void;
  propose(proposal_id: string, agent_id: string, topic: string, content: Record<string, unknown>): void;
  share(proposal_id: string): void;
}

export declare class ConsensusStatus extends enum.Enum {
}

export declare class EscalationWorkflow {
  constructor(mesh_root: string);
  escalate(proposal_id: string, current_tier: number): void;
}

export declare function cast_vote(proposal_id: string, agent_id: string, vote: boolean, confidence: number): void;
export declare function draft(proposal_id: string, agent_id: string, refinement: Record<string, unknown>): void;
export declare function escalate(proposal_id: string, current_tier: number): void;
export declare function get_consensus(proposal_id: string, required_majority: number): void;
export declare function propose(proposal_id: string, agent_id: string, topic: string, content: Record<string, unknown>): void;
export declare function record_influence(agent_id: string, action_id: string, contribution: number): void;
export declare function share(proposal_id: string): void;
