// Auto-generated usage examples for attestation
// Source: generate-api-docs.py

import { AttestationGenerator, AuditReportGenerator, generate_attestation, generate_monthly_report } from "./attestation";

// Create a AttestationGenerator instance
const attestationgenerator = new AttestationGenerator(undefined as unknown as ThegentSettings);
attestationgenerator.generate_attestation("example_run_id");

// Create a AuditReportGenerator instance
const auditreportgenerator = new AuditReportGenerator(undefined as unknown as ThegentSettings);
auditreportgenerator.generate_monthly_report();

// Call generate_attestation
generate_attestation(undefined as unknown as any, "example_run_id");
// Call generate_monthly_report
generate_monthly_report(undefined as unknown as any);
