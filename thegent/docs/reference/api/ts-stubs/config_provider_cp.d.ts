// Auto-generated TypeScript declarations for config_provider_cp
// Source: generate-api-docs.py

export declare class ControlPlaneConfigProvider {
  constructor(url: string, timeout: number);
  get_tenant_config(tenant_id: string): void;
  resolve(tenant_id: any, session_id: any, request_overrides: any, keys: any): void;
}

export declare function get_tenant_config(tenant_id: string): void;
export declare function resolve(tenant_id: any, session_id: any, request_overrides: any, keys: any): void;
