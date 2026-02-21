// Auto-generated usage examples for shm
// Source: generate-api-docs.py

import { SHMSystem, award_xp, get_shm_system, get_xp_state, is_native_active, is_open, record_failure, set_level } from "./shm";

// Create a SHMSystem instance
const shmsystem = new SHMSystem();
shmsystem.award_xp(0);
shmsystem.get_xp_state();
shmsystem.is_native_active();
shmsystem.is_open("example_target", "example_category", 0, 0, 0);
shmsystem.record_failure("example_target", "example_category");
shmsystem.set_level(0);

// Call award_xp
award_xp(undefined as unknown as any, 0);
// Call get_shm_system
get_shm_system("example_session_dir");
// Call get_xp_state
get_xp_state(undefined as unknown as any);
// Call is_native_active
is_native_active(undefined as unknown as any);
// Call is_open
is_open(undefined as unknown as any, "example_target", "example_category", 0, 0, 0);
// Call record_failure
record_failure(undefined as unknown as any, "example_target", "example_category");
// Call set_level
set_level(undefined as unknown as any, 0);
