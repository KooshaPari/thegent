// Auto-generated usage examples for security
// Source: generate-api-docs.py

import { CrossPlatformSecurity, harden, run_security_check } from "./security";

// Create a CrossPlatformSecurity instance
const crossplatformsecurity = new CrossPlatformSecurity();
crossplatformsecurity.harden("example_target");
crossplatformsecurity.run_security_check("example_check_name");

// Call harden
harden(undefined as unknown as any, "example_target");
// Call run_security_check
run_security_check(undefined as unknown as any, "example_check_name");
