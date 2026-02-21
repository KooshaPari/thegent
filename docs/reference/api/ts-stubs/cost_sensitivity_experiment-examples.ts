// Auto-generated usage examples for cost_sensitivity_experiment
// Source: generate-api-docs.py

import { ExperimentRunner, FederatedPolicyEngineSim, PolicyNamespace, resolve_effective_policy, run_scenario, setup_baseline, setup_experiment_a, setup_experiment_b } from "./cost_sensitivity_experiment";

// Create a ExperimentRunner instance
const experimentrunner = new ExperimentRunner();
experimentrunner.run_scenario("example_name", undefined as unknown as FederatedPolicyEngineSim, "example_leaf_ns");

// Create a FederatedPolicyEngineSim instance
const federatedpolicyenginesim = new FederatedPolicyEngineSim(undefined as unknown as Array<PolicyNamespace>);
federatedpolicyenginesim.resolve_effective_policy("example_leaf_namespace_name");

// Create a PolicyNamespace instance
const policynamespace = new PolicyNamespace();

// Call resolve_effective_policy
resolve_effective_policy(undefined as unknown as any, "example_leaf_namespace_name");
// Call run_scenario
run_scenario(undefined as unknown as any, "example_name", undefined as unknown as FederatedPolicyEngineSim, "example_leaf_ns");
// Call setup_baseline
setup_baseline();
// Call setup_experiment_a
setup_experiment_a();
// Call setup_experiment_b
setup_experiment_b();
