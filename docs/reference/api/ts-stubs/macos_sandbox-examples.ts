// Auto-generated usage examples for macos_sandbox
// Source: generate-api-docs.py

import { MacOSSandbox, SandboxLevel, apply_to_command, from_env, generate_profile, get_profile_path, is_sandbox_available, level_from_env, level_from_settings } from "./macos_sandbox";

// Create a MacOSSandbox instance
const macossandbox = new MacOSSandbox(undefined as unknown as any);
macossandbox.apply_to_command(undefined as unknown as Array<string>, undefined as unknown as SandboxLevel, undefined as unknown as any);
macossandbox.from_env();
macossandbox.generate_profile(undefined as unknown as SandboxLevel, "example_project_root");
macossandbox.get_profile_path(undefined as unknown as SandboxLevel);
macossandbox.is_sandbox_available();
macossandbox.level_from_env();
macossandbox.level_from_settings();

// Create a SandboxLevel instance
const sandboxlevel = new SandboxLevel();

// Call apply_to_command
apply_to_command(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as SandboxLevel, undefined as unknown as any);
// Call from_env
from_env(undefined as unknown as any);
// Call generate_profile
generate_profile(undefined as unknown as any, undefined as unknown as SandboxLevel, "example_project_root");
// Call get_profile_path
get_profile_path(undefined as unknown as any, undefined as unknown as SandboxLevel);
// Call is_sandbox_available
is_sandbox_available(undefined as unknown as any);
// Call level_from_env
level_from_env(undefined as unknown as any);
// Call level_from_settings
level_from_settings(undefined as unknown as any);
