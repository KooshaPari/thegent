"""WP-9002: Unified rules synchronization across platforms."""

import logging
from pathlib import Path

_log = logging.getLogger(__name__)


class RulesSync:
    """Synchronizes agent rules from a canonical source to platform-specific locations."""

    def __init__(self, project_root: Path) -> None:
        self.root = project_root
        self.rules_src = project_root / ".thegent" / "rules"

    def sync(self) -> list[str]:
        """Perform synchronization. Returns list of synced files."""
        if not self.rules_src.exists():
            _log.warning(f"No canonical rules source found at {self.rules_src}")
            return []

        synced = []
        rules = list(self.rules_src.glob("*.md")) + list(self.rules_src.glob("*.mdc"))

        for rule_file in rules:
            content = rule_file.read_text(encoding="utf-8")
            name = rule_file.stem

            # 1. Sync to Cursor (.cursor/rules/{name}.mdc)
            cursor_dir = self.root / ".cursor" / "rules"
            cursor_dir.mkdir(parents=True, exist_ok=True)
            # Ensure .mdc extension for Cursor
            cursor_file = cursor_dir / f"{name}.mdc"
            cursor_file.write_text(content, encoding="utf-8")
            synced.append(str(cursor_file))

            # 2. Sync to Codex (.codex/skills/{name}/SKILL.md)
            codex_dir = self.root / ".codex" / "skills" / name
            codex_dir.mkdir(parents=True, exist_ok=True)
            codex_file = codex_dir / "SKILL.md"
            codex_file.write_text(content, encoding="utf-8")
            synced.append(str(codex_file))

            # 3. Sync to Claude (CLAUDE.md)
            # Implementation note: Appending to CLAUDE.md might be destructive if not careful.
            # In Phase 1, we just sync to .claude/skills/ if it exists.
            claude_skills = self.root / ".claude" / "skills" / name
            claude_skills.mkdir(parents=True, exist_ok=True)
            claude_file = claude_skills / "SKILL.md"
            claude_file.write_text(content, encoding="utf-8")
            synced.append(str(claude_file))

        return synced
