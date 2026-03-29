// Auto-generated usage examples for watch_mode
// Source: generate-api-docs.py

import { DocumentationWatcher, start, stop } from "./watch_mode";

// Create a DocumentationWatcher instance
const documentationwatcher = new DocumentationWatcher("example_source_dir", "example_output_dir", undefined as unknown as Callable);
documentationwatcher.start(0);
documentationwatcher.stop();

// Call start
start(undefined as unknown as any, 0);
// Call stop
stop(undefined as unknown as any);
