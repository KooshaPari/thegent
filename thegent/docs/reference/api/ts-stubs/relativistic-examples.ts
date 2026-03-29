// Auto-generated usage examples for relativistic
// Source: generate-api-docs.py

import { RelativisticClockSync, RelativisticNode, add_peer, calculate_dilation_factor, sync_timestamp } from "./relativistic";

// Create a RelativisticClockSync instance
const relativisticclocksync = new RelativisticClockSync(undefined as unknown as RelativisticNode);
relativisticclocksync.add_peer(undefined as unknown as RelativisticNode);
relativisticclocksync.calculate_dilation_factor("example_peer_id");
relativisticclocksync.sync_timestamp("example_peer_id", 0);

// Create a RelativisticNode instance
const relativisticnode = new RelativisticNode();

// Call add_peer
add_peer(undefined as unknown as any, undefined as unknown as RelativisticNode);
// Call calculate_dilation_factor
calculate_dilation_factor(undefined as unknown as any, "example_peer_id");
// Call sync_timestamp
sync_timestamp(undefined as unknown as any, "example_peer_id", 0);
