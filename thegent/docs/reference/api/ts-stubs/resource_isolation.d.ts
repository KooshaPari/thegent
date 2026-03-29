// Auto-generated TypeScript declarations for resource_isolation
// Source: generate-api-docs.py

export declare class EnvIsolator {
  wrap_env(agent_id: string, custom_vars: Record<(str, str)>): void;
}

export declare class ResourceIsolator {
  constructor(base_tmp_dir: string);
  allocate_ports(agent_id: string, count: number): void;
  cleanup_agent(agent_id: string): void;
  setup_agent_env(agent_id: string): void;
}

export declare function allocate_ports(agent_id: string, count: number): void;
export declare function cleanup_agent(agent_id: string): void;
export declare function setup_agent_env(agent_id: string): void;
export declare function wrap_env(agent_id: string, custom_vars: Record<(str, str)>): Record<(str, str)>;
