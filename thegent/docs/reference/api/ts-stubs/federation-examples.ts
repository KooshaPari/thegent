// Auto-generated usage examples for federation
// Source: generate-api-docs.py

import { FederatedPolicyManager, FederationManager, PolicyNamespace, apply_jurisdiction_constraints, arbitrate_conflict, get_effective_policy, get_federation_health, get_hierarchy, join_namespace, leave_namespace, relay_consent, resolve_policy, sync_policies } from "./federation";

// Create a FederatedPolicyManager instance
const federatedpolicymanager = new FederatedPolicyManager("example_base_dir");
federatedpolicymanager.apply_jurisdiction_constraints(undefined as unknown as Record<(str, Any)>, "example_region");
federatedpolicymanager.arbitrate_conflict(undefined as unknown as Array<Record<(str, Any)>>);
federatedpolicymanager.get_federation_health();
federatedpolicymanager.join_namespace("example_ns_str");
federatedpolicymanager.leave_namespace("example_ns_str");
federatedpolicymanager.relay_consent(undefined as unknown as PolicyNamespace, undefined as unknown as PolicyNamespace, "example_run_id", "example_approver");
federatedpolicymanager.resolve_policy(undefined as unknown as PolicyNamespace, "example_policy_id");

// Create a FederationManager instance
const federationmanager = new FederationManager("example_session_dir");
federationmanager.get_effective_policy("example_policy_id");
federationmanager.sync_policies("example_peer_id");

// Create a PolicyNamespace instance
const policynamespace = new PolicyNamespace("example_org", "example_project", "example_environment");
policynamespace.get_hierarchy();

// Call apply_jurisdiction_constraints
apply_jurisdiction_constraints(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, "example_region");
// Call arbitrate_conflict
arbitrate_conflict(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call get_effective_policy
get_effective_policy(undefined as unknown as any, "example_policy_id");
// Call get_federation_health
get_federation_health(undefined as unknown as any);
// Call get_hierarchy
get_hierarchy(undefined as unknown as any);
// Call join_namespace
join_namespace(undefined as unknown as any, "example_ns_str");
// Call leave_namespace
leave_namespace(undefined as unknown as any, "example_ns_str");
// Call relay_consent
relay_consent(undefined as unknown as any, undefined as unknown as PolicyNamespace, undefined as unknown as PolicyNamespace, "example_run_id", "example_approver");
// Call resolve_policy
resolve_policy(undefined as unknown as any, undefined as unknown as PolicyNamespace, "example_policy_id");
// Call sync_policies
sync_policies(undefined as unknown as any, "example_peer_id");
