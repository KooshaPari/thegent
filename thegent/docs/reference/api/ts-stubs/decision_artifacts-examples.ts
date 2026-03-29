// Auto-generated usage examples for decision_artifacts
// Source: generate-api-docs.py

import { BranchingPointArtifact, DecisionArtifact, DecisionType, create } from "./decision_artifacts";

// Create a BranchingPointArtifact instance
const branchingpointartifact = new BranchingPointArtifact();
branchingpointartifact.create(undefined as unknown as MAIFArtifact, "example_condition", false, "example_true_branch", "example_false_branch");

// Create a DecisionArtifact instance
const decisionartifact = new DecisionArtifact();
decisionartifact.create(undefined as unknown as MAIFArtifact, undefined as unknown as DecisionType, undefined as unknown as Array<string>, "example_selected_option");

// Create a DecisionType instance
const decisiontype = new DecisionType();

// Call create
create(undefined as unknown as any, undefined as unknown as MAIFArtifact, "example_condition", false, "example_true_branch", "example_false_branch");
