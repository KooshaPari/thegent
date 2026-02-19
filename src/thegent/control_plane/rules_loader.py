"""WP-10003: Unified rules loader for ShareCLI rules.conf."""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class Rule:
    command: str
    subcommand: str  # '*' for any
    strategy: str
    options: Dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.command}:{self.subcommand}"


class RulesLoader:
    """Parses and caches rules from sharecli/rules.conf."""

    def __init__(self, rules_path: Path):
        self.rules_path = rules_path
        self.rules: Dict[str, Rule] = {}
        self.equivalences: Dict[str, List[str]] = {}
        self._last_mtime: float = 0

    def load(self, force: bool = False) -> None:
        """Load rules from file if modified or forced."""
        if not self.rules_path.exists():
            return

        mtime = self.rules_path.stat().st_mtime
        if not force and mtime <= self._last_mtime:
            return

        new_rules: Dict[str, Rule] = {}
        new_equivs: Dict[str, List[str]] = {}

        try:
            with open(self.rules_path, "r") as f:
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

    def _parse_equivalence(self, def_str: str, equivs: Dict[str, List[str]]) -> None:
        if ":" not in def_str:
            return
        name, members = def_str.split(":", 1)
        equivs[name.strip()] = [m.strip() for m in members.split(",") if m.strip()]

    def _parse_rule_line(self, line: str) -> Optional[Rule]:
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
                try:
                    if "." in v:
                        v = float(v)
                    else:
                        v = int(v)
                except ValueError:
                    pass
                options[k] = v

        return Rule(command=cmd, subcommand=sub, strategy=strategy, options=options)

    def get_rule(self, command: str, subcommand: Optional[str] = None) -> Rule:
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
