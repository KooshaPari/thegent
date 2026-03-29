// Auto-generated usage examples for native_governance_scan
// Source: generate-api-docs.py

import { GovernanceViolation, NativeGovernanceScanner, check_contract, check_contract_content, scan_content, scan_file } from "./native_governance_scan";

// Create a GovernanceViolation instance
const governanceviolation = new GovernanceViolation();

// Create a NativeGovernanceScanner instance
const nativegovernancescanner = new NativeGovernanceScanner();
nativegovernancescanner.check_contract("example_contract_id", "example_path");
nativegovernancescanner.check_contract_content("example_contract_id", "example_content");
nativegovernancescanner.scan_content("example_content");
nativegovernancescanner.scan_file("example_path");

// Call check_contract
check_contract(undefined as unknown as any, "example_contract_id", "example_path");
// Call check_contract_content
check_contract_content(undefined as unknown as any, "example_contract_id", "example_content");
// Call scan_content
scan_content(undefined as unknown as any, "example_content");
// Call scan_file
scan_file(undefined as unknown as any, "example_path");
