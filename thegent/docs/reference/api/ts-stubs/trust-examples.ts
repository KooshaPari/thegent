// Auto-generated usage examples for trust
// Source: generate-api-docs.py

import { TrustBoundaryChecker, TrustLevel, check_data_flow, evaluate_routing, get_agent_trust } from "./trust";

// Create a TrustBoundaryChecker instance
const trustboundarychecker = new TrustBoundaryChecker(undefined as unknown as ThegentSettings, 0);
trustboundarychecker.check_data_flow("example_source_agent", "example_dest_agent");
trustboundarychecker.evaluate_routing("example_task_prompt", "example_target_agent");
trustboundarychecker.get_agent_trust("example_agent_name");

// Create a TrustLevel instance
const trustlevel = new TrustLevel();

// Call check_data_flow
check_data_flow(undefined as unknown as any, "example_source_agent", "example_dest_agent");
// Call evaluate_routing
evaluate_routing(undefined as unknown as any, "example_task_prompt", "example_target_agent");
// Call get_agent_trust
get_agent_trust(undefined as unknown as any, "example_agent_name");
