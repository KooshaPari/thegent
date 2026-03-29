// Auto-generated usage examples for native_secret_scan
// Source: generate-api-docs.py

import { SecretMatch, scan_secrets, scan_secrets_file } from "./native_secret_scan";

// Create a SecretMatch instance
const secretmatch = new SecretMatch();

// Call scan_secrets
scan_secrets("example_content");
// Call scan_secrets_file
scan_secrets_file(undefined as unknown as any);
