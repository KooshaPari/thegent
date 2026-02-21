// Auto-generated usage examples for slo
// Source: generate-api-docs.py

import { SLORegulator, is_compliant, record_execution } from "./slo";

// Create a SLORegulator instance
const sloregulator = new SLORegulator(0, 0);
sloregulator.is_compliant();
sloregulator.record_execution(0, false);

// Call is_compliant
is_compliant(undefined as unknown as any);
// Call record_execution
record_execution(undefined as unknown as any, 0, false);
