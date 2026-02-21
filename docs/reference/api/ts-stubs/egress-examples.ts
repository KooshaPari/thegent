// Auto-generated usage examples for egress
// Source: generate-api-docs.py

import { EgressEvent, SIEMEgress, format_for_syslog, push_event } from "./egress";

// Create a EgressEvent instance
const egressevent = new EgressEvent();

// Create a SIEMEgress instance
const siemegress = new SIEMEgress(undefined as unknown as any);
siemegress.format_for_syslog(undefined as unknown as EgressEvent);
siemegress.push_event(undefined as unknown as EgressEvent);

// Call format_for_syslog
format_for_syslog(undefined as unknown as any, undefined as unknown as EgressEvent);
// Call push_event
push_event(undefined as unknown as any, undefined as unknown as EgressEvent);
