// Auto-generated TypeScript declarations for capability_registry
// Source: generate-api-docs.py

export declare class Capability {
}

export declare class CapabilityRegistry {
  constructor();
  get_capability(cap_id: string): void;
  is_supported(cap_id: string, version: any): void;
  list_capabilities(): void;
  register(cap: Capability): void;
}

export declare function get_capability(cap_id: string): void;
export declare function is_supported(cap_id: string, version: any): void;
export declare function list_capabilities(): void;
export declare function register(cap: Capability): void;
