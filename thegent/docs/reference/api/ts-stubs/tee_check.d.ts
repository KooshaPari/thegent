// Auto-generated TypeScript declarations for tee_check
// Source: generate-api-docs.py

export declare class TEEAttestation {
}

export declare class TEEChecker {
  constructor(mock_mode: boolean);
  check(): void;
  enforce_tee(): void;
}

export declare class TEEType extends Enum {
}

export declare function check(): void;
export declare function enforce_tee(): void;
export declare function get_tee_attestation(): void;
