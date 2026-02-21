// Auto-generated TypeScript declarations for relativistic
// Source: generate-api-docs.py

export declare class RelativisticClockSync {
  constructor(base_node: RelativisticNode);
  add_peer(node: RelativisticNode): void;
  calculate_dilation_factor(peer_id: string): void;
  sync_timestamp(peer_id: string, remote_ts: number): void;
}

export declare class RelativisticNode {
}

export declare function add_peer(node: RelativisticNode): void;
export declare function calculate_dilation_factor(peer_id: string): void;
export declare function sync_timestamp(peer_id: string, remote_ts: number): void;
