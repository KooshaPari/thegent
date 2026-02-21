// Auto-generated usage examples for drift_corrector
// Source: generate-api-docs.py

import { DriftCorrector, check_drift, correct_drift } from "./drift_corrector";

// Create a DriftCorrector instance
const driftcorrector = new DriftCorrector(undefined as unknown as InfraProvisioner);
driftcorrector.check_drift("example_resource_id", undefined as unknown as ResourceSpec);
driftcorrector.correct_drift("example_resource_id", undefined as unknown as ResourceSpec);

// Call check_drift
check_drift(undefined as unknown as any, "example_resource_id", undefined as unknown as ResourceSpec);
// Call correct_drift
correct_drift(undefined as unknown as any, "example_resource_id", undefined as unknown as ResourceSpec);
