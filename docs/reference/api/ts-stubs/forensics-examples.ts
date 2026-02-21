// Auto-generated usage examples for forensics
// Source: generate-api-docs.py

import { IncidentReplayer, generate_incident_report, replay } from "./forensics";

// Create a IncidentReplayer instance
const incidentreplayer = new IncidentReplayer(undefined as unknown as IncidentLedger);
incidentreplayer.generate_incident_report("example_run_id");
incidentreplayer.replay("example_run_id");

// Call generate_incident_report
generate_incident_report(undefined as unknown as any, "example_run_id");
// Call replay
replay(undefined as unknown as any, "example_run_id");
