// Auto-generated usage examples for overrides
// Source: generate-api-docs.py

import { OverrideManager, PolicyOverride, apply_override, cleanup_expired, from_dict, get_override, is_active, to_dict } from "./overrides";

// Create a OverrideManager instance
const overridemanager = new OverrideManager(undefined as unknown as any);
overridemanager.apply_override("example_policy_id", "example_reason", "example_by", 0, undefined as unknown as any);
overridemanager.cleanup_expired();
overridemanager.get_override("example_policy_id");

// Create a PolicyOverride instance
const policyoverride = new PolicyOverride();
policyoverride.from_dict(undefined as unknown as Record<(str, Any)>);
policyoverride.is_active();
policyoverride.to_dict();

// Call apply_override
apply_override(undefined as unknown as any, "example_policy_id", "example_reason", "example_by", 0, undefined as unknown as any);
// Call cleanup_expired
cleanup_expired(undefined as unknown as any);
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_override
get_override(undefined as unknown as any, "example_policy_id");
// Call is_active
is_active(undefined as unknown as any);
// Call to_dict
to_dict(undefined as unknown as any);
