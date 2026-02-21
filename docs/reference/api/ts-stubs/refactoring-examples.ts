// Auto-generated usage examples for refactoring
// Source: generate-api-docs.py

import { CognitiveRefactorer, analyze_reasoning_efficiency, apply_refactor, propose_refactor } from "./refactoring";

// Create a CognitiveRefactorer instance
const cognitiverefactorer = new CognitiveRefactorer("example_agent_id");
cognitiverefactorer.analyze_reasoning_efficiency(undefined as unknown as Array<Record<(str, Any)>>);
cognitiverefactorer.apply_refactor("example_refactor_plan");
cognitiverefactorer.propose_refactor(undefined as unknown as Record<(str, float)>);

// Call analyze_reasoning_efficiency
analyze_reasoning_efficiency(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call apply_refactor
apply_refactor(undefined as unknown as any, "example_refactor_plan");
// Call propose_refactor
propose_refactor(undefined as unknown as any, undefined as unknown as Record<(str, float)>);
