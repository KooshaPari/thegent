// Auto-generated usage examples for explainability
// Source: generate-api-docs.py

import { DetailLevel, ExplainabilityEngine, Explanation, get_explanation, record_decision, render_all } from "./explainability";

// Create a DetailLevel instance
const detaillevel = new DetailLevel();

// Create a ExplainabilityEngine instance
const explainabilityengine = new ExplainabilityEngine();
explainabilityengine.get_explanation("example_decision_id", undefined as unknown as DetailLevel);
explainabilityengine.record_decision("example_decision_id", undefined as unknown as Explanation);
explainabilityengine.render_all("example_decision_id");

// Create a Explanation instance
const explanation = new Explanation();

// Call get_explanation
get_explanation(undefined as unknown as any, "example_decision_id", undefined as unknown as DetailLevel);
// Call record_decision
record_decision(undefined as unknown as any, "example_decision_id", undefined as unknown as Explanation);
// Call render_all
render_all(undefined as unknown as any, "example_decision_id");
