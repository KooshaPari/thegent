// Auto-generated TypeScript declarations for trust
// Source: generate-api-docs.py

export declare class TrustBoundaryChecker {
  constructor(settings: ThegentSettings, cache_ttl_sec: number);
  check_data_flow(source_agent: string, dest_agent: string): void;
  evaluate_routing(task_prompt: string, target_agent: string): void;
  get_agent_trust(agent_name: string): void;
}

export declare class TrustLevel extends enum.IntEnum {
}

export declare function check_data_flow(source_agent: string, dest_agent: string): void;
export declare function evaluate_routing(task_prompt: string, target_agent: string): void;
export declare function get_agent_trust(agent_name: string): void;
