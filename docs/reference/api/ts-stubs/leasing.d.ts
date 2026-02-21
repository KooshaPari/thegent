// Auto-generated TypeScript declarations for leasing
// Source: generate-api-docs.py

export declare class EditLease {
  is_expired(): void;
}

export declare class EditLeaseManager {
  constructor(state_dir: string);
  acquire(path: string, agent_id: string, duration: number, force: boolean): void;
  check(path: string, agent_id: any): void;
  prune(): void;
  release(path: string, agent_id: string): void;
}

export declare function acquire(path: string, agent_id: string, duration: number, force: boolean): void;
export declare function check(path: string, agent_id: any): void;
export declare function get_lease_manager(state_dir: string): void;
export declare function is_expired(): boolean;
export declare function prune(): void;
export declare function release(path: string, agent_id: string): void;
