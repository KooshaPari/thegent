// Auto-generated TypeScript declarations for wsl_interop
// Source: generate-api-docs.py

export declare class WslInterop {
  constructor();
  get_windows_user_profile(): void;
  map_sid_to_uid(sid: string): void;
  to_windows_path(wsl_path: string): void;
  to_wsl_path(windows_path: string): void;
}

export declare function get_windows_user_profile(): void;
export declare function map_sid_to_uid(sid: string): void;
export declare function to_windows_path(wsl_path: string): void;
export declare function to_wsl_path(windows_path: string): void;
