#!/usr/bin/env python3
"""System manifest installer - Nix-like declarative system configuration management.

Usage:
    thegent system install --bundle dev
    thegent system install --target shells.zsh
    thegent system install --all
    thegent system verify
    thegent system status
"""

import argparse
import orjson as json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

MANIFEST_PATH = Path(__file__).parent.parent.parent.parent / "templates" / "system-manifest.json"


def load_manifest(path: Optional[Path] = None) -> dict[str, Any]:
    """Load the system manifest."""
    manifest_path = path or MANIFEST_PATH
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        sys.exit(1)
    return json.loads(manifest_path.read_text())


def expand_bundle(manifest: dict[str, Any], bundle_name: str) -> list[str]:
    """Expand a bundle name to list of targets."""
    bundles = manifest.get("bundles", {})
    if bundle_name not in bundles:
        return [bundle_name]

    bundle = bundles[bundle_name]
    includes = bundle.get("includes", [])
    result = []
    for item in includes:
        if "." in item:  # It's a specific target like "shells.zsh"
            result.append(item)
        else:  # It's another bundle
            result.extend(expand_bundle(manifest, item))
    return result


def detect_installed_targets(manifest: dict[str, Any]) -> list[str]:
    """Auto-detect which targets are installed."""
    detected = []

    # Check harnesses
    harnesses = manifest.get("targets", {}).get("harnesses", {})
    for name, config in harnesses.items():
        for path_pattern in config.get("config_paths", []):
            expanded = Path(os.path.expanduser(path_pattern))
            if expanded.exists():
                detected.append(f"harnesses.{name}")
                break

    # Check shells
    shells = manifest.get("targets", {}).get("shells", {})
    for name, config in shells.items():
        for path_pattern in config.get("config_files", []):
            expanded = Path(os.path.expanduser(path_pattern))
            if expanded.exists():
                detected.append(f"shells.{name}")
                break

    # Check tools
    tools = manifest.get("targets", {}).get("tools", {})
    for name, config in tools.items():
        for path_pattern in config.get("config_files", []):
            expanded = Path(os.path.expanduser(path_pattern))
            if expanded.exists():
                detected.append(f"tools.{name}")
                break

    return detected


