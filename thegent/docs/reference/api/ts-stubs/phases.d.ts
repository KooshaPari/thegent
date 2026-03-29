// Auto-generated TypeScript declarations for phases
// Source: generate-api-docs.py

export declare class PhaseTransitionContract {
  allowed_targets(from_state: string): void;
  validate(from_state: string, to_state: string): void;
}

export declare function allowed_targets(from_state: string): void;
export declare function validate(from_state: string, to_state: string): void;
export declare function validate_transition(from_state: string, to_state: string): void;
