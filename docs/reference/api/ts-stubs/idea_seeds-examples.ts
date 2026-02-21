// Auto-generated usage examples for idea_seeds
// Source: generate-api-docs.py

import { IdeaSeed, IdeaSeedScanner, export_markdown, filter_by_type, scan_directory, scan_file, seeds_add_to_workstream, seeds_export, seeds_scan, to_dict, to_work_stream_items } from "./idea_seeds";

// Create a IdeaSeed instance
const ideaseed = new IdeaSeed();
ideaseed.to_dict();

// Create a IdeaSeedScanner instance
const ideaseedscanner = new IdeaSeedScanner(0);
ideaseedscanner.export_markdown(undefined as unknown as Array<IdeaSeed>, "example_output");
ideaseedscanner.filter_by_type(undefined as unknown as Array<IdeaSeed>, undefined as unknown as Array<string>);
ideaseedscanner.scan_directory("example_root", undefined as unknown as any);
ideaseedscanner.scan_file("example_path");
ideaseedscanner.to_work_stream_items(undefined as unknown as Array<IdeaSeed>);

// Call export_markdown
export_markdown(undefined as unknown as any, undefined as unknown as Array<IdeaSeed>, "example_output");
// Call filter_by_type
filter_by_type(undefined as unknown as any, undefined as unknown as Array<IdeaSeed>, undefined as unknown as Array<string>);
// Call scan_directory
scan_directory(undefined as unknown as any, "example_root", undefined as unknown as any);
// Call scan_file
scan_file(undefined as unknown as any, "example_path");
// Call seeds_add_to_workstream
seeds_add_to_workstream("example_directory", "example_workstream", "example_types", false);
// Call seeds_export
seeds_export("example_directory", "example_output", "example_types", "example_extensions");
// Call seeds_scan
seeds_scan("example_directory", "example_types", "example_extensions", false);
// Call to_dict
to_dict(undefined as unknown as any);
// Call to_work_stream_items
to_work_stream_items(undefined as unknown as any, undefined as unknown as Array<IdeaSeed>);
