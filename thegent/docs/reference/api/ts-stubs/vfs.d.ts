// Auto-generated TypeScript declarations for vfs
// Source: generate-api-docs.py

export declare class VfsAdapter {
  constructor(base_skel_dir: any);
  cleanup_home_dir(target_dir: string, tenant_id: string): void;
  create_home_dir(target_dir: string, tenant_id: string): void;
}

export declare function cleanup_home_dir(target_dir: string, tenant_id: string): void;
export declare function create_home_dir(target_dir: string, tenant_id: string): void;
