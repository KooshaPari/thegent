// Auto-generated usage examples for executor_integration
// Source: generate-api-docs.py

import { IsolatedExecutor, example_usage, execute_for_tenant } from "./executor_integration";

// Create a IsolatedExecutor instance
const isolatedexecutor = new IsolatedExecutor(undefined as unknown as any, false);
isolatedexecutor.execute_for_tenant("example_tenant_id", "example_agent_id", undefined as unknown as Array<unknown>, 0);

// Call example_usage
example_usage();
// Call execute_for_tenant
execute_for_tenant(undefined as unknown as any, "example_tenant_id", "example_agent_id", undefined as unknown as Array<unknown>, 0);
