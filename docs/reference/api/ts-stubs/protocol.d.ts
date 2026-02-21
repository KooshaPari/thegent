// Auto-generated TypeScript declarations for protocol
// Source: generate-api-docs.py

export declare class P2PDiscovery {
  constructor(agent_id: string, port: number, capabilities: Array<string>);
  list_peers(): void;
  start(): void;
  stop(): void;
}

export declare class PeerAgent extends BaseModel {
}

export declare function list_peers(): void;
export declare function start(): void;
export declare function stop(): void;
