"""Skills auto-discovery system for thegent.

This module provides functionality to discover, load, and validate skills
from both `.thegent/skills/` and `~/.thegent/skills/` directories.
"""

import orjson as json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _get_thegent_root() -> Path:
    """Return thegent root (has skills/). Works for dev and installed package."""
    try:
        import importlib.resources

        import thegent

        # Try to find skills in the package
        try:
            ref = importlib.resources.files(thegent)
            pkg_root = Path(str(ref)).parent.parent  # thegent/package/
            skills_dir = pkg_root / "skills"
            if skills_dir.exists():
                return pkg_root
        except Exception:
            pass
    except ImportError:
        pass

    return Path(__file__).resolve().parent.parent.parent


def _get_user_skills_dir() -> Path:
    """Return user's skills directory (~/.thegent/skills/)."""
    home = Path.home()
    return home / ".thegent" / "skills"


def _get_all_skills_dirs() -> list[Path]:
    """Return all skills directories to scan, in priority order."""
    dirs = []

    # User's skills directory takes priority (~/.thegent/skills/)
    user_skills = _get_user_skills_dir()
    if user_skills.exists():
        dirs.append(user_skills)

    # Project/system skills directory (.thegent/skills/)
    root = _get_thegent_root()
    skills_dir = root / "skills"
    if skills_dir.exists():
        dirs.append(skills_dir)

    return dirs


@dataclass
class SkillInfo:
    """Information about a discovered skill."""

    name: str
    description: str
    version: str
    entrypoint: str
    path: Path
    skill_md_path: Path
    skill_json_path: Path


def _resolve_skill_md_path(skill_dir: Path) -> Path | None:
    """Resolve the primary markdown instructions file for a skill."""
    preferred = skill_dir / "SKILL.md"
    if preferred.exists():
        return preferred

    md_files = sorted(skill_dir.glob("*.md"))
    if md_files:
        return md_files[0]
    return None


def _load_skill_manifest(skill_dir: Path, skill_json_path: Path) -> dict[str, Any]:
    """Load optional ``skill.json`` metadata, falling back to SKILL.md-only defaults."""
    if not skill_json_path.exists():
        return {
            "name": skill_dir.name,
            "description": "",
            "version": "1.0.0",
            "entrypoint": "",
        }

    with open(skill_json_path) as f:
        data = json.load(f)
    return {
        "name": data.get("name", skill_dir.name),
        "description": data.get("description", ""),
        "version": data.get("version", "1.0.0"),
        "entrypoint": data.get("entrypoint", ""),
    }


def discover_skills() -> list[SkillInfo]:
    """Discover all skills in both ~/.thegent/skills/ and .thegent/skills/.

    User's skills directory (~/.thegent/skills/) takes priority over
    project/system skills if there are name collisions.

    Returns:
        List of SkillInfo objects for each discovered skill.
    """
    skills: list[SkillInfo] = []
    seen_names: dict[str, bool] = {}  # Track seen skill names to handle priority

    for skills_dir in _get_all_skills_dirs():
        if not skills_dir.exists():
            continue

        for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name):
            if not entry.is_dir():
                continue

            # Skip if we've already seen this skill name (user dir takes priority)
            if entry.name in seen_names:
                continue

            skill_json_path = entry / "skill.json"
            skill_md_path = _resolve_skill_md_path(entry)
            if skill_md_path is None:
                logger.warning(f"Skill {entry.name} has no .md file")
                continue

            try:
                manifest = _load_skill_manifest(entry, skill_json_path)
                skill_name = str(manifest["name"]).strip()
                if not skill_name:
                    logger.error(f"Skill {entry.name} has empty name in manifest")
                    continue
                if skill_name in seen_names:
                    continue

                skill_info = SkillInfo(
                    name=skill_name,
                    description=str(manifest["description"]),
                    version=str(manifest["version"]),
                    entrypoint=str(manifest["entrypoint"]),
                    path=entry,
                    skill_md_path=skill_md_path,
                    skill_json_path=skill_json_path,
                )
                skills.append(skill_info)
                seen_names[skill_name] = True
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse skill.json for {entry.name}: {e}")
            except Exception as e:
                logger.error(f"Failed to load skill {entry.name}: {e}")

    return skills


