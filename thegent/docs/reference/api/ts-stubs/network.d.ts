// Auto-generated TypeScript declarations for network
// Source: generate-api-docs.py

export declare class BandwidthSample {
}

export declare class NetworkMonitor {
  get_stats(interface: any): void;
  get_total_bandwidth(): void;
  list_interfaces(): void;
  sample_bandwidth(interval_s: number): void;
}

export declare class NetworkStats {
}

export declare function get_stats(interface: any): void;
export declare function get_total_bandwidth(): void;
export declare function list_interfaces(): void;
export declare function sample_bandwidth(interval_s: number): void;
