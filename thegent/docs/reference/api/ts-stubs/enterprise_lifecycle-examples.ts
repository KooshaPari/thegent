// Auto-generated usage examples for enterprise_lifecycle
// Source: generate-api-docs.py

import { EnterpriseLifecycleManager, get_lifecycle_map, get_stage_compliance, register_compliance_check } from "./enterprise_lifecycle";

// Create a EnterpriseLifecycleManager instance
const enterpriselifecyclemanager = new EnterpriseLifecycleManager();
enterpriselifecyclemanager.get_lifecycle_map();
enterpriselifecyclemanager.get_stage_compliance("example_stage");
enterpriselifecyclemanager.register_compliance_check("example_stage", "example_check");

// Call get_lifecycle_map
get_lifecycle_map(undefined as unknown as any);
// Call get_stage_compliance
get_stage_compliance(undefined as unknown as any, "example_stage");
// Call register_compliance_check
register_compliance_check(undefined as unknown as any, "example_stage", "example_check");
