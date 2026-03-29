// Auto-generated TypeScript declarations for uid_pool
// Source: generate-api-docs.py

export declare class UidPool {
  constructor(base_uid: number, size: number, state_file: any);
  allocate(tenant_id: string): void;
  get_tenant_id(uid: number): void;
  get_uid(tenant_id: string): void;
  release(tenant_id: string): void;
}

export declare function allocate(tenant_id: string): void;
export declare function get_tenant_id(uid: number): void;
export declare function get_uid(tenant_id: string): void;
export declare function release(tenant_id: string): void;
