// Auto-generated TypeScript declarations for install
// Source: generate-api-docs.py

export declare class BundleItem extends BaseModel {
}

export declare class BundleManifest extends BaseModel {
}

export declare class ConfigManifest extends BaseModel {
}

export declare class FileAction extends StrEnum {
}

export declare class FileManifest extends BaseModel {
}

export declare class InstallManager {
  constructor(dry_run: boolean, verbose: boolean);
  install_file(source: string, target: string, mode: InstallMode): void;
  save_manifest(): void;
  uninstall(): void;
  update_config(config_path: string, key_path: string, value: any): void;
}

export declare class InstallManifest extends BaseModel {
}

export declare class InstallMode extends StrEnum {
}

export declare function cleanup_old_backups(keep_count: number, console: any): void;
export declare function clone_git_repo(repo_url: string, target_dir: string, console: any, dry_run: boolean, branch: any): void;
export declare function create_symlink(source: string, target: string, dry_run: boolean): void;
export declare function get_backup_dir(): string;
export declare function get_bundle_manifest_path(bundle_manifest: any): void;
export declare function get_default_bundle_manifest_path(): void;
export declare function get_home_dir(): string;
export declare function get_manifest_path(): string;
export declare function get_source_dest_mapping(thegent_root: string, bundle: string): void;
export declare function install_file(source: string, target: string, mode: InstallMode): FileAction;
export declare function install_homebrew(console: any, dry_run: boolean): void;
export declare function install_mise(console: any, dry_run: boolean, use_nix: boolean, settings: ThegentSettings | None): void;
export declare function install_system_dependencies(console: any, dry_run: boolean, install_homebrew_pkg: boolean, install_mise_pkg: boolean, use_nix: boolean, git_repos: any): void;
export declare function list_backups(console: any): void;
export declare function list_bundle_names(bundle_manifest: any): void;
export declare function load_bundle_manifest(path: any): void;
export declare function resolve_bundles(bundle_names: any, bundle_manifest: any, thegent_root: string, home: string, cwd: string, fallback_mode: InstallMode): void;
export declare function restore_shell_config(backup_path: string, console: any): void;
export declare function run_install(target: string, mode: string, dry_run: boolean, verbose: boolean, url: any, install_service: boolean, bundles: any, bundle_manifest: any, bundle_conflict_policy: any, settings: ThegentSettings | None): Record<string, unknown>;
export declare function run_install_system(prefix: string, dry_run: boolean, verbose: boolean): void;
export declare function run_wizard(url: any): void;
export declare function save_manifest(): void;
export declare function service_install(): [(bool, str)];
export declare function service_start(): [(bool, str)];
export declare function service_uninstall(): [(bool, str)];
export declare function setup_harness(verbose: boolean): void;
export declare function setup_hooks(cwd: any, dry_run: boolean, verbose: boolean): void;
export declare function setup_rust_dispatcher(verbose: boolean): void;
export declare function setup_skills(cwd: any, template: string, dry_run: boolean, verbose: boolean): void;
export declare function should_exclude(path: any): void;
export declare function smart_copy_file(source: string, target: string, dry_run: boolean): void;
export declare function uninstall(): Record<(str, int)>;
export declare function uninstall_mise_hooks(console: any, dry_run: boolean, settings: ThegentSettings | None): void;
export declare function uninstall_system_dependencies(console: any, dry_run: boolean, uninstall_mise_pkg: boolean, remove_hooks: boolean): void;
export declare function update_config(config_path: string, key_path: string, value: any): void;
export declare function validate_bundle_manifest(bundle_manifest: any): void;
export declare function verify_mise_installation(console: any, settings: ThegentSettings | None): void;
