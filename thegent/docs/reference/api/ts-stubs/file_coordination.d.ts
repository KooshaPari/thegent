// Auto-generated TypeScript declarations for file_coordination
// Source: generate-api-docs.py

export declare class FileLeaseRegistry {
  constructor(registry_dir: string);
  claim_lease(path: string, agent_id: string, mode: string, ttl: number): void;
  release_lease(path: string, agent_id: string, token: string): void;
  renew_lease(path: string, agent_id: string, token: string, ttl: number): void;
}

export declare class HybridLogicalClock {
  constructor();
  now(): void;
}

export declare class OCCManager {
  constructor(version_db: string);
  get_version(path: string): void;
  verify_and_commit(path: string, base_version: string, new_content: Uint8Array): void;
}

export declare function claim_lease(path: string, agent_id: string, mode: string, ttl: number): void;
export declare function get_version(path: string): void;
export declare function now(): void;
export declare function release_lease(path: string, agent_id: string, token: string): void;
export declare function renew_lease(path: string, agent_id: string, token: string, ttl: number): void;
export declare function verify_and_commit(path: string, base_version: string, new_content: Uint8Array): void;
