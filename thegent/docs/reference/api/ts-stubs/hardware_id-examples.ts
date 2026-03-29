// Auto-generated usage examples for hardware_id
// Source: generate-api-docs.py

import { HardwareAttestation, HardwareIdentityManager, get_hardware_attestation, verify_attestation } from "./hardware_id";

// Create a HardwareAttestation instance
const hardwareattestation = new HardwareAttestation();

// Create a HardwareIdentityManager instance
const hardwareidentitymanager = new HardwareIdentityManager("example_agent_id");
hardwareidentitymanager.get_hardware_attestation();
hardwareidentitymanager.verify_attestation(undefined as unknown as HardwareAttestation);

// Call get_hardware_attestation
get_hardware_attestation(undefined as unknown as any);
// Call verify_attestation
verify_attestation(undefined as unknown as any, undefined as unknown as HardwareAttestation);
