// Auto-generated TypeScript declarations for edge_sync
// Source: generate-api-docs.py

export declare class EdgeSyncController {
  constructor(device_id: string);
  apply_remote_delta(compressed_delta: Uint8Array): void;
  compute_delta(current_state: Record<(str, Any)>): void;
  get_adaptive_polling_interval(battery_level: number): void;
}

export declare function apply_remote_delta(compressed_delta: Uint8Array): void;
export declare function compute_delta(current_state: Record<(str, Any)>): void;
export declare function get_adaptive_polling_interval(battery_level: number): void;
