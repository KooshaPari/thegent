// Auto-generated usage examples for final_state_consensus
// Source: generate-api-docs.py

import { FinalStateConsensusProtocol, get_final_state, propose_state, reach_consensus, vote } from "./final_state_consensus";

// Create a FinalStateConsensusProtocol instance
const finalstateconsensusprotocol = new FinalStateConsensusProtocol();
finalstateconsensusprotocol.get_final_state("example_proposal_id");
finalstateconsensusprotocol.propose_state("example_node_id", undefined as unknown as Record<(str, Any)>);
finalstateconsensusprotocol.reach_consensus("example_proposal_id", 0);
finalstateconsensusprotocol.vote("example_proposal_id", "example_node_id", false);

// Call get_final_state
get_final_state(undefined as unknown as any, "example_proposal_id");
// Call propose_state
propose_state(undefined as unknown as any, "example_node_id", undefined as unknown as Record<(str, Any)>);
// Call reach_consensus
reach_consensus(undefined as unknown as any, "example_proposal_id", 0);
// Call vote
vote(undefined as unknown as any, "example_proposal_id", "example_node_id", false);
