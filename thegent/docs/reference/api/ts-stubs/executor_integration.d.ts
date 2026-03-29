// Auto-generated TypeScript declarations for executor_integration
// Source: generate-api-docs.py

export declare class IsolatedExecutor {
  constructor(isolation_provider: any, enable_isolation: boolean);
  execute_for_tenant(tenant_id: string, agent_id: string, command: Array<unknown>, timeout_sec: number): void;
}

export declare function example_usage(): void;
export declare function execute_for_tenant(tenant_id: string, agent_id: string, command: Array<unknown>, timeout_sec: number): void;
