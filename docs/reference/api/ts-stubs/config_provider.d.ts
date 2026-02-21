// Auto-generated TypeScript declarations for config_provider
// Source: generate-api-docs.py

export declare class ConfigProvider extends Protocol {
  get_tenant_config(tenant_id: string): void;
  resolve(tenant_id: any, session_id: any, request_overrides: any, keys: any): void;
}

export declare class EnvConfigProvider {
  get_tenant_config(tenant_id: string): void;
  resolve(tenant_id: any, session_id: any, request_overrides: any, keys: any): void;
}

export declare function get_config_provider(): void;
export declare function get_tenant_config(tenant_id: string): void;
export declare function resolve(tenant_id: any, session_id: any, request_overrides: any, keys: any): Record<(str, Any)>;
