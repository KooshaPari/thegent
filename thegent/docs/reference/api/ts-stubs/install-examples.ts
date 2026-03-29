// Auto-generated usage examples for install
// Source: generate-api-docs.py

import { BundleItem, BundleManifest, ConfigManifest, FileAction, FileManifest, InstallManager, InstallManifest, InstallMode, cleanup_old_backups, clone_git_repo, create_symlink, get_backup_dir, get_bundle_manifest_path, get_default_bundle_manifest_path, get_home_dir, get_manifest_path, get_source_dest_mapping, install_file, install_homebrew, install_mise, install_system_dependencies, list_backups, list_bundle_names, load_bundle_manifest, resolve_bundles, restore_shell_config, run_install, run_install_system, run_wizard, save_manifest, service_install, service_start, service_uninstall, setup_harness, setup_hooks, setup_rust_dispatcher, setup_skills, should_exclude, smart_copy_file, uninstall, uninstall_mise_hooks, uninstall_system_dependencies, update_config, validate_bundle_manifest, verify_mise_installation } from "./install";

// Create a BundleItem instance
const bundleitem = new BundleItem();

// Create a BundleManifest instance
const bundlemanifest = new BundleManifest();

// Create a ConfigManifest instance
const configmanifest = new ConfigManifest();

// Create a FileAction instance
const fileaction = new FileAction();

// Create a FileManifest instance
const filemanifest = new FileManifest();

// Create a InstallManager instance
const installmanager = new InstallManager(false, false);
installmanager.install_file("example_source", "example_target", undefined as unknown as InstallMode);
installmanager.save_manifest();
installmanager.uninstall();
installmanager.update_config("example_config_path", "example_key_path", undefined as unknown as any);

// Create a InstallManifest instance
const installmanifest = new InstallManifest();

// Create a InstallMode instance
const installmode = new InstallMode();

// Call cleanup_old_backups
cleanup_old_backups(0, undefined as unknown as any);
// Call clone_git_repo
clone_git_repo("example_repo_url", "example_target_dir", undefined as unknown as any, false, undefined as unknown as any);
// Call create_symlink
create_symlink("example_source", "example_target", false);
// Call get_backup_dir
get_backup_dir();
// Call get_bundle_manifest_path
get_bundle_manifest_path(undefined as unknown as any);
// Call get_default_bundle_manifest_path
get_default_bundle_manifest_path();
// Call get_home_dir
get_home_dir();
// Call get_manifest_path
get_manifest_path();
// Call get_source_dest_mapping
get_source_dest_mapping("example_thegent_root", "example_bundle");
// Call install_file
install_file(undefined as unknown as any, "example_source", "example_target", undefined as unknown as InstallMode);
// Call install_homebrew
install_homebrew(undefined as unknown as any, false);
// Call install_mise
install_mise(undefined as unknown as any, false, false, undefined as unknown as ThegentSettings | None);
// Call install_system_dependencies
install_system_dependencies(undefined as unknown as any, false, false, false, false, undefined as unknown as any);
// Call list_backups
list_backups(undefined as unknown as any);
// Call list_bundle_names
list_bundle_names(undefined as unknown as any);
// Call load_bundle_manifest
load_bundle_manifest(undefined as unknown as any);
// Call resolve_bundles
resolve_bundles(undefined as unknown as any, undefined as unknown as any, "example_thegent_root", "example_home", "example_cwd", undefined as unknown as InstallMode);
// Call restore_shell_config
restore_shell_config("example_backup_path", undefined as unknown as any);
// Call run_install
run_install("example_target", "example_mode", false, false, undefined as unknown as any, false, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as ThegentSettings | None);
// Call run_install_system
run_install_system("example_prefix", false, false);
// Call run_wizard
run_wizard(undefined as unknown as any);
// Call save_manifest
save_manifest(undefined as unknown as any);
// Call service_install
service_install();
// Call service_start
service_start();
// Call service_uninstall
service_uninstall();
// Call setup_harness
setup_harness(false);
// Call setup_hooks
setup_hooks(undefined as unknown as any, false, false);
// Call setup_rust_dispatcher
setup_rust_dispatcher(false);
// Call setup_skills
setup_skills(undefined as unknown as any, "example_template", false, false);
// Call should_exclude
should_exclude(undefined as unknown as any);
// Call smart_copy_file
smart_copy_file("example_source", "example_target", false);
// Call uninstall
uninstall(undefined as unknown as any);
// Call uninstall_mise_hooks
uninstall_mise_hooks(undefined as unknown as any, false, undefined as unknown as ThegentSettings | None);
// Call uninstall_system_dependencies
uninstall_system_dependencies(undefined as unknown as any, false, false, false);
// Call update_config
update_config(undefined as unknown as any, "example_config_path", "example_key_path", undefined as unknown as any);
// Call validate_bundle_manifest
validate_bundle_manifest(undefined as unknown as any);
// Call verify_mise_installation
verify_mise_installation(undefined as unknown as any, undefined as unknown as ThegentSettings | None);
