"""Skills discovery module."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillManifest:
    """Manifest for a skill."""

    name: str
    description: str = ""
    instructions: str = ""
    source_path: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.tags is None:
            object.__setattr__(self, "tags", [])


class SkillActivator:
    """Activates skills dynamically."""

    def __init__(self, discovery: SkillDiscovery) -> None:
        self._discovery = discovery

    def activate(self, skill_name: str, base_prompt: str) -> str:
        """Activate a skill and return the enhanced prompt."""
        try:
            manifest = self._discovery.find(skill_name)
            if not manifest.instructions:
                return base_prompt
            return f"{base_prompt}\n\n{manifest.instructions}"
        except KeyError:
            raise KeyError(skill_name)

    def activate_many(self, skill_names: list[str], base_prompt: str) -> str:
        """Activate multiple skills and return the enhanced prompt."""
        result = base_prompt
        for name in skill_names:
            try:
                manifest = self._discovery.find(name)
                result = f"{result}\n\n{manifest.instructions}"
            except KeyError:
                raise KeyError(name)
        return result


class SkillDiscovery:
    """Discovers available skills."""

    def __init__(self, search_dirs: list[Path] | None = None) -> None:
        self._search_dirs = search_dirs or []
        self._cache: list[SkillManifest] = []
        self._name_map: dict[str, SkillManifest] = {}

    def discover(self) -> list[SkillManifest]:
        """Discover available skills from search directories."""
        self._cache = []
        self._name_map = {}
        for search_dir in self._search_dirs:
            if not search_dir.exists():
                continue
            # Check for SKILL.md, skill.json, skill.yaml directly in search_dir
            skill_md = search_dir / "SKILL.md"
            skill_json = search_dir / "skill.json"
            skill_yaml = search_dir / "skill.yaml"
            if skill_md.exists():
                self._parse_skill_md(skill_md)
            elif skill_json.exists():
                self._parse_skill_json(skill_json)
            elif skill_yaml.exists():
                self._parse_skill_yaml(skill_yaml)
            # Also check subdirectories
            self._discover_in_dir(search_dir)
        return self._cache

    def _discover_in_dir(self, directory: Path) -> None:
        """Discover skills in a directory."""
        for item in directory.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                skill_json = item / "skill.json"
                skill_yaml = item / "skill.yaml"
                if skill_md.exists():
                    self._parse_skill_md(skill_md)
                elif skill_json.exists():
                    self._parse_skill_json(skill_json)
                elif skill_yaml.exists():
                    self._parse_skill_yaml(skill_yaml)

    def _parse_skill_md(self, path: Path) -> None:
        """Parse a SKILL.md file."""
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")
        name = path.parent.name.replace("-", " ").replace("_", " ").title()
        instructions = ""
        has_h1 = False
        for i, line in enumerate(lines):
            if i == 0 and line.startswith("# "):
                name = line[2:].strip()
                has_h1 = True
            elif (not has_h1 and line.strip()) or has_h1:
                instructions += line + "\n"
        manifest = SkillManifest(
            name=name,
            instructions=instructions.strip(),
            source_path=str(path),
        )
        self._add_manifest(manifest)

    def _parse_skill_json(self, path: Path) -> None:
        """Parse a skill.json file."""
        try:
            data = _json.loads(path.read_bytes())
            manifest = SkillManifest(
                name=data.get("name", path.parent.name),
                description=data.get("description", ""),
                instructions=data.get("instructions", ""),
                tags=data.get("tags", []),
                source_path=str(path),
            )
            self._add_manifest(manifest)
        except Exception:
            pass

    def _parse_skill_yaml(self, path: Path) -> None:
        """Parse a skill.yaml file (simple YAML parsing)."""
        try:
            content = path.read_text(encoding="utf-8")
            name = ""
            description = ""
            instructions = ""
            tags: list[str] = []
            in_tags = False
            for line in content.split("\n"):
                if line.startswith("name:"):
                    name = line[5:].strip()
                elif line.startswith("description:"):
                    description = line[12:].strip()
                elif line.startswith("instructions:"):
                    instructions = line[13:].strip()
                elif line.startswith("tags:"):
                    in_tags = True
                elif in_tags and line.strip().startswith("-"):
                    tags.append(line.strip()[1:].strip())
                elif in_tags and line.strip() and not line.strip().startswith("-"):
                    in_tags = False
            manifest = SkillManifest(
                name=name or path.parent.name,
                description=description,
                instructions=instructions,
                tags=tags,
                source_path=str(path),
            )
            self._add_manifest(manifest)
        except Exception:
            pass

    def _add_manifest(self, manifest: SkillManifest) -> None:
        """Add a manifest to the discovery cache."""
        if manifest.name not in self._name_map:
            self._cache.append(manifest)
            self._name_map[manifest.name] = manifest

    def find(self, name: str) -> SkillManifest:
        """Find a skill by name."""
        if not self._cache:
            self.discover()
        if name not in self._name_map:
            raise KeyError(name)
        return self._name_map[name]


__all__ = ["SkillActivator", "SkillDiscovery", "SkillManifest", "SkillInfo"]


@dataclass
class SkillInfo:
    """Information about a skill."""

    id: str
    name: str
    description: str = ""
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
