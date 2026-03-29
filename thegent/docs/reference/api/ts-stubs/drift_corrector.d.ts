// Auto-generated TypeScript declarations for drift_corrector
// Source: generate-api-docs.py

export declare class DriftCorrector {
  constructor(provisioner: InfraProvisioner);
  check_drift(resource_id: string, target_spec: ResourceSpec): void;
  correct_drift(resource_id: string, target_spec: ResourceSpec): void;
}

export declare function check_drift(resource_id: string, target_spec: ResourceSpec): void;
export declare function correct_drift(resource_id: string, target_spec: ResourceSpec): void;
