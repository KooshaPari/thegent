// Auto-generated usage examples for kill_switch
// Source: generate-api-docs.py

import { SafetyKillSwitch, activate, check_status, verify_alignment_drift } from "./kill_switch";

// Create a SafetyKillSwitch instance
const safetykillswitch = new SafetyKillSwitch("example_workspace_root");
safetykillswitch.activate("example_reason");
safetykillswitch.check_status();
safetykillswitch.verify_alignment_drift(0);

// Call activate
activate(undefined as unknown as any, "example_reason");
// Call check_status
check_status(undefined as unknown as any);
// Call verify_alignment_drift
verify_alignment_drift(undefined as unknown as any, 0);
