// Auto-generated usage examples for autonomous_learning
// Source: generate-api-docs.py

import { AutonomousLearningSurface, add_learning_point, get_recommendation } from "./autonomous_learning";

// Create a AutonomousLearningSurface instance
const autonomouslearningsurface = new AutonomousLearningSurface();
autonomouslearningsurface.add_learning_point("example_context", "example_action", undefined as unknown as any);
autonomouslearningsurface.get_recommendation("example_context");

// Call add_learning_point
add_learning_point(undefined as unknown as any, "example_context", "example_action", undefined as unknown as any);
// Call get_recommendation
get_recommendation(undefined as unknown as any, "example_context");
