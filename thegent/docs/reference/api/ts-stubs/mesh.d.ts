// Auto-generated TypeScript declarations for mesh
// Source: generate-api-docs.py

export declare class AgentMesh {
  constructor(node_id: string, registry_url: string);
  discover_peers(capability: any): void;
  join_mesh(public_addr: string): void;
  route_to_peer(peer_id: string, payload: Record<(str, Any)>): void;
}

export declare class MeshNode extends BaseModel {
}

export declare function discover_peers(capability: any): void;
export declare function join_mesh(public_addr: string): void;
export declare function route_to_peer(peer_id: string, payload: Record<(str, Any)>): void;
