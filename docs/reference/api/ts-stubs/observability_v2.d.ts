// Auto-generated TypeScript declarations for observability_v2
// Source: generate-api-docs.py

export declare class AdvancedMetrics {
  constructor(metrics_file: string);
  record(agent_id: string, command: string, duration: number, success: boolean): void;
}

export declare class JSONLFormatter extends logging.Formatter {
  format(record: any): void;
}

export declare class MeshCLI {
  status(mesh_dir: string): void;
  tasks(mesh_dir: string): void;
}

export declare function format(record: any): void;
export declare function record(agent_id: string, command: string, duration: number, success: boolean): void;
export declare function status(mesh_dir: string): void;
export declare function tasks(mesh_dir: string): void;
