// Auto-generated usage examples for economic_governance
// Source: generate-api-docs.py

import { EconomicGovernance, check_budget, route_with_governance, set_budget_limit } from "./economic_governance";

// Create a EconomicGovernance instance
const economicgovernance = new EconomicGovernance();
economicgovernance.check_budget("example_tenant_id", 0);
economicgovernance.route_with_governance("example_tenant_id", undefined as unknown as Array<Record<(str, Any)>>);
economicgovernance.set_budget_limit("example_tenant_id", 0);

// Call check_budget
check_budget(undefined as unknown as any, "example_tenant_id", 0);
// Call route_with_governance
route_with_governance(undefined as unknown as any, "example_tenant_id", undefined as unknown as Array<Record<(str, Any)>>);
// Call set_budget_limit
set_budget_limit(undefined as unknown as any, "example_tenant_id", 0);
