// Auto-generated TypeScript declarations for final_state_consensus
// Source: generate-api-docs.py

export declare class FinalStateConsensusProtocol {
  constructor();
  get_final_state(proposal_id: string): void;
  propose_state(node_id: string, state: Record<(str, Any)>): void;
  reach_consensus(proposal_id: string, threshold: number): void;
  vote(proposal_id: string, node_id: string, vote: boolean): void;
}

export declare function get_final_state(proposal_id: string): void;
export declare function propose_state(node_id: string, state: Record<(str, Any)>): void;
export declare function reach_consensus(proposal_id: string, threshold: number): void;
export declare function vote(proposal_id: string, node_id: string, vote: boolean): void;
