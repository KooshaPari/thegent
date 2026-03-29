// Auto-generated usage examples for learning
// Source: generate-api-docs.py

import { LearningSubcommands, record, should_skip } from "./learning";

// Create a LearningSubcommands instance
const learningsubcommands = new LearningSubcommands(undefined as unknown as any);
learningsubcommands.record("example_pattern", false, "example_reason");
learningsubcommands.should_skip("example_pattern", 0);

// Call record
record(undefined as unknown as any, "example_pattern", false, "example_reason");
// Call should_skip
should_skip(undefined as unknown as any, "example_pattern", 0);
