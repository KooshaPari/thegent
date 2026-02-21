// Auto-generated usage examples for jetbrains_cli
// Source: generate-api-docs.py

import { JetBrainsCLI, diff, format, inspect, merge } from "./jetbrains_cli";

// Create a JetBrainsCLI instance
const jetbrainscli = new JetBrainsCLI(undefined as unknown as any);
jetbrainscli.diff("example_file1", "example_file2");
jetbrainscli.format(undefined as unknown as Array<string>, undefined as unknown as any);
jetbrainscli.inspect("example_project_root", undefined as unknown as any);
jetbrainscli.merge("example_file1", "example_file2", "example_base", "example_output");

// Call diff
diff(undefined as unknown as any, "example_file1", "example_file2");
// Call format
format(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as any);
// Call inspect
inspect(undefined as unknown as any, "example_project_root", undefined as unknown as any);
// Call merge
merge(undefined as unknown as any, "example_file1", "example_file2", "example_base", "example_output");
