// Auto-generated TypeScript declarations for observability
// Source: generate-api-docs.py

export declare class MeshLogger {
  constructor(mesh_root: string);
  log(agent_id: string, event: string, data: any): void;
}

export declare class MetricsAggregator {
  constructor(mesh_root: string);
  get_summary(): void;
  record_metric(agent_id: string, name: string, value: number): void;
}

export declare function get_summary(): void;
export declare function log(agent_id: string, event: string, data: any): void;
export declare function mesh_status_cmd(mesh_root: string): void;
export declare function record_metric(agent_id: string, name: string, value: number): void;
