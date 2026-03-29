// Auto-generated TypeScript declarations for tailscale
// Source: generate-api-docs.py

export declare class TailscaleConfig extends BaseSettings {
}

export declare class TailscaleError extends Exception {
}

export declare class TailscaleManager {
  constructor(config: any);
  get_online_nodes(): void;
  is_available(): void;
  list_nodes(): void;
  ping_node(hostname: string): void;
}

export declare class TailscaleNode {
}

export declare function get_online_nodes(): void;
export declare function is_available(): void;
export declare function list_nodes(): void;
export declare function ping_node(hostname: string): void;
