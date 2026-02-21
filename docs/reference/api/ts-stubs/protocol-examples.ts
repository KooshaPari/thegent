// Auto-generated usage examples for protocol
// Source: generate-api-docs.py

import { P2PDiscovery, PeerAgent, list_peers, start, stop } from "./protocol";

// Create a P2PDiscovery instance
const p2pdiscovery = new P2PDiscovery("example_agent_id", 0, undefined as unknown as Array<string>);
p2pdiscovery.list_peers();
p2pdiscovery.start();
p2pdiscovery.stop();

// Create a PeerAgent instance
const peeragent = new PeerAgent();

// Call list_peers
list_peers(undefined as unknown as any);
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
