// Auto-generated usage examples for enterprise_compliance_tests
// Source: generate-api-docs.py

import { EnterpriseComplianceTestMatrix, get_compliance_status, run_test } from "./enterprise_compliance_tests";

// Create a EnterpriseComplianceTestMatrix instance
const enterprisecompliancetestmatrix = new EnterpriseComplianceTestMatrix();
enterprisecompliancetestmatrix.get_compliance_status();
enterprisecompliancetestmatrix.run_test("example_test_id");

// Call get_compliance_status
get_compliance_status(undefined as unknown as any);
// Call run_test
run_test(undefined as unknown as any, "example_test_id");
