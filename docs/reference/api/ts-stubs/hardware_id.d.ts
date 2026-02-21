// Auto-generated TypeScript declarations for hardware_id
// Source: generate-api-docs.py

export declare class HardwareAttestation extends BaseModel {
}

export declare class HardwareIdentityManager {
  constructor(agent_id: string);
  get_hardware_attestation(): void;
  verify_attestation(attestation: HardwareAttestation): void;
}

export declare function get_hardware_attestation(): void;
export declare function verify_attestation(attestation: HardwareAttestation): void;
