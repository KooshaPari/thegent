// Auto-generated TypeScript declarations for tenancy
// Source: generate-api-docs.py

export declare class KeyIsolator {
  constructor(settings: any);
  delete_tenant(owner: string): void;
  get_key(owner: string, provider: string): void;
  get_tenant_dir(owner: string): void;
  isolate_key(owner: string, provider: string, api_key: string): void;
  list_tenants(): void;
}

export declare function delete_tenant(owner: string): void;
export declare function get_key(owner: string, provider: string): void;
export declare function get_tenant_dir(owner: string): void;
export declare function isolate_key(owner: string, provider: string, api_key: string): void;
export declare function list_tenants(): void;
