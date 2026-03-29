// Auto-generated TypeScript declarations for distributed
// Source: generate-api-docs.py

export declare class DistributedResourceCoordinator {
  constructor(lease_file: any, resource_limits: any, lock_timeout: number);
  acquire(resource: string, amount: number, owner: string, ttl_s: number, total: any): void;
  cleanup_expired(): void;
  get_active_leases(resource: any): void;
  get_available(resource: string, total: number): void;
  release(lease_id: string): void;
}

export declare class ResourceCoordinationError extends Exception {
}

export declare class ResourceLease {
  from_dict(data: Record<string, unknown>): void;
  is_expired(): void;
  to_dict(): void;
}

export declare function acquire(resource: string, amount: number, owner: string, ttl_s: number, total: any): void;
export declare function cleanup_expired(): void;
export declare function from_dict(data: Record<string, unknown>): void;
export declare function get_active_leases(resource: any): void;
export declare function get_available(resource: string, total: number): void;
export declare function is_expired(): void;
export declare function release(lease_id: string): void;
export declare function to_dict(): void;
