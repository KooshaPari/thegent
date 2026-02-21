// Auto-generated usage examples for file_coordination
// Source: generate-api-docs.py

import { FileLeaseRegistry, HybridLogicalClock, OCCManager, claim_lease, get_version, now, release_lease, renew_lease, verify_and_commit } from "./file_coordination";

// Create a FileLeaseRegistry instance
const fileleaseregistry = new FileLeaseRegistry("example_registry_dir");
fileleaseregistry.claim_lease("example_path", "example_agent_id", "example_mode", 0);
fileleaseregistry.release_lease("example_path", "example_agent_id", "example_token");
fileleaseregistry.renew_lease("example_path", "example_agent_id", "example_token", 0);

// Create a HybridLogicalClock instance
const hybridlogicalclock = new HybridLogicalClock();
hybridlogicalclock.now();

// Create a OCCManager instance
const occmanager = new OCCManager("example_version_db");
occmanager.get_version("example_path");
occmanager.verify_and_commit("example_path", "example_base_version", undefined as unknown as Uint8Array);

// Call claim_lease
claim_lease(undefined as unknown as any, "example_path", "example_agent_id", "example_mode", 0);
// Call get_version
get_version(undefined as unknown as any, "example_path");
// Call now
now(undefined as unknown as any);
// Call release_lease
release_lease(undefined as unknown as any, "example_path", "example_agent_id", "example_token");
// Call renew_lease
renew_lease(undefined as unknown as any, "example_path", "example_agent_id", "example_token", 0);
// Call verify_and_commit
verify_and_commit(undefined as unknown as any, "example_path", "example_base_version", undefined as unknown as Uint8Array);
