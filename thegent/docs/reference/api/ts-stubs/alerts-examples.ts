// Auto-generated usage examples for alerts
// Source: generate-api-docs.py

import { AlertFatigueController, InterruptionKind, get_fatigue_level, record_alert } from "./alerts";

// Create a AlertFatigueController instance
const alertfatiguecontroller = new AlertFatigueController(undefined as unknown as ThegentSettings);
alertfatiguecontroller.get_fatigue_level();
alertfatiguecontroller.record_alert(undefined as unknown as InterruptionKind);

// Create a InterruptionKind instance
const interruptionkind = new InterruptionKind();

// Call get_fatigue_level
get_fatigue_level(undefined as unknown as any);
// Call record_alert
record_alert(undefined as unknown as any, undefined as unknown as InterruptionKind);
