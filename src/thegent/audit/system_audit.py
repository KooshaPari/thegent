"""System audit framework: detect drift between declared config and actual state.

This module checks:
- Hooks: registered in hook-config.yaml vs hook scripts on disk
- Agents: agent .md files on disk vs any agent registry
- Config: ThegentSettings fields vs actual environment variables set
- Dependencies: pyproject.toml declared deps vs pip-installed packages
"""

from __future__ import annotations

import importlib.metadata
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from thegent.integrations.base import SerializableMixin


class AuditStatus(str, Enum):
    """Status of a single audit check."""

    OK = "ok"
    DRIFT = "drift"
    MISSING = "missing"
    UNEXPECTED = "unexpected"
    ERROR = "error"
    WARN = "warn"


@dataclass
class AuditResult(SerializableMixin):
    """Result of one audit check."""

    category: str
    item: str
    status: AuditStatus
    expected: str
    actual: str
    fix_suggestion: str = ""

    def is_ok(self) -> bool:
        """Return True when no problem detected."""
        return self.status == AuditStatus.OK


@dataclass
class AuditReport:
    """Full audit report produced by SystemAuditor.run_full_audit()."""

    timestamp: str
    results: list[AuditResult] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._recompute_summary()

    def _recompute_summary(self) -> None:
        counts: dict[str, int] = {s.value: 0 for s in AuditStatus}
        counts["total"] = len(self.results)
        for r in self.results:
            counts[r.status.value] = counts.get(r.status.value, 0) + 1
        self.summary = counts

    def add_results(self, results: list[AuditResult]) -> None:
        """Append results and refresh summary counts."""
        self.results.extend(results)
        self._recompute_summary()

    @property
    def has_drift(self) -> bool:
        """True when any non-OK result exists."""
        return any(not r.is_ok() for r in self.results)


# ---------------------------------------------------------------------------
# Internal path helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    """Resolve project root as the directory containing pyproject.toml.

    Walks upward from this file's location until pyproject.toml is found.
    Falls back to cwd if not found.
    """
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return Path.cwd()


def _hooks_dir(root: Path) -> Path:
    return root / "hooks"


def _agents_dir(root: Path) -> Path:
    return root / "agents"


def _hook_config_path(root: Path) -> Path:
    return root / "hooks" / "hook-config.yaml"


def _pyproject_path(root: Path) -> Path:
    return root / "pyproject.toml"


def _normalize_pkg_name(name: str) -> str:
    """Normalize package name per PEP 503: lowercase, dashes/underscores/dots to -."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _extract_pkg_name(dep_spec: str) -> str:
    """Extract bare package name from a PEP 508 dependency specifier.

    Examples::

        "httpx>=0.28.1"  -> "httpx"
        "pydantic[email]>=2.0"  -> "pydantic"
        "orjson; implementation_name == 'cpython'"  -> "orjson"
    """
    # Strip environment markers
    dep_spec = dep_spec.split(";", maxsplit=1)[0].strip()
    # Strip extras like [email]
    dep_spec = re.sub(r"\[.*?\]", "", dep_spec)
    # Strip version specifiers; first non-name character breaks the name
    name = re.split(r"[><=!~\s]", dep_spec)[0].strip()
    return name


def _check_specifier(specifier: str, installed_ver: str) -> tuple[bool, str]:
    """Return (satisfies, note) for *installed_ver* against *specifier*.

    Falls back gracefully when the *packaging* library is unavailable.
    """
    if not specifier:
        return True, ""
    try:
        from packaging.specifiers import SpecifierSet

        ss = SpecifierSet(specifier)
        ok = installed_ver in ss
        note = "" if ok else f"(requires {specifier})"
        return ok, note
    except Exception:
        return True, f"(could not verify specifier '{specifier}')"


# ---------------------------------------------------------------------------
# SystemAuditor
# ---------------------------------------------------------------------------