def load_skill(skill_name: str) -> dict[str, Any] | None:
    """Load skill content by name.

    Searches in both ~/.thegent/skills/ and .thegent/skills/.
    User's skills directory takes priority.

    Args:
        skill_name: Name of the skill to load.

    Returns:
        Dictionary with skill info and content, or None if not found.
    """
    skill_name = skill_name.strip()
    if not skill_name:
        logger.warning("Skill name cannot be empty")
        return None

    # Search in priority order
    for skills_dir in _get_all_skills_dirs():
        skill_path = skills_dir / skill_name

        if not skill_path.exists():
            continue

        try:
            skill_json_path = skill_path / "skill.json"
            skill_manifest = _load_skill_manifest(skill_path, skill_json_path)

            # Find SKILL.md or any .md file
            skill_md_path = _resolve_skill_md_path(skill_path)

            skill_content = ""
            if skill_md_path and skill_md_path.exists():
                skill_content = skill_md_path.read_text()

            return {
                "name": skill_manifest.get("name", skill_name),
                "description": skill_manifest.get("description", ""),
                "version": skill_manifest.get("version", "1.0.0"),
                "entrypoint": skill_manifest.get("entrypoint", ""),
                "path": str(skill_path),
                "content": skill_content,
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse skill.json for {skill_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load skill {skill_name}: {e}")
            return None

    logger.warning(f"Skill not found: {skill_name}")
    return None


def validate_skill(skill_path: Path | str) -> dict[str, Any]:
    """Validate a skill directory.

    Args:
        skill_path: Path to the skill directory.

    Returns:
        Dictionary with validation results:
        - valid: bool
        - errors: list of error messages
        - warnings: list of warning messages
    """
    if isinstance(skill_path, str):
        skill_path = Path(skill_path)

    result: dict[str, Any] = {"valid": True, "errors": [], "warnings": []}

    if not skill_path.exists():
        result["valid"] = False
        result["errors"].append(f"Skill path does not exist: {skill_path}")
        return result

    if not skill_path.is_dir():
        result["valid"] = False
        result["errors"].append(f"Skill path is not a directory: {skill_path}")
        return result

    # Check for skill.json (optional for SKILL.md-only compatibility)
    skill_json_path = skill_path / "skill.json"
    if not skill_json_path.exists():
        result["warnings"].append("Missing skill.json (using SKILL.md-only compatibility mode)")
    else:
        try:
            with open(skill_json_path) as f:
                data = json.load(f)

            # Check required fields
            required_fields = ["name", "description", "version", "entrypoint"]
            for field in required_fields:
                if field not in data:
                    result["warnings"].append(f"Missing recommended field in skill.json: {field}")

            # Validate version format
            version = data.get("version", "")
            if version and not _is_valid_version(version):
                result["warnings"].append(f"Non-standard version format: {version}")

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON in skill.json: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error reading skill.json: {e}")

    # Check for SKILL.md or any .md file
    md_files = list(skill_path.glob("*.md"))
    if not md_files:
        result["warnings"].append("No .md file found (SKILL.md recommended)")
    # Check if SKILL.md exists (preferred)
    elif not (skill_path / "SKILL.md").exists():
        result["warnings"].append("SKILL.md not found (consider renaming main .md file)")

    return result


def _is_valid_version(version: str) -> bool:
    """Check if version string follows semver-like format."""
    parts = version.split(".")
    if len(parts) < 2:
        return False
    return all(part.isdigit() for part in parts)


def get_skill_content(skill_name: str) -> str | None:
    """Get the SKILL.md content for injection into agent prompts.

    This function loads a skill and returns its content (SKILL.md)
    for injection into the system prompt.

    Args:
        skill_name: Name of the skill to load.

    Returns:
        The skill's markdown content, or None if not found.
    """
    skill = load_skill(skill_name)
    if skill:
        return skill.get("content", "")
    return None


# ---------------------------------------------------------------------------
# SKILL.md spec-compatible discovery (WL-101)
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)


class SkillManifest(BaseModel, frozen=True):
    """Immutable manifest for a discovered skill."""

    name: str
    description: str = ""
    instructions: str = ""
    source_path: str = ""
    tags: list[str] = Field(default_factory=list)


def _parse_skill_md(path: Path) -> SkillManifest:
    """Parse a SKILL.md file into a SkillManifest."""
    text = path.read_text(encoding="utf-8")
    match = _H1_RE.search(text)
    name = match.group(1).strip() if match else path.parent.name
    # Instructions = everything after the first H1 line
    if match:
        instructions = text[match.end() :].strip()
    else:
        instructions = text.strip()
    return SkillManifest(
        name=name,
        instructions=instructions,
        source_path=str(path),
    )


def _parse_skill_json(path: Path) -> SkillManifest:
    """Parse a skill.json file into a SkillManifest."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return SkillManifest(
        name=data["name"],
        description=data.get("description", ""),
        instructions=data.get("instructions", ""),
        source_path=str(path),
        tags=data.get("tags", []),
    )


def _parse_skill_yaml(path: Path) -> SkillManifest:
    """Parse a skill.yaml file into a SkillManifest."""
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SkillManifest(
        name=data["name"],
        description=data.get("description", ""),
        instructions=data.get("instructions", ""),
        source_path=str(path),
        tags=data.get("tags", []),
    )


_PARSERS: dict[str, Any] = {
    "SKILL.md": _parse_skill_md,
    "skill.json": _parse_skill_json,
    "skill.yaml": _parse_skill_yaml,
}

_DEFAULT_SEARCH_DIRS: list[str] = [
    ".thegent/skills/",
    "~/.thegent/skills/",
]


class SkillDiscovery:
    """Scan directories for SKILL.md, skill.json, skill.yaml files."""

    def __init__(self, search_dirs: list[Path | str] | None = None) -> None:
        if search_dirs is None:
            self._dirs = [Path(d).expanduser() for d in _DEFAULT_SEARCH_DIRS]
        else:
            self._dirs = [Path(d) for d in search_dirs]

    def discover(self) -> list[SkillManifest]:
        """Scan each search directory for skill manifest files."""
        manifests: list[SkillManifest] = []
        for d in self._dirs:
            if not d.exists():
                continue
            for filename, parser in _PARSERS.items():
                candidate = d / filename
                if candidate.is_file():
                    manifests.append(parser(candidate))
        return manifests

    def find(self, name: str) -> SkillManifest:
        """Find a skill by exact name. Raises KeyError if not found."""
        for manifest in self.discover():
            if manifest.name == name:
                return manifest
        msg = f"Skill not found: {name!r}"
        raise KeyError(msg)


class SkillActivator:
    """Activate skills by injecting their instructions into a system prompt."""

    def __init__(self, discovery: SkillDiscovery) -> None:
        self._discovery = discovery

    def activate(self, name: str, system_prompt: str) -> str:
        """Append a single skill's instructions to the system prompt."""
        manifest = self._discovery.find(name)
        if not manifest.instructions:
            return system_prompt
        return f"{system_prompt}\n\n## Skill: {manifest.name}\n\n{manifest.instructions}"

    def activate_many(self, names: list[str], system_prompt: str) -> str:
        """Activate multiple skills sequentially."""
        result = system_prompt
        for name in names:
            result = self.activate(name, result)
        return result
