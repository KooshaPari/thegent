// Auto-generated usage examples for traceability
// Source: generate-api-docs.py

import { TraceabilityAuditor, TraceabilityReport, audit, generate_markdown_report } from "./traceability";

// Create a TraceabilityAuditor instance
const traceabilityauditor = new TraceabilityAuditor("example_root_dir");
traceabilityauditor.audit(undefined as unknown as Array<string>);
traceabilityauditor.generate_markdown_report(undefined as unknown as TraceabilityReport);

// Create a TraceabilityReport instance
const traceabilityreport = new TraceabilityReport();

// Call audit
audit(undefined as unknown as any, undefined as unknown as Array<string>);
// Call generate_markdown_report
generate_markdown_report(undefined as unknown as any, undefined as unknown as TraceabilityReport);
