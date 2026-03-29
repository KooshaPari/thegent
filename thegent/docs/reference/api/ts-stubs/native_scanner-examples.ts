// Auto-generated usage examples for native_scanner
// Source: generate-api-docs.py

import { NativeGovernanceScanner, add_trigger, scan } from "./native_scanner";

// Create a NativeGovernanceScanner instance
const nativegovernancescanner = new NativeGovernanceScanner();
nativegovernancescanner.add_trigger("example_trigger", false);
nativegovernancescanner.scan("example_content");

// Call add_trigger
add_trigger(undefined as unknown as any, "example_trigger", false);
// Call scan
scan(undefined as unknown as any, "example_content");
