"""Bundle manifest loading and path resolution helpers for install workflows."""

import orjson as json
import os
from pathlib import Path
from typing import Any

from thegent.install_models import BundleItem, BundleManifest, InstallMode


def coerce_path(value: str) -> Path:
    """Normalize and expand a user path token."""
    return Path(os.path.expandvars(value)).expanduser()


def source_requires_pin_and_checksum(source: str) -> bool:
    """Determine whether a source should include immutable pin/checksum metadata."""
    normalized = source.strip().lower()
    return normalized.startswith(("http://", "https://", "git+", "github:"))


def get_default_bundle_manifest_path() -> Path:
    """Default location for the third-party bundle manifest."""
    return Path.home() / ".config" / "thegent" / "third_party_bundles.json"


def get_bundle_manifest_path(bundle_manifest: Path | str | None = None) -> Path:
    """Get the bundle manifest path."""
    if bundle_manifest is not None:
        return coerce_path(str(bundle_manifest))
    return get_default_bundle_manifest_path()


def load_bundle_manifest(path: Path | str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Load third-party bundle definitions from an external JSON manifest."""
    manifest_path = coerce_path(str(path)) if path is not None else get_default_bundle_manifest_path()

    if not manifest_path.exists():
        return {}

    try:
        data = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError, ValueError):
        return {}

    raw_bundles = data.get("bundles") if isinstance(data, dict) else None
    if not isinstance(raw_bundles, dict):
        return {}

    bundles: dict[str, list[dict[str, Any]]] = {}
    for name, bundle in raw_bundles.items():
        if not isinstance(name, str):
            continue
        raw_items = bundle.get("items") if isinstance(bundle, dict) else bundle

        if not isinstance(raw_items, list):
            continue

        items: list[dict[str, Any]] = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue

            source = raw.get("source")
            target = raw.get("target")
            if not isinstance(source, str) or not isinstance(target, str):
                continue

            item: dict[str, Any] = {
                "source": source.strip(),
                "target": target.strip(),
            }
            mode = raw.get("mode")
            if isinstance(mode, str) and mode.strip():
                item["mode"] = mode.strip().lower()
            else:
                item["mode"] = ""
            pin = raw.get("pin")
            if isinstance(pin, str) and pin.strip():
                item["pin"] = pin.strip()
            checksum = raw.get("checksum")
            if isinstance(checksum, str) and checksum.strip():
                item["checksum"] = checksum.strip()
            items.append(item)

        if items:
            bundles[name] = items

    return bundles


def list_bundle_names(bundle_manifest: Path | str | None = None) -> list[str]:
    """List available bundle names from the bundle manifest."""
    manifest = load_bundle_manifest(bundle_manifest)
    return list(manifest.keys())


def validate_bundle_manifest(bundle_manifest: Path | str | None = None) -> tuple[bool, list[str]]:
    """Validate a bundle manifest file."""
    issues: list[str] = []
    manifest_path = bundle_manifest or get_default_bundle_manifest_path()

    if manifest_path and isinstance(manifest_path, (str | Path)):
        path = Path(manifest_path) if not isinstance(manifest_path, Path) else manifest_path
        if not path.exists():
            issues.append(f"Bundle manifest not found: {path}")
            return False, issues

        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError, ValueError) as e:
            issues.append(f"Failed to parse bundle manifest: {e}")
            return False, issues

        if not isinstance(data, dict):
            issues.append("Bundle manifest must be a JSON object")
            return False, issues

        bundles = data.get("bundles")
        if not isinstance(bundles, dict):
            issues.append("Bundle manifest must have a 'bundles' object")
            return False, issues

        for name, bundle in bundles.items():
            if not isinstance(name, str):
                issues.append("Bundle name must be a string")
                continue
            if not isinstance(bundle, dict):
                issues.append(f"Bundle '{name}' must be an object")
                continue
            items = bundle.get("items")
            if not isinstance(items, list):
                issues.append(f"Bundle '{name}' must have an 'items' array")
                continue
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    issues.append(f"Bundle '{name}' item {i} must be an object")
                    continue
                if "source" not in item:
                    issues.append(f"Bundle '{name}' item {i} missing 'source'")
                if "target" not in item:
                    issues.append(f"Bundle '{name}' item {i} missing 'target'")
                source = item.get("source")
                if isinstance(source, str) and source_requires_pin_and_checksum(source):
                    pin = item.get("pin")
                    checksum = item.get("checksum")
                    if not isinstance(pin, str) or not pin.strip():
                        issues.append(f"Bundle '{name}' item {i} requires non-empty 'pin' for external source")
                    if not isinstance(checksum, str) or not checksum.strip():
                        issues.append(f"Bundle '{name}' item {i} requires non-empty 'checksum' for external source")

    return len(issues) == 0, issues


def coerce_bundle_items(raw: dict[str, list[dict[str, Any]]]) -> BundleManifest:
    """Normalize raw manifest payloads into a validated structure."""
    normalized: dict[str, list[BundleItem]] = {}
    for name, items in raw.items():
        if not name or not isinstance(items, list):
            continue
        parsed_items: list[BundleItem] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            source = item.get("source")
            target = item.get("target")
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            parsed_items.append(
                BundleItem(
                    source=source.strip(),
                    target=target.strip(),
                    mode=str(item.get("mode", "")).strip().lower(),
                    pin=str(item.get("pin")).strip() if isinstance(item.get("pin"), str) else None,
                    checksum=str(item.get("checksum")).strip() if isinstance(item.get("checksum"), str) else None,
                )
            )
        if parsed_items:
            normalized[name] = parsed_items
    return BundleManifest(bundles=normalized)


def resolve_bundle_mode(raw_mode: str, fallback: InstallMode) -> InstallMode:
    """Convert a user-defined bundle mode into an InstallMode."""
    normalized = (raw_mode or "").strip().lower()
    if normalized in {"", "copy"}:
        return fallback
    if normalized == "symlink":
        return InstallMode.EDITABLE
    try:
        return InstallMode(normalized)
    except ValueError:
        return fallback


def resolve_bundle_source(source: str, thegent_root: Path) -> Path:
    """Resolve a bundle source path."""
    normalized = source.strip()
    if normalized.startswith("thegent:"):
        normalized = normalized.split(":", 1)[1].lstrip("/")
        return thegent_root / normalized

    expanded = coerce_path(normalized)
    if expanded.is_absolute():
        return expanded
    return thegent_root / expanded


def resolve_bundle_target(target: str, *, home: Path, cwd: Path) -> Path:
    """Resolve a bundle target path."""
    normalized = target.strip()
    normalized = normalized.replace("{home}", str(home)).replace("{HOME}", str(home))
    normalized = normalized.replace("{cwd}", str(cwd)).replace("{CWD}", str(cwd))
    normalized = normalized.replace("${HOME}", str(home)).replace("${CWD}", str(cwd))
    normalized = os.path.expandvars(normalized)

    expanded = coerce_path(normalized)
    if expanded.is_absolute():
        return expanded
    return home / expanded


def resolve_bundles(
    bundle_names: list[str] | None,
    bundle_manifest: Path | str | None,
    thegent_root: Path,
    home: Path,
    cwd: Path,
    fallback_mode: InstallMode,
) -> list[tuple[Path, Path, InstallMode]]:
    """Resolve selected bundles to install tuples."""
    selected = list(bundle_names or [])
    if not selected:
        return []

    manifest = coerce_bundle_items(load_bundle_manifest(bundle_manifest)).bundles
    include_all = "all" in selected

    missing = [name for name in selected if name != "all" and name not in manifest]
    if missing:
        known = ", ".join(sorted(manifest))
        hint = f"Known: {known}" if known else "No bundles available"
        raise ValueError(f"Unknown bundle(s): {', '.join(missing)}. {hint}")

    resolved_items: list[tuple[Path, Path, InstallMode]] = []
    names_to_apply: list[str]
    if include_all:
        names_to_apply = list(manifest.keys())
    else:
        seen: set[str] = set()
        names_to_apply = []
        for name in selected:
            if name in seen:
                continue
            seen.add(name)
            names_to_apply.append(name)

    for name in names_to_apply:
        for item in manifest[name]:
            source = resolve_bundle_source(item.source, thegent_root)
            target = resolve_bundle_target(item.target, home=home, cwd=cwd)
            mode = resolve_bundle_mode(item.mode, fallback_mode)
            resolved_items.append((source, target, mode))
    return resolved_items
