// Auto-generated usage examples for cli_initiative
// Source: generate-api-docs.py

import { Initiative, initiative_audit_cmd, initiative_list_cmd, parse_plan_initiatives } from "./cli_initiative";

// Create a Initiative instance
const initiative = new Initiative("example_id", "example_title", "example_status", "example_deliverables", "example_effort");

// Call initiative_audit_cmd
initiative_audit_cmd();
// Call initiative_list_cmd
initiative_list_cmd();
// Call parse_plan_initiatives
parse_plan_initiatives("example_plan_path");
