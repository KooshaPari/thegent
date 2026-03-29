// Auto-generated usage examples for health_check
// Source: generate-api-docs.py

import { HealthChecker, register_check, run_checks } from "./health_check";

// Create a HealthChecker instance
const healthchecker = new HealthChecker();
healthchecker.register_check("example_name", undefined as unknown as callable);
healthchecker.run_checks();

// Call register_check
register_check(undefined as unknown as any, "example_name", undefined as unknown as callable);
// Call run_checks
run_checks(undefined as unknown as any);
