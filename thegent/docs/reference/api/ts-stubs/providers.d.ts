// Auto-generated TypeScript declarations for providers
// Source: generate-api-docs.py

export declare class ProviderConfig {
}

export declare class ProviderRegistry {
  clear(): void;
  count(): void;
  get(provider_id: string): void;
  get_fallback_order(provider_id: string): void;
  list_providers(): void;
  register(config: ProviderConfig): void;
  unregister(provider_id: string): void;
}

export declare class ProviderType extends Enum {
}

export declare function clear(): void;
export declare function count(): void;
export declare function get(provider_id: string): void;
export declare function get_fallback_order(provider_id: string): void;
export declare function list_providers(): void;
export declare function register(config: ProviderConfig): void;
export declare function unregister(provider_id: string): void;
