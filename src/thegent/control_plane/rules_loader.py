"""WP-10003: Unified rules loader for heliosShield rules.conf."""

import contextlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Rule:
    command: str
    subcommand: str  # '*' for any
    strategy: str
    options: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.command}:{self.subcommand}"


class RulesLoader:
    """Parses and caches rules from centralized rules.conf."""

    def __init__(self, rules_path: Path | None = None) -> None:
        if rules_path is None:
            # Centralized config path
            rules_path = Path.home() / ".config" / "thegent" / "rules.conf"
            if not rules_path.exists():
                # Fallback to CWD
                rules_path = Path.cwd() / "rules.conf"
        self.rules_path = rules_path
        self.rules: dict[str, Rule] = {}
        self.equivalences: dict[str, list[str]] = {}
        self._last_mtime: float = 0

    def load(self, force: bool = False) -> None:
        """Load rules from file if modified or forced."""
        if not self.rules_path.exists():
            return

        mtime = self.rules_path.stat().st_mtime
        if not force and mtime <= self._last_mtime:
            return

        new_rules: dict[str, Rule] = {}
        new_equivs: dict[str, list[str]] = {}

        try:
            with open(self.rules_path) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if not line:
                        continue

                    if line.startswith("equivalence="):
                        self._parse_equivalence(line[12:], new_equivs)
                        continue

                    rule = self._parse_rule_line(line)
                    if rule:
                        new_rules[rule.key] = rule

            self.rules = new_rules
            self.equivalences = new_equivs
            self._last_mtime = mtime
            logger.info(f"Loaded {len(self.rules)} rules from {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")

    def _parse_equivalence(self, def_str: str, equivs: dict[str, list[str]]) -> None:
        if ":" not in def_str:
            return
        name, members = def_str.split(":", 1)
        equivs[name.strip()] = [m.strip() for m in members.split(",") if m.strip()]

    def _parse_rule_line(self, line: str) -> Rule | None:
        parts = line.split()
        if len(parts) < 2:
            return None

        pattern = parts[0]
        strategy = parts[1]
        options_parts = parts[2:]

        if ":" in pattern:
            cmd, sub = pattern.split(":", 1)
        else:
            cmd, sub = pattern, "*"

        options = {}
        for opt in options_parts:
            if "=" in opt:
                k, v = opt.split("=", 1)
                # Try to convert to numeric if possible
                with contextlib.suppress(ValueError):
                    v = float(v) if "." in v else int(v)
                options[k] = v

        return Rule(command=cmd, subcommand=sub, strategy=strategy, options=options)

    def get_rule(self, command: str, subcommand: str | None = None) -> Rule:
        """Find the matching rule for a command/subcommand."""
        self.load()
        sub = subcommand or "*"

        # Exact match
        key = f"{command}:{sub}"
        if key in self.rules:
            return self.rules[key]

        # Wildcard match
        wild_key = f"{command}:*"
        if wild_key in self.rules:
            return self.rules[wild_key]

        # Fallback
        return Rule(command=command, subcommand=sub, strategy="passthrough")
