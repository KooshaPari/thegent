// Auto-generated usage examples for compliance_reports
// Source: generate-api-docs.py

import { ComplianceReporter, export_report, generate_report } from "./compliance_reports";

// Create a ComplianceReporter instance
const compliancereporter = new ComplianceReporter();
compliancereporter.export_report(undefined as unknown as Record<(str, Any)>, "example_output_path", "example_format");
compliancereporter.generate_report(undefined as unknown as Record<(str, Any)>, "example_format");

// Call export_report
export_report(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, "example_output_path", "example_format");
// Call generate_report
generate_report(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, "example_format");
