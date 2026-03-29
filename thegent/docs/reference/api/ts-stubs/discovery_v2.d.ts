// Auto-generated TypeScript declarations for discovery_v2
// Source: generate-api-docs.py

export declare class AgentManifest {
  create(manifest_path: string, agent_info: Record<(str, Any)>): void;
}

export declare class AgentScanner {
  scan(): void;
}

export declare class HeartbeatMonitor {
  constructor(heartbeat_dir: string, failure_threshold: number);
  beat(agent_id: string): void;
  cleanup_stale(callback: any): void;
  get_stale_agents(): void;
}

export declare function beat(agent_id: string): void;
export declare function cleanup_stale(callback: any): void;
export declare function create(manifest_path: string, agent_info: Record<(str, Any)>): void;
export declare function get_stale_agents(): void;
export declare function scan(): void;
