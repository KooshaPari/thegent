// Auto-generated usage examples for mesh
// Source: generate-api-docs.py

import { AgentMesh, MeshNode, discover_peers, join_mesh, route_to_peer } from "./mesh";

// Create a AgentMesh instance
const agentmesh = new AgentMesh("example_node_id", "example_registry_url");
agentmesh.discover_peers(undefined as unknown as any);
agentmesh.join_mesh("example_public_addr");
agentmesh.route_to_peer("example_peer_id", undefined as unknown as Record<(str, Any)>);

// Create a MeshNode instance
const meshnode = new MeshNode();

// Call discover_peers
discover_peers(undefined as unknown as any, undefined as unknown as any);
// Call join_mesh
join_mesh(undefined as unknown as any, "example_public_addr");
// Call route_to_peer
route_to_peer(undefined as unknown as any, "example_peer_id", undefined as unknown as Record<(str, Any)>);
