// Auto-generated usage examples for migration
// Source: generate-api-docs.py

import { MigrationController, evaluate_version, get_preferred_version, set_canary, set_dual_write, should_use_new_version } from "./migration";

// Create a MigrationController instance
const migrationcontroller = new MigrationController(undefined as unknown as any);
migrationcontroller.evaluate_version("example_contract_id", "example_version");
migrationcontroller.get_preferred_version("example_contract_id");
migrationcontroller.set_canary(0);
migrationcontroller.set_dual_write(false);
migrationcontroller.should_use_new_version("example_run_id");

// Call evaluate_version
evaluate_version(undefined as unknown as any, "example_contract_id", "example_version");
// Call get_preferred_version
get_preferred_version(undefined as unknown as any, "example_contract_id");
// Call set_canary
set_canary(undefined as unknown as any, 0);
// Call set_dual_write
set_dual_write(undefined as unknown as any, false);
// Call should_use_new_version
should_use_new_version(undefined as unknown as any, "example_run_id");
