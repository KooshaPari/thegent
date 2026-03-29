// Auto-generated usage examples for teammates
// Source: generate-api-docs.py

import { DelegationRequest, TeammateManager, TeammatePersona, create_team, delegate, get_delegations, list_personas, update_status } from "./teammates";

// Create a DelegationRequest instance
const delegationrequest = new DelegationRequest();

// Create a TeammateManager instance
const teammatemanager = new TeammateManager("example_storage_path", undefined as unknown as any);
teammatemanager.create_team("example_team_id", "example_name", "example_description", undefined as unknown as TeamType, undefined as unknown as CoordinationMode, "example_lead_id");
teammatemanager.delegate("example_teammate_id", "example_parent_run_id", "example_prompt", undefined as unknown as any, undefined as unknown as RelationshipType);
teammatemanager.get_delegations(undefined as unknown as any);
teammatemanager.list_personas();
teammatemanager.update_status("example_req_id", "example_status", undefined as unknown as any);

// Create a TeammatePersona instance
const teammatepersona = new TeammatePersona();

// Call create_team
create_team(undefined as unknown as any, "example_team_id", "example_name", "example_description", undefined as unknown as TeamType, undefined as unknown as CoordinationMode, "example_lead_id");
// Call delegate
delegate(undefined as unknown as any, "example_teammate_id", "example_parent_run_id", "example_prompt", undefined as unknown as any, undefined as unknown as RelationshipType);
// Call get_delegations
get_delegations(undefined as unknown as any, undefined as unknown as any);
// Call list_personas
list_personas(undefined as unknown as any);
// Call update_status
update_status(undefined as unknown as any, "example_req_id", "example_status", undefined as unknown as any);
