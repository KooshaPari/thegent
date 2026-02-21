"""WL-015: Cross-platform rules synchronization.

Reads canonical rules from .thegent/rules/ and writes platform-specific
formats for Cursor (.cursor/rules/*.mdc), Claude Code (CLAUDE.md), and
Codex (.codex/skills/SKILL.md).

FR Traceability: FR-HAX-002
"""

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_log = logging.getLogger(__name__)

Platform = Literal["cursor", "claude", "codex"]
ALL_PLATFORMS: tuple[Platform, ...] = ("cursor", "claude", "codex")

_CLAUDE_MD_SECTION_START = "<!-- thegent:rules:start -->"
_CLAUDE_MD_SECTION_END = "<!-- thegent:rules:end -->"


@dataclass
class Rule:
    """A single canonical rule loaded from .thegent/rules/<id>.md."""

    id: str
    title: str
    platforms: list[Platform]
    content: str
    source_file: Path


@dataclass
class SyncRecord:
    """Record of a single file written (or that would be written) during sync."""

    platform: Platform
    destination: Path
    action: Literal["write", "skip", "dry_run"]


@dataclass
class RulesSyncResult:
    """Aggregate result of a rules sync operation."""

    rules_loaded: int = 0
    records: list[SyncRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False
    duration: float = 0.0

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def files_written(self) -> list[Path]:
        return [r.destination for r in self.records if r.action == "write"]

    @property
    def files_dry_run(self) -> list[Path]:
        return [r.destination for r in self.records if r.action == "dry_run"]


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Parse YAML-like frontmatter from a markdown file.

    Returns (metadata_dict, body_without_frontmatter).
    Raises ValueError if frontmatter is malformed.
    """
    if not text.startswith("---"):
        return {}, text

    end = text.find("---", 3)
    if end == -1:
        raise ValueError("Unclosed frontmatter block (missing closing ---)")

    raw_fm = text[3:end].strip()
    body = text[end + 3 :].lstrip("\n")

    meta: dict[str, object] = {}
    for line in raw_fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Parse list syntax: [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            meta[key] = items
        else:
            meta[key] = value.strip("\"'")

    return meta, body


def _validate_platforms(raw: object, rule_id: str) -> list[Platform]:
    """Validate and return list of platforms from frontmatter value.

    Raises ValueError for unknown platform names.
    """
    valid: set[Platform] = set(ALL_PLATFORMS)
    if isinstance(raw, list):
        items = [str(p).lower() for p in raw]
    elif isinstance(raw, str):
        items = [raw.lower()]
    else:
        raise ValueError(f"Rule {rule_id!r}: 'platforms' must be a list or string, got {type(raw).__name__}")

    unknown = [p for p in items if p not in valid]
    if unknown:
        raise ValueError(f"Rule {rule_id!r}: unknown platform(s): {unknown!r}. Valid: {sorted(valid)}")

    return items  # type: ignore[return-value]


class RulesSyncManager:
    """Synchronises canonical rules from .thegent/rules/ to platform targets.

    Usage::

        manager = RulesSyncManager()
        rules = manager.load_canonical_rules(project_path)
        result = manager.sync_all(project_path, platforms=["cursor", "claude"], dry_run=False)
    """

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_canonical_rules(self, project_path: Path) -> list[Rule]:
        """Read all *.md rule files from <project_path>/.thegent/rules/.

        Each file must contain YAML frontmatter with at minimum:
          - id: <str>
          - title: <str>
          - platforms: [cursor, claude, codex]

        Raises FileNotFoundError if the rules directory does not exist.
        Raises ValueError for any malformed rule file.
        """
        rules_dir = project_path / ".thegent" / "rules"
        if not rules_dir.is_dir():
            raise FileNotFoundError(f"Canonical rules directory not found: {rules_dir}")

        rules: list[Rule] = []
        for md_file in sorted(rules_dir.glob("*.md")):
            rule = self._load_rule_file(md_file)
            rules.append(rule)
            _log.debug("Loaded rule %r from %s", rule.id, md_file.name)

        _log.info("Loaded %d canonical rule(s) from %s", len(rules), rules_dir)
        return rules

    def _load_rule_file(self, path: Path) -> Rule:
        """Parse a single rule file and return a Rule instance.

        Raises ValueError if required frontmatter fields are missing or invalid.
        """
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)

        rule_id = meta.get("id")
        if not rule_id:
            raise ValueError(f"{path}: frontmatter missing required field 'id'")

        title = meta.get("title")
        if not title:
            raise ValueError(f"{path}: frontmatter missing required field 'title'")

        raw_platforms = meta.get("platforms")
        if raw_platforms is None:
            raise ValueError(f"{path}: frontmatter missing required field 'platforms'")

        platforms = _validate_platforms(raw_platforms, str(rule_id))

        return Rule(
            id=str(rule_id),
            title=str(title),
            platforms=platforms,
            content=body,
            source_file=path,
        )

    # ------------------------------------------------------------------
    # Platform sync methods
    # ------------------------------------------------------------------

    def sync_to_cursor(
        self,
        rules: list[Rule],
        project_path: Path,
        dry_run: bool = False,
    ) -> list[SyncRecord]:
        """Write a single consolidated .cursor/rules/thegent-rules.mdc file.

        Only rules that include 'cursor' in their platforms list are included.
        The .mdc file is formatted as a standard Cursor rules document.
        """
        cursor_rules = [r for r in rules if "cursor" in r.platforms]
        if not cursor_rules:
            _log.info("No rules target cursor platform; skipping Cursor sync.")
            return []

        cursor_dir = project_path / ".cursor" / "rules"
        dest = cursor_dir / "thegent-rules.mdc"

        lines: list[str] = [
            "---",
            "description: thegent canonical rules (auto-generated by `thegent rules sync`)",
            "alwaysApply: true",
            "---",
            "",
        ]
        for rule in cursor_rules:
            lines.append(f"## {rule.title}")
            lines.append("")
            lines.append(rule.content.strip())
            lines.append("")

        content = "\n".join(lines)
        action: Literal["write", "skip", "dry_run"]

        if dry_run:
            action = "dry_run"
            _log.info("[dry-run] Would write Cursor rules to %s", dest)
        else:
            cursor_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            action = "write"
            _log.info("Wrote Cursor rules to %s (%d rule(s))", dest, len(cursor_rules))

        return [SyncRecord(platform="cursor", destination=dest, action=action)]

    def sync_to_claude(
        self,
        rules: list[Rule],
        project_path: Path,
        dry_run: bool = False,
    ) -> list[SyncRecord]:
        """Append or merge a thegent rules section into CLAUDE.md.

        The section is bounded by HTML comment markers so subsequent syncs
        replace only the managed block without touching surrounding content.
        Rules without 'claude' in their platforms list are excluded.
        """
        claude_rules = [r for r in rules if "claude" in r.platforms]
        if not claude_rules:
            _log.info("No rules target claude platform; skipping Claude sync.")
            return []

        claude_md = project_path / "CLAUDE.md"
        section_lines: list[str] = [
            _CLAUDE_MD_SECTION_START,
            "",
            "# thegent Rules (auto-generated by `thegent rules sync`)",
            "",
        ]
        for rule in claude_rules:
            section_lines.append(f"## {rule.title}")
            section_lines.append("")
            section_lines.append(rule.content.strip())
            section_lines.append("")

        section_lines.append(_CLAUDE_MD_SECTION_END)
        new_section = "\n".join(section_lines) + "\n"

        action: Literal["write", "skip", "dry_run"]

        if dry_run:
            action = "dry_run"
            _log.info("[dry-run] Would update Claude rules section in %s", claude_md)
        else:
            if claude_md.exists():
                existing = claude_md.read_text(encoding="utf-8")
                updated = _replace_managed_section(existing, new_section)
            else:
                updated = new_section

            claude_md.write_text(updated, encoding="utf-8")
            action = "write"
            _log.info("Updated Claude rules section in %s (%d rule(s))", claude_md, len(claude_rules))

        return [SyncRecord(platform="claude", destination=claude_md, action=action)]

    def sync_to_codex(
        self,
        rules: list[Rule],
        project_path: Path,
        dry_run: bool = False,
    ) -> list[SyncRecord]:
        """Write .codex/skills/SKILL.md with all codex-targeted rules.

        Only rules that include 'codex' in their platforms list are written.
        """
        codex_rules = [r for r in rules if "codex" in r.platforms]
        if not codex_rules:
            _log.info("No rules target codex platform; skipping Codex sync.")
            return []

        skills_dir = project_path / ".codex" / "skills"
        dest = skills_dir / "SKILL.md"

        lines: list[str] = [
            "# thegent Rules",
            "",
            "> Auto-generated by `thegent rules sync`. Do not edit manually.",
            "",
        ]
        for rule in codex_rules:
            lines.append(f"## {rule.title}")
            lines.append("")
            lines.append(rule.content.strip())
            lines.append("")

        content = "\n".join(lines)
        action: Literal["write", "skip", "dry_run"]

        if dry_run:
            action = "dry_run"
            _log.info("[dry-run] Would write Codex skills to %s", dest)
        else:
            skills_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            action = "write"
            _log.info("Wrote Codex skills to %s (%d rule(s))", dest, len(codex_rules))

        return [SyncRecord(platform="codex", destination=dest, action=action)]

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def sync_all(
        self,
        project_path: Path,
        platforms: list[Platform] | None = None,
        dry_run: bool = False,
    ) -> RulesSyncResult:
        """Orchestrate rules sync across the requested platforms.

        Args:
            project_path: Root of the project containing .thegent/rules/.
            platforms:    List of platforms to sync. Defaults to all platforms.
            dry_run:      Report what would be written without writing files.

        Returns:
            RulesSyncResult with per-file records and any errors.

        Raises:
            FileNotFoundError: If .thegent/rules/ does not exist.
        """
        effective_platforms: list[Platform] = list(platforms) if platforms else list(ALL_PLATFORMS)
        t0 = time.monotonic()

        rules = self.load_canonical_rules(project_path)
        result = RulesSyncResult(rules_loaded=len(rules), dry_run=dry_run)

        dispatch: dict[Platform, object] = {
            "cursor": self.sync_to_cursor,
            "claude": self.sync_to_claude,
            "codex": self.sync_to_codex,
        }

        for platform in effective_platforms:
            sync_fn = dispatch[platform]
            records: list[SyncRecord] = sync_fn(rules, project_path, dry_run)  # type: ignore[operator]
            result.records.extend(records)

        result.duration = time.monotonic() - t0
        _log.info(
            "Rules sync complete: %d rule(s), %d file(s) %s in %.3fs",
            result.rules_loaded,
            len(result.records),
            "would be written" if dry_run else "written",
            result.duration,
        )
        return result


def _replace_managed_section(existing: str, new_section: str) -> str:
    """Replace the thegent-managed block inside existing CLAUDE.md content.

    If the markers are not present, the new section is appended.
    """
    pattern = re.compile(
        re.escape(_CLAUDE_MD_SECTION_START) + r".*?" + re.escape(_CLAUDE_MD_SECTION_END) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(existing):
        return pattern.sub(new_section, existing)
    # Markers not yet present — append
    separator = "\n" if existing and not existing.endswith("\n") else ""
    return existing + separator + new_section
