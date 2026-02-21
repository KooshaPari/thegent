// Auto-generated usage examples for hitl
// Source: generate-api-docs.py

import { HITLManager, approve, is_approved, request_approval } from "./hitl";

// Create a HITLManager instance
const hitlmanager = new HITLManager();
hitlmanager.approve("example_request_id");
hitlmanager.is_approved("example_request_id");
hitlmanager.request_approval("example_request_id", "example_action", undefined as unknown as Record<(str, Any)>);

// Call approve
approve(undefined as unknown as any, "example_request_id");
// Call is_approved
is_approved(undefined as unknown as any, "example_request_id");
// Call request_approval
request_approval(undefined as unknown as any, "example_request_id", "example_action", undefined as unknown as Record<(str, Any)>);
