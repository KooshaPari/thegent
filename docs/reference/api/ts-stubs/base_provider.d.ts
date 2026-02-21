// Auto-generated TypeScript declarations for base_provider
// Source: generate-api-docs.py

export declare class IsolationProvider extends ABC {
  allocate_tenant(tenant_id: string, agent_id: any): void;
  cleanup_tenant(context: TenantContext): void;
  execute_in_context(context: TenantContext, command: Array<unknown>, timeout_sec: number): void;
}

export declare function allocate_tenant(tenant_id: string, agent_id: any): void;
export declare function cleanup_tenant(context: TenantContext): void;
export declare function execute_in_context(context: TenantContext, command: Array<unknown>, timeout_sec: number): void;