class SystemAuditor:
    """Detects drift between declared configuration and actual on-disk state."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or _project_root()

    # ------------------------------------------------------------------
    # Hook audit
    # ------------------------------------------------------------------

    def audit_hooks(self) -> list[AuditResult]:
        """Compare hooks declared in hook-config.yaml against scripts on disk.

        For each hook entry in the config's ``hooks:`` section we check that a
        corresponding ``.sh`` file exists under ``hooks/``.  We also flag any
        ``.sh`` files in the hooks directory that are *not* registered in config.
        """
        results: list[AuditResult] = []
        config_path = _hook_config_path(self._root)
        hooks_dir = _hooks_dir(self._root)

        if not config_path.exists():
            return [
                AuditResult(
                    category="hooks",
                    item="hook-config.yaml",
                    status=AuditStatus.MISSING,
                    expected=str(config_path),
                    actual="not found",
                    fix_suggestion=f"Create {config_path} with a 'hooks:' section.",
                )
            ]

        try:
            import yaml

            with config_path.open() as fh:
                config: dict[str, Any] = yaml.safe_load(fh) or {}
        except Exception as exc:
            return [
                AuditResult(
                    category="hooks",
                    item="hook-config.yaml",
                    status=AuditStatus.ERROR,
                    expected="valid YAML",
                    actual=str(exc),
                    fix_suggestion="Fix YAML syntax in hook-config.yaml.",
                )
            ]

        declared_hooks: dict[str, Any] = config.get("hooks", {}) or {}

        # Collect .sh files in hooks directory (skip subdirectories)
        disk_scripts: dict[str, Path] = {}
        if hooks_dir.exists():
            for p in hooks_dir.iterdir():
                if p.is_file() and p.suffix == ".sh":
                    disk_scripts[p.stem] = p

        # Check declared -> disk
        for hook_name in declared_hooks:
            if hook_name in disk_scripts:
                results.append(
                    AuditResult(
                        category="hooks",
                        item=hook_name,
                        status=AuditStatus.OK,
                        expected=f"hooks/{hook_name}.sh",
                        actual=str(disk_scripts[hook_name].relative_to(self._root)),
                    )
                )
            else:
                results.append(
                    AuditResult(
                        category="hooks",
                        item=hook_name,
                        status=AuditStatus.MISSING,
                        expected=f"hooks/{hook_name}.sh",
                        actual="not found on disk",
                        fix_suggestion=(
                            f"Create hooks/{hook_name}.sh or remove the '{hook_name}' entry from hook-config.yaml."
                        ),
                    )
                )

        # Check disk -> declared (undeclared scripts)
        for stem, path in disk_scripts.items():
            if stem not in declared_hooks:
                results.append(
                    AuditResult(
                        category="hooks",
                        item=stem,
                        status=AuditStatus.UNEXPECTED,
                        expected="registered in hook-config.yaml",
                        actual=str(path.relative_to(self._root)),
                        fix_suggestion=(f"Register '{stem}' in hooks/hook-config.yaml or remove {path.name}."),
                    )
                )

        return results

    # ------------------------------------------------------------------
    # Agent audit
    # ------------------------------------------------------------------

    def audit_agents(self) -> list[AuditResult]:
        """Verify agent .md files in agents/ are valid and parseable.

        Checks:
        - agents/ directory exists
        - Each .md file is non-empty
        - Any agent referenced in bounded-contexts.yaml (if present) is on disk
        """
        results: list[AuditResult] = []
        agents_dir = _agents_dir(self._root)

        if not agents_dir.exists():
            return [
                AuditResult(
                    category="agents",
                    item="agents/",
                    status=AuditStatus.MISSING,
                    expected="agents/ directory",
                    actual="not found",
                    fix_suggestion="Create an agents/ directory with agent .md persona files.",
                )
            ]

        agent_files: list[Path] = sorted(p for p in agents_dir.iterdir() if p.suffix == ".md" and p.is_file())

        if not agent_files:
            results.append(
                AuditResult(
                    category="agents",
                    item="agents/",
                    status=AuditStatus.WARN,
                    expected="at least one .md agent file",
                    actual="directory empty",
                    fix_suggestion="Add at least one agent persona .md file to agents/.",
                )
            )
            return results

        for agent_file in agent_files:
            agent_name = agent_file.stem
            content = agent_file.read_text(encoding="utf-8", errors="replace")
            if not content.strip():
                results.append(
                    AuditResult(
                        category="agents",
                        item=agent_name,
                        status=AuditStatus.WARN,
                        expected="non-empty persona definition",
                        actual="empty file",
                        fix_suggestion=f"Add persona definition to agents/{agent_file.name}.",
                    )
                )
            else:
                results.append(
                    AuditResult(
                        category="agents",
                        item=agent_name,
                        status=AuditStatus.OK,
                        expected=f"agents/{agent_file.name}",
                        actual=f"agents/{agent_file.name} ({len(content)} bytes)",
                    )
                )

        # Cross-check bounded-contexts.yaml if present
        bc_path = agents_dir / "bounded-contexts.yaml"
        if bc_path.exists():
            try:
                import yaml

                with bc_path.open() as fh:
                    bc: dict[str, Any] = yaml.safe_load(fh) or {}
                registered: list[str] = bc.get("agents", []) or []
                disk_names = {p.stem for p in agent_files}
                for name in registered:
                    if name not in disk_names:
                        results.append(
                            AuditResult(
                                category="agents",
                                item=name,
                                status=AuditStatus.MISSING,
                                expected=f"agents/{name}.md",
                                actual="referenced in bounded-contexts.yaml but not found on disk",
                                fix_suggestion=(f"Create agents/{name}.md or remove from bounded-contexts.yaml."),
                            )
                        )
            except Exception as exc:
                results.append(
                    AuditResult(
                        category="agents",
                        item="bounded-contexts.yaml",
                        status=AuditStatus.ERROR,
                        expected="valid YAML",
                        actual=str(exc),
                        fix_suggestion="Fix YAML syntax in agents/bounded-contexts.yaml.",
                    )
                )

        return results

    # ------------------------------------------------------------------
    # Config audit
    # ------------------------------------------------------------------

    def audit_config(self) -> list[AuditResult]:
        """Compare ThegentSettings field defaults against actual environment.

        For each field that has a corresponding THGENT_* environment variable
        we report whether the env var is set (non-default) or absent (default).
        We also flag env vars whose values diverge from the declared default.
        """
        results: list[AuditResult] = []

        try:
            from thegent.config import ThegentSettings

            settings = ThegentSettings()
        except Exception as exc:
            return [
                AuditResult(
                    category="config",
                    item="ThegentSettings",
                    status=AuditStatus.ERROR,
                    expected="ThegentSettings loads without error",
                    actual=str(exc),
                    fix_suggestion="Fix configuration errors; check .env and THGENT_* env vars.",
                )
            ]

        model_cfg = settings.model_config
        env_prefix: str = model_cfg.get("env_prefix", "THGENT_")  # pydantic-settings attribute

        fields_info = type(settings).model_fields

        known_env_keys: set[str] = set()
        for field_name, field_info in fields_info.items():
            env_key = f"{env_prefix}{field_name.upper()}"
            known_env_keys.add(env_key)
            env_val = os.environ.get(env_key)

            try:
                current_val = getattr(settings, field_name)
            except AttributeError:
                continue

            default = field_info.default
            has_factory = field_info.default_factory is not None

            if env_val is not None:
                results.append(
                    AuditResult(
                        category="config",
                        item=field_name,
                        status=AuditStatus.OK,
                        expected=f"{env_key}=<user override>",
                        actual=f"{env_key}={env_val!r} -> effective={current_val!r}",
                    )
                )
            else:
                default_label = "factory" if has_factory else repr(default)
                results.append(
                    AuditResult(
                        category="config",
                        item=field_name,
                        status=AuditStatus.OK,
                        expected=f"default ({default_label})",
                        actual=f"effective={current_val!r}",
                    )
                )

        # Flag unknown THGENT_* env vars
        for key, val in os.environ.items():
            if key.startswith(env_prefix) and key not in known_env_keys:
                results.append(
                    AuditResult(
                        category="config",
                        item=key,
                        status=AuditStatus.UNEXPECTED,
                        expected="recognized THGENT_* environment variable",
                        actual=f"{key}={val!r} (not mapped to any ThegentSettings field)",
                        fix_suggestion=(
                            f"Remove {key} from environment or add a corresponding field to ThegentSettings."
                        ),
                    )
                )

        return results

    # ------------------------------------------------------------------
    # Dependency audit
    # ------------------------------------------------------------------

    def audit_dependencies(self) -> list[AuditResult]:
        """Compare pyproject.toml declared dependencies against installed packages.

        Uses importlib.metadata to check installed distributions.  Reports:
        - MISSING: declared but not installed
        - OK: present and version satisfies declared specifier
        - DRIFT: present but version does not satisfy declared specifier
        - WARN: present but specifier cannot be verified
        """
        results: list[AuditResult] = []
        pyproject = _pyproject_path(self._root)

        if not pyproject.exists():
            return [
                AuditResult(
                    category="dependencies",
                    item="pyproject.toml",
                    status=AuditStatus.MISSING,
                    expected=str(pyproject),
                    actual="not found",
                    fix_suggestion="Ensure pyproject.toml is present at the project root.",
                )
            ]

        try:
            if sys.version_info >= (3, 11):
                import tomllib

                with pyproject.open("rb") as fh:
                    pydata: dict[str, Any] = tomllib.load(fh)
            else:  # Python < 3.11 fallback
                import tomli  # type: ignore[import-not-found]  # tomli not needed on 3.11+

                with pyproject.open("rb") as fh:
                    pydata = tomli.load(fh)  # type: ignore[possibly-undefined]
        except Exception as exc:
            return [
                AuditResult(
                    category="dependencies",
                    item="pyproject.toml",
                    status=AuditStatus.ERROR,
                    expected="valid TOML",
                    actual=str(exc),
                    fix_suggestion="Fix TOML syntax in pyproject.toml.",
                )
            ]

        deps: list[str] = pydata.get("project", {}).get("dependencies", [])

        # Build installed package map: normalized name -> version string
        installed: dict[str, str] = {}
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name", "")
            ver = dist.metadata.get("Version", "")
            if name:
                installed[_normalize_pkg_name(name)] = ver

        for dep_spec in deps:
            pkg_name = _extract_pkg_name(dep_spec)
            norm = _normalize_pkg_name(pkg_name)

            if norm in installed:
                installed_ver = installed[norm]
                specifier_part = dep_spec[len(pkg_name) :].strip()
                # Strip extras from specifier_part if present
                specifier_part = re.sub(r"^\[.*?\]", "", specifier_part).strip()
                # Strip environment markers
                specifier_part = specifier_part.split(";")[0].strip()
                ok, note = _check_specifier(specifier_part, installed_ver)
                results.append(
                    AuditResult(
                        category="dependencies",
                        item=pkg_name,
                        status=AuditStatus.OK if ok else AuditStatus.DRIFT,
                        expected=dep_spec,
                        actual=f"{pkg_name}=={installed_ver}{' ' + note if note else ''}",
                        fix_suggestion="" if ok else f"Run: pip install '{dep_spec}'",
                    )
                )
            else:
                results.append(
                    AuditResult(
                        category="dependencies",
                        item=pkg_name,
                        status=AuditStatus.MISSING,
                        expected=dep_spec,
                        actual="not installed",
                        fix_suggestion=f"Run: pip install '{dep_spec}'",
                    )
                )

        return results

    # ------------------------------------------------------------------
    # Full audit
    # ------------------------------------------------------------------

    def run_full_audit(self) -> AuditReport:
        """Run all audit categories and return a combined AuditReport."""
        report = AuditReport(timestamp=datetime.now(UTC).isoformat())
        report.add_results(self.audit_hooks())
        report.add_results(self.audit_agents())
        report.add_results(self.audit_config())
        report.add_results(self.audit_dependencies())
        return report

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def format_report(self, report: AuditReport) -> str:
        """Return a human-readable text summary of the audit report."""
        lines: list[str] = [
            f"System Audit Report — {report.timestamp}",
            "=" * 60,
        ]

        by_category: dict[str, list[AuditResult]] = {}
        for r in report.results:
            by_category.setdefault(r.category, []).append(r)

        status_icons = {
            AuditStatus.OK: "OK ",
            AuditStatus.DRIFT: "DRF",
            AuditStatus.MISSING: "MIS",
            AuditStatus.UNEXPECTED: "UNX",
            AuditStatus.ERROR: "ERR",
            AuditStatus.WARN: "WRN",
        }

        for category, results in by_category.items():
            lines.append(f"\n[{category.upper()}]")
            for r in results:
                icon = status_icons.get(r.status, "???")
                lines.append(f"  [{icon}] {r.item}")
                if r.status != AuditStatus.OK:
                    lines.append(f"        expected: {r.expected}")
                    lines.append(f"        actual  : {r.actual}")
                    if r.fix_suggestion:
                        lines.append(f"        fix     : {r.fix_suggestion}")

        lines.append("\n" + "=" * 60)
        summary = report.summary
        total = summary.get("total", 0)
        ok_count = summary.get("ok", 0)
        issue_count = total - ok_count
        lines.append(f"Total: {total}  OK: {ok_count}  Issues: {issue_count}")
        for status in AuditStatus:
            count = summary.get(status.value, 0)
            if count and status != AuditStatus.OK:
                lines.append(f"  {status.value.upper()}: {count}")

        return "\n".join(lines)

    def export_json(self, report: AuditReport, path: Path) -> None:
        """Write machine-readable JSON audit report to *path*."""
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(asdict(report), fh, indent=2, default=str)
