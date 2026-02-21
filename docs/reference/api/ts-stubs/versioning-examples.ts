// Auto-generated usage examples for versioning
// Source: generate-api-docs.py

import { VersioningManager, generate_version_manifest, generate_version_switcher_html } from "./versioning";

// Create a VersioningManager instance
const versioningmanager = new VersioningManager(undefined as unknown as Array<string>);
versioningmanager.generate_version_manifest();
versioningmanager.generate_version_switcher_html("example_current_version");

// Call generate_version_manifest
generate_version_manifest(undefined as unknown as any);
// Call generate_version_switcher_html
generate_version_switcher_html(undefined as unknown as any, "example_current_version");
