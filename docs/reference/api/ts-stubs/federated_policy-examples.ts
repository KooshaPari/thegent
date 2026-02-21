// Auto-generated usage examples for federated_policy
// Source: generate-api-docs.py

import { FederatedPolicyEngine, PolicyRule, PolicyScope, create, evaluate, load_from_file, merge, register, resolve_policies } from "./federated_policy";

// Create a FederatedPolicyEngine instance
const federatedpolicyengine = new FederatedPolicyEngine("example_default_namespace");
federatedpolicyengine.evaluate("example_namespace", undefined as unknown as Record<(str, Any)>);
federatedpolicyengine.load_from_file("example_path", "example_namespace");
federatedpolicyengine.merge(undefined as unknown as FederatedPolicyEngine);
federatedpolicyengine.register(undefined as unknown as PolicyRule);
federatedpolicyengine.resolve_policies("example_namespace");

// Create a PolicyRule instance
const policyrule = new PolicyRule();
policyrule.create("example_rule_id", undefined as unknown as PolicyScope, "example_condition", "example_action", 0, "example_namespace");

// Create a PolicyScope instance
const policyscope = new PolicyScope();

// Call create
create(undefined as unknown as any, "example_rule_id", undefined as unknown as PolicyScope, "example_condition", "example_action", 0, "example_namespace");
// Call evaluate
evaluate(undefined as unknown as any, "example_namespace", undefined as unknown as Record<(str, Any)>);
// Call load_from_file
load_from_file(undefined as unknown as any, "example_path", "example_namespace");
// Call merge
merge(undefined as unknown as any, undefined as unknown as FederatedPolicyEngine);
// Call register
register(undefined as unknown as any, undefined as unknown as PolicyRule);
// Call resolve_policies
resolve_policies(undefined as unknown as any, "example_namespace");
