// Auto-generated TypeScript declarations for omega_consensus
// Source: generate-api-docs.py

export declare class OmegaConsensus {
  constructor(swarm_size: number, threshold: number);
  cast_vote(proposal_id: string, voter_id: string, vote: boolean, signature: string): void;
  finalize_consensus(proposal_id: string): void;
  get_final_state(): void;
  propose_state(proposer_id: string, state: any, metadata: Record<(str, Any)>): void;
}

export declare class OmegaProposal extends BaseModel {
}

export declare class OmegaVote extends BaseModel {
}

export declare function cast_vote(proposal_id: string, voter_id: string, vote: boolean, signature: string): void;
export declare function finalize_consensus(proposal_id: string): void;
export declare function get_final_state(): void;
export declare function propose_state(proposer_id: string, state: any, metadata: Record<(str, Any)>): void;
