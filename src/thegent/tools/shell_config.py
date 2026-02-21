"""Shell configuration file management utilities for thegent."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SHELL_CONFIG_NAMES = {
    ".bashrc",
    ".bash_profile",
    ".bash_login",
    ".profile",
    ".zshrc",
    ".zprofile",
    ".zshenv",
    ".zlogin",
    ".config/fish/config.fish",
}

_SHELL_EXTENSIONS = {".zsh", ".sh", ".fish", ".bash"}

_FUNC_PATTERNS = [
    re.compile(r"^function\s+(\w+)\s*(?:\(\))?\s*\{"),
    re.compile(r"^(\w+)\s*\(\)\s*\{"),
    re.compile(r"^(\w+)\s*\(\)\s*$"),
]
_ALIAS_PATTERN = re.compile(r"^alias\s+([A-Za-z0-9_-]+)=")
_SOURCE_DYNAMIC = re.compile(r"[\$`]")


def _is_shell_config(path: Path) -> bool:
    """Return True if path is a recognized shell config file."""
    name = path.name
    suffix = path.suffix.lower()
    return name in _SHELL_CONFIG_NAMES or suffix in _SHELL_EXTENSIONS or "config.fish" in str(path)


def _extract_raw_source(line: str) -> str | None:
    """Extract the raw source string, or None if not a source line."""
    stripped = line.strip()
    m = re.match(r'^(?:source|\.)\s+["\']?([^"\'#]+)["\']?', stripped)
    if not m:
        return None
    return m.group(1).strip()


def _resolve_source(raw: str, base_dir: Path) -> Path | None:
    """Resolve a raw path string to an absolute Path, or None if dynamic."""
    if _SOURCE_DYNAMIC.search(raw):
        if raw.startswith("~/"):
            target = str(Path.home()) + raw[1:]
            return Path(target)
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = base_dir / p
    return p


def _parse_functions(lines: list[str]) -> list[str]:
    funcs: list[str] = []
    for line in lines:
        stripped = line.strip()
        for pat in _FUNC_PATTERNS:
            m = pat.match(stripped)
            if m:
                funcs.append(m.group(1))
                break
    return funcs


def _parse_aliases(lines: list[str]) -> list[str]:
    aliases: list[str] = []
    for line in lines:
        m = _ALIAS_PATTERN.match(line.strip())
        if m:
            aliases.append(m.group(1))
    return aliases


@dataclass
class ShellConfigFile:
    """Represents a parsed shell configuration file."""

    path: Path
    lines: list[str] = field(default_factory=list)
    sources: list[Path] = field(default_factory=list)
    raw_sources: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    @classmethod
    def parse(cls, path: Path) -> ShellConfigFile:
        """Parse a shell config file, extracting functions, aliases, and sources."""
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        sources: list[Path] = []
        raw_sources: list[str] = []
        for line in lines:
            raw = _extract_raw_source(line)
            if raw is not None:
                raw_sources.append(raw)
                resolved = _resolve_source(raw, path.parent)
                if resolved is not None:
                    sources.append(resolved)
        return cls(
            path=path.resolve(),
            lines=lines,
            sources=sources,
            raw_sources=raw_sources,
            functions=_parse_functions(lines),
            aliases=_parse_aliases(lines),
        )

    def has_line(self, pattern: str) -> bool:
        """Return True if any line matches the given regex pattern."""
        compiled = re.compile(pattern)
        return any(compiled.search(line) for line in self.lines)


class ShellConfigAuditor:
    """Audits shell configuration files."""

    def __init__(self, home: Path | None = None) -> None:
        self.home = home or Path.home()

    def audit(self, dirs: list[Path] | None = None) -> list[ShellConfigFile]:
        """Scan directories for shell config files and parse them."""
        if dirs is None:
            return self._audit_home()
        seen: set[Path] = set()
        configs: list[ShellConfigFile] = []
        for d in dirs:
            if not d.is_dir():
                continue
            for p in sorted(d.iterdir()):
                if p.is_file() and _is_shell_config(p):
                    resolved = p.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        configs.append(ShellConfigFile.parse(p))
        return configs

    def _audit_home(self) -> list[ShellConfigFile]:
        configs: list[ShellConfigFile] = []
        for name in sorted(_SHELL_CONFIG_NAMES):
            path = self.home / name
            if path.exists():
                configs.append(ShellConfigFile.parse(path))
        return configs

    def find_duplicates(self, configs: list[ShellConfigFile]) -> dict[str, list[Path]]:
        """Return functions defined in more than one config file."""
        func_to_files: dict[str, list[Path]] = {}
        for cfg in configs:
            for fn in cfg.functions:
                func_to_files.setdefault(fn, []).append(cfg.path)
        return {fn: paths for fn, paths in func_to_files.items() if len(paths) > 1}

    def find_duplicate_aliases(self, configs: list[ShellConfigFile]) -> dict[str, list[Path]]:
        """Return aliases defined in more than one config file."""
        alias_to_files: dict[str, list[Path]] = {}
        for cfg in configs:
            for a in cfg.aliases:
                alias_to_files.setdefault(a, []).append(cfg.path)
        return {a: p for a, p in alias_to_files.items() if len(p) > 1}

    def generate_consolidated(self, configs: list[ShellConfigFile]) -> str:
        """Merge all configs into a single consolidated shell script."""
        if not configs:
            return "# No shell configuration files found\n"
        parts = ["#!/usr/bin/env zsh", "# Consolidated shell configuration", ""]
        dupes = self.find_duplicates(configs)
        if dupes:
            parts.append("# WARNING: Duplicate function definitions detected:")
            for fn, paths in sorted(dupes.items()):
                files = ", ".join(str(p) for p in paths)
                parts.append(f"#   WARNING: {fn} defined in: {files}")
            parts.append("")
        for cfg in configs:
            parts.append(f"# --- Source: {cfg.path} ---")
            parts.extend(cfg.lines)
            parts.append("")
        return "\n".join(parts)

    def check_sourcing_order(self, configs: list[ShellConfigFile]) -> list[str]:
        """Check for sourcing issues, return list of problem strings."""
        issues: list[str] = []
        known_paths = {cfg.path for cfg in configs}
        for cfg in configs:
            if not cfg.lines:
                issues.append(f"{cfg.path.name} is empty")
            for src in cfg.sources:
                if src not in known_paths:
                    issues.append(f"{cfg.path.name} sources {src} which is not in the discovered set")
        return issues

    def sourcing_graph(self, configs: list[ShellConfigFile]) -> dict[str, list[str]]:
        """Return {{filename: [sourced filenames]}} for files that source others."""
        return {cfg.path.name: [s.name for s in cfg.sources] for cfg in configs if cfg.sources}
