// Auto-generated TypeScript declarations for probing
// Source: generate-api-docs.py

export declare class AgentFingerprint extends BaseModel {
}

export declare class AgentProber {
  constructor(agent_id: string);
  identify_deviations(current_fp: AgentFingerprint, baseline_fp: AgentFingerprint): void;
  probe_agent(proxy_fn: any): void;
}

export declare function identify_deviations(current_fp: AgentFingerprint, baseline_fp: AgentFingerprint): void;
export declare function probe_agent(proxy_fn: any): void;
