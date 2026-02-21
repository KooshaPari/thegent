// Auto-generated TypeScript declarations for macos_sandbox
// Source: generate-api-docs.py

export declare class MacOSSandbox {
  constructor(profile_dir: any);
  apply_to_command(cmd: Array<string>, level: SandboxLevel, project_root: any): void;
  from_env(): void;
  generate_profile(level: SandboxLevel, project_root: string): void;
  get_profile_path(level: SandboxLevel): void;
  is_sandbox_available(): void;
  level_from_env(): void;
  level_from_settings(): void;
}

export declare class SandboxLevel extends Enum {
}

export declare function apply_to_command(cmd: Array<string>, level: SandboxLevel, project_root: any): void;
export declare function from_env(): void;
export declare function generate_profile(level: SandboxLevel, project_root: string): void;
export declare function get_profile_path(level: SandboxLevel): void;
export declare function is_sandbox_available(): void;
export declare function level_from_env(): void;
export declare function level_from_settings(): void;
