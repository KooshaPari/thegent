// Auto-generated usage examples for wsl_interop
// Source: generate-api-docs.py

import { WslInterop, get_windows_user_profile, map_sid_to_uid, to_windows_path, to_wsl_path } from "./wsl_interop";

// Create a WslInterop instance
const wslinterop = new WslInterop();
wslinterop.get_windows_user_profile();
wslinterop.map_sid_to_uid("example_sid");
wslinterop.to_windows_path("example_wsl_path");
wslinterop.to_wsl_path("example_windows_path");

// Call get_windows_user_profile
get_windows_user_profile(undefined as unknown as any);
// Call map_sid_to_uid
map_sid_to_uid(undefined as unknown as any, "example_sid");
// Call to_windows_path
to_windows_path(undefined as unknown as any, "example_wsl_path");
// Call to_wsl_path
to_wsl_path(undefined as unknown as any, "example_windows_path");
