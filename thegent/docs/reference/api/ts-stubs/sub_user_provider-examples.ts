// Auto-generated usage examples for sub_user_provider
// Source: generate-api-docs.py

import { SubUserIsolationProvider, allocate_tenant, cleanup_tenant, execute_in_context, preexec_fn } from "./sub_user_provider";

// Create a SubUserIsolationProvider instance
const subuserisolationprovider = new SubUserIsolationProvider("example_base_home_dir", 0, 0, undefined as unknown as any, undefined as unknown as any, false);
subuserisolationprovider.allocate_tenant("example_tenant_id", undefined as unknown as any, undefined as unknown as any);
subuserisolationprovider.cleanup_tenant(undefined as unknown as TenantContext);
subuserisolationprovider.execute_in_context(undefined as unknown as TenantContext, undefined as unknown as Array<unknown>, 0, undefined as unknown as any, false);

// Call allocate_tenant
allocate_tenant(undefined as unknown as any, "example_tenant_id", undefined as unknown as any, undefined as unknown as any);
// Call cleanup_tenant
cleanup_tenant(undefined as unknown as any, undefined as unknown as TenantContext);
// Call execute_in_context
execute_in_context(undefined as unknown as any, undefined as unknown as TenantContext, undefined as unknown as Array<unknown>, 0, undefined as unknown as any, false);
// Call preexec_fn
preexec_fn();
