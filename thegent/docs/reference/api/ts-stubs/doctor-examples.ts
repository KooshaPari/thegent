// Auto-generated usage examples for doctor
// Source: generate-api-docs.py

import { DoctorCheck, DoctorRunner, apply_fix, apply_fixes, run_checks } from "./doctor";

// Create a DoctorCheck instance
const doctorcheck = new DoctorCheck();
doctorcheck.apply_fix();

// Create a DoctorRunner instance
const doctorrunner = new DoctorRunner();
doctorrunner.apply_fixes(undefined as unknown as Array<DoctorCheck>);
doctorrunner.run_checks();

// Call apply_fix
apply_fix(undefined as unknown as any);
// Call apply_fixes
apply_fixes(undefined as unknown as any, undefined as unknown as Array<DoctorCheck>);
// Call run_checks
run_checks(undefined as unknown as any);
