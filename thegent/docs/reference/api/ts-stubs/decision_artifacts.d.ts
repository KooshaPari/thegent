// Auto-generated TypeScript declarations for decision_artifacts
// Source: generate-api-docs.py

export declare class BranchingPointArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, condition: string, condition_result: boolean, true_branch: string, false_branch: string): void;
}

export declare class DecisionArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, decision_type: DecisionType, options_considered: Array<string>, selected_option: string): void;
}

export declare class DecisionType extends str, Enum {
}

export declare function create(maif: MAIFArtifact, condition: string, condition_result: boolean, true_branch: string, false_branch: string): void;
