// Auto-generated TypeScript declarations for digital_twin
// Source: generate-api-docs.py

export declare class DigitalTwinManager {
  constructor(storage_dir: string);
  capture_snapshot(identity_id: string, values: Record<(str, float)>): void;
  reconcile_twin(twin_a_id: string, twin_b_id: string): void;
}

export declare class PersonaSnapshot {
}

export declare function capture_snapshot(identity_id: string, values: Record<(str, float)>): void;
export declare function reconcile_twin(twin_a_id: string, twin_b_id: string): void;
