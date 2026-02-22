"""Cross-project persona registry.

Discovers and catalogs AI agent personas (Markdown files with YAML frontmatter)
across multiple local projects, persisting the catalog to a shared JSON file at
~/.thegent/persona_registry.json.

FR Traceability: FR-AGT-020 (cross-project persona discovery and search)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml  # bundled via pyyaml (already in pyproject.toml dependencies)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

_AGENTS_SUBDIR = "agents"
_FRONTMATTER_FIELDS_CAPABILITIES = ("tools", "capabilities")


@dataclass
class PersonaRecord:
    """Catalog entry for a single AI agent persona."""

    name: str
    project_root: Path
    capabilities: list[str]
    persona_file: Path
    last_seen: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "name": self.name,
            "project_root": str(self.project_root),
            "capabilities": self.capabilities,
            "persona_file": str(self.persona_file),
            "last_seen": self.last_seen.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersonaRecord:
        """Deserialize from a plain dict (as loaded from JSON)."""
        raw_ts = data.get("last_seen", "")
        try:
            ts = datetime.fromisoformat(raw_ts)
        except (ValueError, TypeError):
            ts = datetime.now(tz=UTC)

        return cls(
            name=data["name"],
            project_root=Path(data["project_root"]),
            capabilities=list(data.get("capabilities") or []),
            persona_file=Path(data["persona_file"]),
            last_seen=ts,
        )


# ---------------------------------------------------------------------------
# Frontmatter parser (minimal, no external dep beyond pyyaml)
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract YAML frontmatter from a Markdown string.

    Returns an empty dict if no frontmatter is present or if parsing fails.
    """
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return {}

    # Find the closing ---
    rest = stripped[3:]
    end = rest.find("\n---")
    if end == -1:
        return {}

    yaml_block = rest[:end]
    try:
        parsed = yaml.safe_load(yaml_block)
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def _extract_capabilities(frontmatter: dict[str, Any]) -> list[str]:
    """Pull capability strings from frontmatter.

    Looks for ``tools`` or ``capabilities`` keys; normalises every entry to a
    lowercase string, splitting comma-delimited values.
    """
    caps: list[str] = []
    for key in _FRONTMATTER_FIELDS_CAPABILITIES:
        value = frontmatter.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            caps.extend(p.strip().lower() for p in value.split(",") if p.strip())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    caps.extend(p.strip().lower() for p in item.split(",") if p.strip())
    return list(dict.fromkeys(caps))  # deduplicate, preserve order


def _extract_name(frontmatter: dict[str, Any], stem: str) -> str:
    """Return name from frontmatter, falling back to the file stem."""
    name = frontmatter.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return stem


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CrossProjectRegistry:
    """Discovers and catalogs agent personas across projects.

    The registry is backed by a JSON file at ``REGISTRY_FILE`` (defaults to
    ``~/.thegent/persona_registry.json``).  All mutating methods keep the
    in-memory state updated; callers must call :meth:`save` to persist.
    """

    REGISTRY_FILE: Path = Path.home() / ".thegent" / "persona_registry.json"

    def __init__(self, registry_file: Path | None = None) -> None:
        self._registry_file: Path = registry_file or self.REGISTRY_FILE
        # Keyed by (project_root_str, persona_name) for deduplication.
        self._records: dict[tuple[str, str], PersonaRecord] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover_personas(self, project_root: Path) -> list[PersonaRecord]:
        """Scan *project_root*/agents/ for ``.md`` persona files.

        For each file the YAML frontmatter is parsed to extract the persona
        name and capabilities.  A :class:`PersonaRecord` is returned for each
        file found.  The records are NOT added to the registry; use
        :meth:`register_project` for that.
        """
        agents_dir = project_root / _AGENTS_SUBDIR
        records: list[PersonaRecord] = []

        if not agents_dir.is_dir():
            logger.debug("No agents/ directory at %s", agents_dir)
            return records

        for md_file in sorted(agents_dir.glob("*.md")):
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                logger.warning("Cannot read %s: %s", md_file, exc)
                continue

            frontmatter = _parse_frontmatter(text)
            name = _extract_name(frontmatter, md_file.stem)
            capabilities = _extract_capabilities(frontmatter)

            records.append(
                PersonaRecord(
                    name=name,
                    project_root=project_root.resolve(),
                    capabilities=capabilities,
                    persona_file=md_file.resolve(),
                    last_seen=datetime.now(tz=UTC),
                )
            )

        return records

    def register_project(self, project_root: Path) -> list[PersonaRecord]:
        """Discover personas in *project_root* and add them to the registry.

        Existing records for the same (project, name) are overwritten with
        fresh metadata.  Calls :meth:`save` automatically before returning.

        Returns the list of newly discovered records.
        """
        project_root = project_root.resolve()
        records = self.discover_personas(project_root)
        now = datetime.now(tz=UTC)

        for record in records:
            record.last_seen = now
            key = (str(record.project_root), record.name)
            self._records[key] = record

        self.save()
        return records

    def search(self, capability: str) -> list[PersonaRecord]:
        """Return all personas that advertise *capability*.

        The match is case-insensitive and checks whether the normalised
        capability string appears in the persona's capability list.
        """
        needle = capability.strip().lower()
        return [r for r in self._records.values() if needle in r.capabilities]

    def get_all(self) -> list[PersonaRecord]:
        """Return all records currently held in the registry."""
        return list(self._records.values())

    def save(self) -> None:
        """Persist the registry to :attr:`REGISTRY_FILE` (JSON)."""
        self._registry_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [r.to_dict() for r in self._records.values()]
        tmp = self._registry_file.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(self._registry_file)
        except OSError as exc:
            logger.error("Failed to save persona registry: %s", exc)
            raise

    def load(self) -> None:
        """Load the registry from :attr:`REGISTRY_FILE`.

        Silently starts with an empty registry if the file does not exist.
        Raises :class:`ValueError` if the file exists but is malformed.
        """
        if not self._registry_file.exists():
            return

        try:
            raw = self._registry_file.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Corrupt persona registry at {self._registry_file}: {exc}") from exc

        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON list in {self._registry_file}, got {type(payload)}")

        self._records.clear()
        for item in payload:
            self._load_one_record(item)

    def _load_one_record(self, item: dict[str, Any]) -> None:
        """Parse and insert a single record from loaded JSON, logging on error."""
        try:
            record = PersonaRecord.from_dict(item)
        except (KeyError, TypeError) as exc:
            logger.warning("Skipping malformed registry entry %s: %s", item, exc)
            return
        key = (str(record.project_root), record.name)
        self._records[key] = record
