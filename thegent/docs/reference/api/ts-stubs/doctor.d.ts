// Auto-generated TypeScript declarations for doctor
// Source: generate-api-docs.py

export declare class DoctorCheck {
  apply_fix(): void;
}

export declare class DoctorRunner {
  apply_fixes(checks: Array<DoctorCheck>): void;
  run_checks(): void;
}

export declare function apply_fix(): void;
export declare function apply_fixes(checks: Array<DoctorCheck>): void;
export declare function run_checks(): void;
