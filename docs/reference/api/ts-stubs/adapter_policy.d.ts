// Auto-generated TypeScript declarations for adapter_policy
// Source: generate-api-docs.py

export declare class AdapterAdmissionPolicy {
  constructor(registry: CapabilityRegistry, cache_ttl_sec: number);
  evaluate_admission(adapter_id: string, lane: string): void;
}

export declare function evaluate_admission(adapter_id: string, lane: string): void;
