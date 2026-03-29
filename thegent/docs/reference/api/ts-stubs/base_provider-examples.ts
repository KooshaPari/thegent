// Auto-generated usage examples for base_provider
// Source: generate-api-docs.py

import { IsolationProvider, allocate_tenant, cleanup_tenant, execute_in_context } from "./base_provider";

// Create a IsolationProvider instance
const isolationprovider = new IsolationProvider();
isolationprovider.allocate_tenant("example_tenant_id", undefined as unknown as any);
isolationprovider.cleanup_tenant(undefined as unknown as TenantContext);
isolationprovider.execute_in_context(undefined as unknown as TenantContext, undefined as unknown as Array<unknown>, 0);

// Call allocate_tenant
allocate_tenant(undefined as unknown as any, "example_tenant_id", undefined as unknown as any);
// Call cleanup_tenant
cleanup_tenant(undefined as unknown as any, undefined as unknown as TenantContext);
// Call execute_in_context
execute_in_context(undefined as unknown as any, undefined as unknown as TenantContext, undefined as unknown as Array<unknown>, 0);