def install_target(
    target: str,
    manifest: dict[str, Any],
    dry_run: bool = False,
    verbose: bool = False,
    use_symlinks: bool = False,
    backup_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Install a single target.
    
    Args:
        target: Target to install (e.g., "tools.git")
        manifest: System manifest
        dry_run: If True, only show what would be done
        verbose: If True, print detailed output
        use_symlinks: If True, use symlinks instead of copying
        backup_dir: Directory to backup existing configs to
    """
    results = {"copied": 0, "skipped": 0, "errors": 0, "details": []}

    parts = target.split(".")
    if len(parts) != 2:
        print(f"Error: Invalid target format: {target} (expected category.name)")
        results["errors"] += 1
        return results

    category, name = parts
    targets = manifest.get("targets", {}).get(category, {})

    if name not in targets:
        print(f"Warning: Unknown target {target}")
        results["errors"] += 1
        return results

    config = targets[name]
    source = config.get("source")

    if not source:
        print(f"Warning: No source defined for {target}")
        results["skipped"] += 1
        return results

    # Determine source path
    thegent_root = Path(__file__).parent.parent.parent.parent
    source_path = thegent_root / source

    if not source_path.exists():
        print(f"Warning: Source path not found: {source_path}")
        results["skipped"] += 1
        return results

    # Install config files
    for path_pattern in config.get("config_files", []):
        target_path = Path(os.path.expanduser(path_pattern))

        # Backup existing config if needed
        if target_path.exists() and backup_dir:
            if not dry_run:
                backup_path = backup_dir / target_path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                if verbose:
                    print(f"  Backing up {target_path} -> {backup_path}")
                shutil.copy2(target_path, backup_path)

        if dry_run:
            if use_symlinks:
                print(f"[DRY-RUN] Would symlink {source_path} -> {target_path}")
            else:
                print(f"[DRY-RUN] Would install {source_path} -> {target_path}")
            results["skipped"] += 1
            continue

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Use symlink or copy
            if use_symlinks:
                if target_path.exists():
                    if target_path.is_symlink():
                        target_path.unlink()
                    else:
                        shutil.rmtree(target_path) if target_path.is_dir() else target_path.unlink()
                source_path = source_path.resolve()
                target_path.symlink_to(source_path)
                if verbose:
                    print(f"  Symlinked {source_path} -> {target_path}")
                results["copied"] += 1
            else:
                if source_path.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)
                if verbose:
                    print(f"  Copied {source_path} -> {target_path}")
                results["copied"] += 1
        except Exception as e:
            print(f"Error installing {target}: {e}")
            results["errors"] += 1

    return results


def verify_target(target: str, manifest: dict[str, Any]) -> dict[str, Any]:
    """Verify a target is correctly installed."""
    results = {"status": "unknown", "details": []}

    parts = target.split(".")
    if len(parts) != 2:
        results["status"] = "error"
        results["details"].append(f"Invalid target format: {target}")
        return results

    category, name = parts
    targets = manifest.get("targets", {}).get(category, {})

    if name not in targets:
        results["status"] = "error"
        results["details"].append(f"Unknown target: {target}")
        return results

    config = targets[name]
    all_exist = True

    for path_pattern in config.get("config_files", []):
        target_path = Path(os.path.expanduser(path_pattern))
        exists = target_path.exists()
        if not exists:
            all_exist = False
        results["details"].append(f"{path_pattern}: {'✓' if exists else '✗'}")

    results["status"] = "ok" if all_exist else "missing"
    return results


def cmd_install(args: argparse.Namespace) -> int:
    """Install command."""
    manifest = load_manifest(args.manifest)

    # Determine targets
    if args.all:
        targets = []
        for category in ["harnesses", "shells", "tools"]:
            for name in manifest.get("targets", {}).get(category, {}).keys():
                targets.append(f"{category}.{name}")
    elif args.bundle:
        targets = expand_bundle(manifest, args.bundle)
    elif args.target:
        targets = [args.target]
    elif args.auto:
        targets = detect_installed_targets(manifest)
    else:
        print("Error: Must specify --all, --bundle, --target, or --auto")
        return 1

    if args.verbose:
        print(f"Installing targets: {targets}")

    # Determine backup directory
    backup_dir = None
    do_backup = args.backup and not args.no_backup
    if do_backup:
        from datetime import datetime
        backup_dir = Path.home() / ".thegent" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        if not args.dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
        if args.verbose:
            print(f"Backup directory: {backup_dir}")

    total = {"copied": 0, "skipped": 0, "errors": 0}

    for target in targets:
        result = install_target(
            target,
            manifest,
            dry_run=args.dry_run,
            verbose=args.verbose,
            use_symlinks=args.symlink,
            backup_dir=backup_dir,
        )
        total["copied"] += result["copied"]
        total["skipped"] += result["skipped"]
        total["errors"] += result["errors"]

    print(f"\nResults: {total['copied']} copied, {total['skipped']} skipped, {total['errors']} errors")
    return 0 if total["errors"] == 0 else 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify command."""
    manifest = load_manifest(args.manifest)

    # Determine targets
    if args.all:
        targets = []
        for category in ["harnesses", "shells", "tools"]:
            for name in manifest.get("targets", {}).get(category, {}).keys():
                targets.append(f"{category}.{name}")
    elif args.target:
        targets = [args.target]
    else:
        targets = detect_installed_targets(manifest)

    print(f"Verifying {len(targets)} targets...\n")

    all_ok = True
    for target in targets:
        result = verify_target(target, manifest)
        status_icon = "✓" if result["status"] == "ok" else "✗"
        print(f"{status_icon} {target}: {result['status']}")
        if args.verbose:
            for detail in result["details"]:
                print(f"    {detail}")
        if result["status"] != "ok":
            all_ok = False

    return 0 if all_ok else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Status command - show what's installed vs available."""
    manifest = load_manifest(args.manifest)

    installed = detect_installed_targets(manifest)

    print("=== Installed Targets ===")
    for target in sorted(installed):
        print(f"  ✓ {target}")

    print(f"\n=== Available ({len(installed)} installed) ===")
    all_targets = []
    for category in ["harnesses", "shells", "tools"]:
        for name in manifest.get("targets", {}).get(category, {}).keys():
            full_target = f"{category}.{name}"
            if full_target not in installed:
                print(f"  ○ {full_target}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="thegent system management")
    parser.add_argument("--manifest", type=Path, help="Path to manifest file")

    subparsers = parser.add_subparsers()

    # Install command
    install_parser = subparsers.add_parser("install", help="Install system configurations")
    install_parser.add_argument("--all", action="store_true", help="Install all targets")
    install_parser.add_argument("--bundle", type=str, help="Install a bundle (core, dev, terminal, productivity, all)")
    install_parser.add_argument("--target", type=str, help="Install a specific target (e.g., shells.zsh)")
    install_parser.add_argument("--auto", action="store_true", help="Auto-detect and install")
    install_parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")
    install_parser.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying (more Nix-like)")
    install_parser.add_argument("--backup", action="store_true", default=True, help="Backup existing configs before installing (default: True)")
    install_parser.add_argument("--no-backup", action="store_true", help="Skip backing up existing configs")
    install_parser.add_argument("-v", "--verbose", action="store_true")
    install_parser.set_defaults(func=cmd_install)

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify installed configurations")
    verify_parser.add_argument("--all", action="store_true", help="Verify all targets")
    verify_parser.add_argument("--target", type=str, help="Verify a specific target")
    verify_parser.add_argument("-v", "--verbose", action="store_true")
    verify_parser.set_defaults(func=cmd_verify)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
