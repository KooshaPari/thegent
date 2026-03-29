// Auto-generated usage examples for smart_merge
// Source: generate-api-docs.py

import { SmartMerger, merge_ast, merge_structural, predict_conflicts, resolve_imports } from "./smart_merge";

// Create a SmartMerger instance
const smartmerger = new SmartMerger("example_mergiraf_path");
smartmerger.merge_ast("example_base", "example_local", "example_remote", "example_output");
smartmerger.merge_structural("example_base_file", "example_local_file", "example_remote_file", "example_output_file");
smartmerger.predict_conflicts(undefined as unknown as Array<Record<(str, Any)>>);
smartmerger.resolve_imports("example_content", "example_lang");

// Call merge_ast
merge_ast(undefined as unknown as any, "example_base", "example_local", "example_remote", "example_output");
// Call merge_structural
merge_structural(undefined as unknown as any, "example_base_file", "example_local_file", "example_remote_file", "example_output_file");
// Call predict_conflicts
predict_conflicts(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call resolve_imports
resolve_imports(undefined as unknown as any, "example_content", "example_lang");
