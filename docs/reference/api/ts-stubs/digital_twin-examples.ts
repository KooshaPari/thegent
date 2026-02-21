// Auto-generated usage examples for digital_twin
// Source: generate-api-docs.py

import { DigitalTwinManager, PersonaSnapshot, capture_snapshot, reconcile_twin } from "./digital_twin";

// Create a DigitalTwinManager instance
const digitaltwinmanager = new DigitalTwinManager("example_storage_dir");
digitaltwinmanager.capture_snapshot("example_identity_id", undefined as unknown as Record<(str, float)>);
digitaltwinmanager.reconcile_twin("example_twin_a_id", "example_twin_b_id");

// Create a PersonaSnapshot instance
const personasnapshot = new PersonaSnapshot();

// Call capture_snapshot
capture_snapshot(undefined as unknown as any, "example_identity_id", undefined as unknown as Record<(str, float)>);
// Call reconcile_twin
reconcile_twin(undefined as unknown as any, "example_twin_a_id", "example_twin_b_id");
