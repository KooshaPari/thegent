// Auto-generated usage examples for adapter_policy
// Source: generate-api-docs.py

import { AdapterAdmissionPolicy, evaluate_admission } from "./adapter_policy";

// Create a AdapterAdmissionPolicy instance
const adapteradmissionpolicy = new AdapterAdmissionPolicy(undefined as unknown as CapabilityRegistry, 0);
adapteradmissionpolicy.evaluate_admission("example_adapter_id", "example_lane");

// Call evaluate_admission
evaluate_admission(undefined as unknown as any, "example_adapter_id", "example_lane");
