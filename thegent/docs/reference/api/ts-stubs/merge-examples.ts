// Auto-generated usage examples for merge
// Source: generate-api-docs.py

import { SmartMerge, merge_ast_aware, merge_structural, predict_conflicts, resolve_imports } from "./merge";

// Create a SmartMerge instance
const smartmerge = new SmartMerge("example_mesh_root");
smartmerge.merge_ast_aware("example_base", "example_ours", "example_theirs", "example_output");
smartmerge.merge_structural("example_path_a", "example_path_b", "example_output");
smartmerge.predict_conflicts(undefined as unknown as Array<Record<string, unknown>>);
smartmerge.resolve_imports("example_content_a", "example_content_b", "example_language");

// Call merge_ast_aware
merge_ast_aware(undefined as unknown as any, "example_base", "example_ours", "example_theirs", "example_output");
// Call merge_structural
merge_structural(undefined as unknown as any, "example_path_a", "example_path_b", "example_output");
// Call predict_conflicts
predict_conflicts(undefined as unknown as any, undefined as unknown as Array<Record<string, unknown>>);
// Call resolve_imports
resolve_imports(undefined as unknown as any, "example_content_a", "example_content_b", "example_language");
