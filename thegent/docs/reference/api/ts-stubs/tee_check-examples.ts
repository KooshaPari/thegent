// Auto-generated usage examples for tee_check
// Source: generate-api-docs.py

import { TEEAttestation, TEEChecker, TEEType, check, enforce_tee, get_tee_attestation } from "./tee_check";

// Create a TEEAttestation instance
const teeattestation = new TEEAttestation();

// Create a TEEChecker instance
const teechecker = new TEEChecker(false);
teechecker.check();
teechecker.enforce_tee();

// Create a TEEType instance
const teetype = new TEEType();

// Call check
check(undefined as unknown as any);
// Call enforce_tee
enforce_tee(undefined as unknown as any);
// Call get_tee_attestation
get_tee_attestation();
