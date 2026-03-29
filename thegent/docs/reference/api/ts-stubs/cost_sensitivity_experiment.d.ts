// Auto-generated TypeScript declarations for cost_sensitivity_experiment
// Source: generate-api-docs.py

export declare class ExperimentRunner {
  constructor();
  run_scenario(name: string, engine: FederatedPolicyEngineSim, leaf_ns: string): void;
}

export declare class FederatedPolicyEngineSim {
  constructor(namespaces: Array<PolicyNamespace>);
  resolve_effective_policy(leaf_namespace_name: string): void;
}

export declare class PolicyNamespace {
}

export declare function resolve_effective_policy(leaf_namespace_name: string): void;
export declare function run_scenario(name: string, engine: FederatedPolicyEngineSim, leaf_ns: string): void;
export declare function setup_baseline(): [(FederatedPolicyEngineSim, str)];
export declare function setup_experiment_a(): [(FederatedPolicyEngineSim, str)];
export declare function setup_experiment_b(): [(FederatedPolicyEngineSim, str)];
