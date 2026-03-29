// Auto-generated TypeScript declarations for discovery
// Source: generate-api-docs.py

export declare class DiscoverySystem {
  is_native_active(): void;
  scan_agents(): void;
}

export declare function get_discovery_system(): DiscoverySystem;
export declare function is_native_active(): boolean;
export declare function scan_agents(): Array<Record<(str, Any)>>;
