// Auto-generated TypeScript declarations for offload
// Source: generate-api-docs.py

export declare class ComputeOffload {
  constructor(nodes: any, ssh_user: any);
  available_targets(): void;
  offload(target_id: string, command: string, timeout_s: number): void;
  register_target(target_id: string, host: string, port: number): void;
}

export declare function available_targets(): void;
export declare function offload(target_id: string, command: string, timeout_s: number): void;
export declare function register_target(target_id: string, host: string, port: number): void;
