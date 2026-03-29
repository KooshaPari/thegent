// Auto-generated TypeScript declarations for sub_user_provider
// Source: generate-api-docs.py

export declare class SubUserIsolationProvider extends IsolationProvider {
  constructor(base_home_dir: string, base_uid: number, uid_pool_size: number, state_dir: any, skel_dir: any, enable_l1_nesting: boolean);
  allocate_tenant(tenant_id: string, agent_id: any, role: any): void;
  cleanup_tenant(context: TenantContext): void;
  execute_in_context(context: TenantContext, command: Array<unknown>, timeout_sec: number, limits: any, share: boolean): void;
}

export declare function allocate_tenant(tenant_id: string, agent_id: any, role: any): void;
export declare function cleanup_tenant(context: TenantContext): void;
export declare function execute_in_context(context: TenantContext, command: Array<unknown>, timeout_sec: number, limits: any, share: boolean): void;
export declare function preexec_fn(): void;
