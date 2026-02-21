// Auto-generated usage examples for leasing
// Source: generate-api-docs.py

import { EditLease, EditLeaseManager, acquire, check, get_lease_manager, is_expired, prune, release } from "./leasing";

// Create a EditLease instance
const editlease = new EditLease();
editlease.is_expired();

// Create a EditLeaseManager instance
const editleasemanager = new EditLeaseManager("example_state_dir");
editleasemanager.acquire("example_path", "example_agent_id", 0, false);
editleasemanager.check("example_path", undefined as unknown as any);
editleasemanager.prune();
editleasemanager.release("example_path", "example_agent_id");

// Call acquire
acquire(undefined as unknown as any, "example_path", "example_agent_id", 0, false);
// Call check
check(undefined as unknown as any, "example_path", undefined as unknown as any);
// Call get_lease_manager
get_lease_manager("example_state_dir");
// Call is_expired
is_expired(undefined as unknown as any);
// Call prune
prune(undefined as unknown as any);
// Call release
release(undefined as unknown as any, "example_path", "example_agent_id");
