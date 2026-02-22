import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from thegent.skills.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes

logger = logging.getLogger(__name__)


@dataclass
class SessionSnapshot:
    """Structured snapshot of recently observed session context."""

    snapshot_id: str
    trigger: str
    captured_at: str
    project_root: str
    prompts: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


class SessionScraper:
    """MTSP-18: Session Scraper to extract user prompts and context.
    Focuses on terminal panes (tmux) and local history files.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.default_snapshot_dir = self.project_root / "docs" / "dumps" / "session-snapshots"

    def _extract_structured_signals(self, content: str) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
        prompts: list[str] = []
        commands: list[str] = []
        files: list[str] = []
        facts: list[str] = []
        decisions: list[str] = []
        tags: list[str] = []

        path_pattern = re.compile(r"\b(?:[\w\-.]+/)+[\w\-.]+\b|\b[\w\-.]+\.(?:py|rs|ts|js|json|md|yaml|yml|toml|sh)\b")
        tag_pattern = re.compile(r"#([A-Za-z0-9_-]{2,})")

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith(">") and len(line) > 2:
                prompts.append(line[1:].strip())
            elif "?" in line and len(line) > 10 and not line.lower().startswith("agent"):
                prompts.append(line)

            if line.startswith("$ "):
                commands.append(line[2:].strip())
            elif line.startswith("> ") and any(token in line for token in ("git ", "rg ", "python ", "cargo ", "npm ", "uv ")):
                commands.append(line[2:].strip())

            lowered = line.lower()
            if lowered.startswith("fact:"):
                facts.append(line.split(":", 1)[1].strip())
            if lowered.startswith("decision:"):
                decisions.append(line.split(":", 1)[1].strip())

            files.extend(match.group(0) for match in path_pattern.finditer(line))
            tags.extend(match.group(1) for match in tag_pattern.finditer(line))

        return (
            _dedupe_keep_order(prompts),
            _dedupe_keep_order(commands),
            _dedupe_keep_order(files),
            _dedupe_keep_order(facts),
            _dedupe_keep_order(decisions),
            _dedupe_keep_order(tags),
        )

    def scrape_tmux_prompts(self) -> list[str]:
        """Scrape likely user prompts from active Claude Code tmux panes."""
        prompts: list[str] = []
        panes = list_tmux_panes()

        for pane in panes:
            if is_claude_code_pane(pane):
                content = capture_tmux_pane(pane.pane_id, last_lines=100)
                pane_prompts, *_ = self._extract_structured_signals(content)
                prompts.extend(pane_prompts)

        return _dedupe_keep_order(prompts)

    def scrape_claude_history(self) -> list[str]:
        """Scrape prompts from local Claude history files if they exist."""
        prompts: list[str] = []
        history_dirs = [Path.home() / ".claude" / "history", self.project_root / ".claude" / "history"]

        for hdir in history_dirs:
            if hdir.exists():
                # Read most recent history files
                files = sorted(hdir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
                for f in files[:5]:  # Only look at last 5 sessions
                    try:
                        with open(f) as hfile:
                            # Heuristic: search for "prompt" or "user_input" keys
                            # Format depends on version, but usually contains JSON objects
                            import json

                            data = json.load(hfile)
                            if isinstance(data, list):
                                for entry in data:
                                    if not isinstance(entry, dict):
                                        continue
                                    for key in ("prompt", "user", "user_input", "text"):
                                        value = entry.get(key)
                                        if isinstance(value, str) and value.strip():
                                            prompts.append(value.strip())
                                            break
                    except Exception as e:  # noqa: PERF203 - intentional per-item error handling
                        logger.error(f"Error reading history file {f}: {e}")

        return _dedupe_keep_order(prompts)

    def scrape_ante_history(self) -> list[str]:
        """Scrape prompts from Ante user_input_history.jsonl."""
        import json

        prompts = []
        history_file = Path.home() / ".ante" / "user_input_history.jsonl"

        if not history_file.exists():
            return prompts

        try:
            with open(history_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict) and "prompt" in data:
                            prompt = data["prompt"]
                            if isinstance(prompt, str) and prompt:
                                prompts.append(prompt)
                    except json.JSONDecodeError:
                        logger.debug(f"Failed to parse JSONL line: {line}")
        except Exception as e:
            logger.error(f"Error reading Ante history file {history_file}: {e}")

        return _dedupe_keep_order(prompts)

    def collect_all_recent_prompts(self) -> list[str]:
        """Unified collection from all available scrapers."""
        all_prompts: list[str] = []
        all_prompts.extend(self.scrape_tmux_prompts())
        all_prompts.extend(self.scrape_claude_history())
        all_prompts.extend(self.scrape_ante_history())
        return _dedupe_keep_order(all_prompts)

    def collect_snapshot(self, trigger: str = "manual") -> SessionSnapshot:
        """Collect a rich, structured session snapshot for memory/documentation pipelines."""
        now = datetime.now(tz=timezone.utc)
        snapshot_id = now.strftime("snapshot-%Y%m%dT%H%M%S%fZ")

        prompts: list[str] = []
        commands: list[str] = []
        files: list[str] = []
        facts: list[str] = []
        decisions: list[str] = []
        tags: list[str] = []
        sources: list[str] = []

        panes = list_tmux_panes()
        for pane in panes:
            if not is_claude_code_pane(pane):
                continue
            content = capture_tmux_pane(pane.pane_id, last_lines=150)
            p, c, f, fa, d, t = self._extract_structured_signals(content)
            prompts.extend(p)
            commands.extend(c)
            files.extend(f)
            facts.extend(fa)
            decisions.extend(d)
            tags.extend(t)
            sources.append(f"tmux:{pane.pane_id}")

        claude_prompts = self.scrape_claude_history()
        if claude_prompts:
            prompts.extend(claude_prompts)
            sources.append("claude-history")

        ante_prompts = self.scrape_ante_history()
        if ante_prompts:
            prompts.extend(ante_prompts)
            sources.append("ante-history")

        return SessionSnapshot(
            snapshot_id=snapshot_id,
            trigger=trigger,
            captured_at=now.isoformat(),
            project_root=str(self.project_root),
            prompts=_dedupe_keep_order(prompts),
            commands=_dedupe_keep_order(commands),
            files=_dedupe_keep_order(files),
            facts=_dedupe_keep_order(facts),
            decisions=_dedupe_keep_order(decisions),
            tags=_dedupe_keep_order(tags),
            sources=_dedupe_keep_order(sources),
        )

    def persist_snapshot(self, trigger: str = "manual", out_dir: Path | None = None) -> Path:
        """Persist a structured snapshot as JSON and return its path."""
        snapshot = self.collect_snapshot(trigger=trigger)
        target_dir = out_dir or self.default_snapshot_dir / datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{snapshot.snapshot_id}.json"
        path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        return path

    def list_snapshots(
        self,
        *,
        limit: int = 50,
        trigger: str | None = None,
        tag: str | None = None,
        root_dir: Path | None = None,
    ) -> list[Path]:
        """List persisted snapshots, newest first, with optional filters."""
        search_root = root_dir or self.default_snapshot_dir
        if not search_root.exists():
            return []
        candidates = sorted(search_root.glob("**/snapshot-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        filtered: list[Path] = []
        for path in candidates:
            snapshot = self.load_snapshot(path)
            if snapshot is None:
                continue
            if trigger and snapshot.trigger != trigger:
                continue
            if tag and tag not in snapshot.tags:
                continue
            filtered.append(path)
            if len(filtered) >= max(0, limit):
                break
        return filtered

    def load_snapshot(self, path: Path) -> SessionSnapshot | None:
        """Load a snapshot JSON file into SessionSnapshot."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        try:
            return SessionSnapshot(
                snapshot_id=str(data.get("snapshot_id", "")),
                trigger=str(data.get("trigger", "unknown")),
                captured_at=str(data.get("captured_at", "")),
                project_root=str(data.get("project_root", str(self.project_root))),
                prompts=list(data.get("prompts", [])),
                commands=list(data.get("commands", [])),
                files=list(data.get("files", [])),
                facts=list(data.get("facts", [])),
                decisions=list(data.get("decisions", [])),
                tags=list(data.get("tags", [])),
                sources=list(data.get("sources", [])),
            )
        except Exception:
            return None

    def latest_snapshot(self, *, root_dir: Path | None = None) -> SessionSnapshot | None:
        """Return the newest available snapshot if present."""
        paths = self.list_snapshots(limit=1, root_dir=root_dir)
        if not paths:
            return None
        return self.load_snapshot(paths[0])

    def snapshot_markdown(self, snapshot: SessionSnapshot) -> str:
        """Render a SessionSnapshot as concise markdown."""
        lines = [
            f"# Session Snapshot: {snapshot.snapshot_id}",
            "",
            f"- Trigger: {snapshot.trigger}",
            f"- Captured: {snapshot.captured_at}",
            f"- Project: {snapshot.project_root}",
            "",
            "## Prompts",
        ]
        lines.extend([f"- {p}" for p in snapshot.prompts] or ["- (none)"])
        lines.append("")
        lines.append("## Commands")
        lines.extend([f"- `{c}`" for c in snapshot.commands] or ["- (none)"])
        lines.append("")
        lines.append("## Files")
        lines.extend([f"- `{f}`" for f in snapshot.files] or ["- (none)"])
        lines.append("")
        lines.append("## Facts")
        lines.extend([f"- {f}" for f in snapshot.facts] or ["- (none)"])
        lines.append("")
        lines.append("## Decisions")
        lines.extend([f"- {d}" for d in snapshot.decisions] or ["- (none)"])
        lines.append("")
        lines.append("## Tags")
        lines.extend([f"- #{t}" for t in snapshot.tags] or ["- (none)"])
        return "\n".join(lines) + "\n"

    def export_snapshot_markdown(self, snapshot_path: Path, out_path: Path | None = None) -> Path:
        """Export snapshot JSON to markdown beside the source (or a provided destination)."""
        snapshot = self.load_snapshot(snapshot_path)
        if snapshot is None:
            raise ValueError(f"Could not load snapshot: {snapshot_path}")
        target = out_path or snapshot_path.with_suffix(".md")
        target.write_text(self.snapshot_markdown(snapshot), encoding="utf-8")
        return target

    def summarize_snapshots(self, *, limit: int = 200, root_dir: Path | None = None) -> dict[str, Any]:
        """Build summary stats from recent snapshots for memory/research reporting."""
        paths = self.list_snapshots(limit=limit, root_dir=root_dir)
        trigger_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}
        total_prompts = 0
        total_commands = 0
        total_files = 0
        latest_captured_at: str | None = None

        for path in paths:
            snapshot = self.load_snapshot(path)
            if snapshot is None:
                continue
            trigger_counts[snapshot.trigger] = trigger_counts.get(snapshot.trigger, 0) + 1
            for tag in snapshot.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            total_prompts += len(snapshot.prompts)
            total_commands += len(snapshot.commands)
            total_files += len(snapshot.files)
            if latest_captured_at is None or snapshot.captured_at > latest_captured_at:
                latest_captured_at = snapshot.captured_at

        return {
            "project_root": str(self.project_root),
            "total_snapshots": len(paths),
            "total_prompts": total_prompts,
            "total_commands": total_commands,
            "total_files": total_files,
            "trigger_counts": dict(sorted(trigger_counts.items())),
            "tag_counts": dict(sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
            "latest_captured_at": latest_captured_at,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    def persist_snapshot_index(self, *, limit: int = 200, out_path: Path | None = None, root_dir: Path | None = None) -> Path:
        """Persist snapshot summary index JSON for downstream dashboards/reporting."""
        summary = self.summarize_snapshots(limit=limit, root_dir=root_dir)
        target = out_path or (self.default_snapshot_dir / "snapshot-index.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return target

    @staticmethod
    def snapshot_index_markdown(summary: dict[str, Any]) -> str:
        """Render snapshot summary index as markdown."""
        lines = [
            "# Snapshot Index",
            "",
            f"- Project: {summary.get('project_root', '')}",
            f"- Total snapshots: {summary.get('total_snapshots', 0)}",
            f"- Total prompts: {summary.get('total_prompts', 0)}",
            f"- Total commands: {summary.get('total_commands', 0)}",
            f"- Total files: {summary.get('total_files', 0)}",
            f"- Latest captured_at: {summary.get('latest_captured_at') or '(none)'}",
            "",
            "## Trigger Counts",
        ]
        trigger_counts = summary.get("trigger_counts", {})
        lines.extend([f"- {k}: {v}" for k, v in trigger_counts.items()] or ["- (none)"])
        lines.extend(["", "## Top Tags"])
        tag_counts = summary.get("tag_counts", {})
        lines.extend([f"- #{k}: {v}" for k, v in tag_counts.items()] or ["- (none)"])
        return "\n".join(lines) + "\n"

    def export_snapshot_index_markdown(
        self,
        *,
        limit: int = 200,
        out_path: Path | None = None,
        root_dir: Path | None = None,
    ) -> Path:
        """Persist snapshot index markdown."""
        summary = self.summarize_snapshots(limit=limit, root_dir=root_dir)
        target = out_path or (self.default_snapshot_dir / "snapshot-index.md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.snapshot_index_markdown(summary), encoding="utf-8")
        return target
