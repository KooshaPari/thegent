import orjson as json
import logging
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any, Literal, TypedDict

from thegent.skills.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes

logger = logging.getLogger(__name__)


class SessionScrapeRequestEvent(TypedDict, total=False):
    event_name: Literal["session.scraper.snapshot.requested"]
    version: Literal["v1"]
    event_id: str
    occurred_at: str
    trigger: str
    project_root: str
    tags: list[str]
    since: str
    max_prompts: int


class SnapshotSummary(TypedDict):
    prompts: int
    commands: int
    files: int
    facts: int
    decisions: int
    tags: int
    sources: list[str]


class SessionSnapshotCreatedEvent(TypedDict):
    event_name: Literal["session.scraper.snapshot.created"]
    version: Literal["v1"]
    event_id: str
    request_event_id: str
    occurred_at: str
    snapshot_id: str
    snapshot_path: str
    summary: SnapshotSummary


class SessionSnapshotFailedEvent(TypedDict, total=False):
    event_name: Literal["session.scraper.snapshot.failed"]
    version: Literal["v1"]
    event_id: str
    request_event_id: str
    occurred_at: str
    error_code: Literal["SCRAPER_IO", "SCRAPER_PARSE", "SCRAPER_RUNTIME"]
    error_message: str
    partial_snapshot_path: str


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
        self.default_event_log = self.default_snapshot_dir / "events.jsonl"

    @staticmethod
    def _normalize_trigger(trigger: str) -> str:
        value = trigger.strip()
        return value or "manual"

    @staticmethod
    def _new_event_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(tz=UTC).isoformat()

    def _extract_structured_signals(
        self, content: str
    ) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
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

            if line.startswith(("$ ", "> ")) and (
                line.startswith("$ ")
                or any(token in line for token in ("git ", "rg ", "python ", "cargo ", "npm ", "uv "))
            ):
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
        now = datetime.now(tz=UTC)
        snapshot_id = now.strftime("snapshot-%Y%m%dT%H%M%S%fZ")
        normalized_trigger = self._normalize_trigger(trigger)

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
            trigger=normalized_trigger,
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

    def persist_snapshot(
        self,
        trigger: str = "manual",
        out_dir: Path | None = None,
        request_event_id: str | None = None,
        event_log: Path | None = None,
    ) -> Path:
        """Persist a structured snapshot as JSON and return its path.

        Optionally emit a session.scraper.snapshot.created or .failed event to event_log.
        """
        try:
            snapshot = self.collect_snapshot(trigger=trigger)
            target_dir = out_dir or self.default_snapshot_dir / datetime.now(tz=UTC).strftime("%Y-%m-%d")
            target_dir.mkdir(parents=True, exist_ok=True)
            path = target_dir / f"{snapshot.snapshot_id}.json"
            path.write_text(json.dumps(snapshot.to_dict().decode(), indent=2), encoding="utf-8")

            # Emit created event if event_log specified
            if event_log:
                created_event: SessionSnapshotCreatedEvent = {
                    "event_name": "session.scraper.snapshot.created",
                    "version": "v1",
                    "event_id": self._new_event_id(),
                    "request_event_id": request_event_id or self._new_event_id(),
                    "occurred_at": self._now_iso(),
                    "snapshot_id": snapshot.snapshot_id,
                    "snapshot_path": str(path),
                    "summary": {
                        "prompts": len(snapshot.prompts),
                        "commands": len(snapshot.commands),
                        "files": len(snapshot.files),
                        "facts": len(snapshot.facts),
                        "decisions": len(snapshot.decisions),
                        "tags": len(snapshot.tags),
                        "sources": snapshot.sources,
                    },
                }
                event_log.parent.mkdir(parents=True, exist_ok=True)
                with open(event_log, "a") as f:
                    f.write(json.dumps(created_event).decode() + "\n")

            return path
        except Exception as e:
            # Emit failed event if event_log specified
            if event_log:
                failed_event: SessionSnapshotFailedEvent = {
                    "event_name": "session.scraper.snapshot.failed",
                    "version": "v1",
                    "event_id": self._new_event_id(),
                    "request_event_id": request_event_id or self._new_event_id(),
                    "occurred_at": self._now_iso(),
                    "error_code": "SCRAPER_RUNTIME",
                    "error_message": str(e),
                }
                event_log.parent.mkdir(parents=True, exist_ok=True)
                with open(event_log, "a") as f:
                    f.write(json.dumps(failed_event).decode() + "\n")
            raise

    def list_snapshots(
        self,
        *,
        limit: int = 50,
        trigger: str | None = None,
        tag: str | None = None,
        since: str | None = None,
        root_dir: Path | None = None,
    ) -> list[Path]:
        """List persisted snapshots, newest first, with optional filters."""
        if limit <= 0:
            return []
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
            if since and snapshot.captured_at < since:
                continue
            filtered.append(path)
            if len(filtered) >= limit:
                break
        return filtered

    def prune_snapshots(self, max_keep: int = 500, root_dir: Path | None = None) -> int:
        """Delete oldest snapshot JSON files beyond max_keep and return deleted count."""
        max_keep = max(max_keep, 0)
        valid_paths = self.list_snapshots(limit=10_000_000, root_dir=root_dir)
        if len(valid_paths) <= max_keep:
            return 0

        deleted = 0
        for path in valid_paths[max_keep:]:
            try:
                path.unlink()
                deleted += 1
            except Exception:
                continue
        return deleted

    def list_triggers(self, limit: int = 500, root_dir: Path | None = None) -> list[str]:
        """Return unique trigger names from newest snapshots in first-seen order."""
        if limit <= 0:
            return []

        triggers: list[str] = []
        seen: set[str] = set()
        for path in self.list_snapshots(limit=limit, root_dir=root_dir):
            snapshot = self.load_snapshot(path)
            if snapshot is None:
                continue
            trigger = snapshot.trigger.strip()
            if not trigger or trigger in seen:
                continue
            seen.add(trigger)
            triggers.append(trigger)
        return triggers

    def list_tags(self, limit: int = 500, root_dir: Path | None = None) -> list[str]:
        """Return unique tags from newest snapshots ordered by frequency desc, then name."""
        if limit <= 0:
            return []

        tag_counts: dict[str, int] = {}
        for path in self.list_snapshots(limit=limit, root_dir=root_dir):
            snapshot = self.load_snapshot(path)
            if snapshot is None:
                continue
            for raw_tag in snapshot.tags:
                tag = raw_tag.strip()
                if not tag:
                    continue
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return [tag for tag, _ in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))]

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
            "generated_at": datetime.now(tz=UTC).isoformat(),
        }

    def persist_snapshot_index(
        self, *, limit: int = 200, out_path: Path | None = None, root_dir: Path | None = None
    ) -> Path:
        """Persist snapshot summary index JSON for downstream dashboards/reporting."""
        summary = self.summarize_snapshots(limit=limit, root_dir=root_dir)
        target = out_path or (self.default_snapshot_dir / "snapshot-index.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return target

    @staticmethod
    def _snapshot_day_key(snapshot: SessionSnapshot, path: Path) -> str:
        captured_at = snapshot.captured_at.strip()
        if captured_at:
            try:
                captured_dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
                return captured_dt.date().isoformat()
            except Exception:
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", captured_at[:10]):
                    return captured_at[:10]

        parent_name = path.parent.name
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", parent_name):
            return parent_name
        return "unknown"

    def summarize_snapshots_by_day(self, limit: int = 1000, root_dir: Path | None = None) -> dict[str, dict[str, int]]:
        """Build per-day totals for snapshots, prompts, commands, and files."""
        if limit <= 0:
            return {}

        daily_counts: dict[str, dict[str, int]] = {}
        for path in self.list_snapshots(limit=limit, root_dir=root_dir):
            snapshot = self.load_snapshot(path)
            if snapshot is None:
                continue

            day = self._snapshot_day_key(snapshot, path)
            day_counts = daily_counts.setdefault(
                day,
                {"snapshots": 0, "prompts": 0, "commands": 0, "files": 0},
            )
            day_counts["snapshots"] += 1
            day_counts["prompts"] += len(snapshot.prompts)
            day_counts["commands"] += len(snapshot.commands)
            day_counts["files"] += len(snapshot.files)

        return dict(sorted(daily_counts.items()))

    def persist_snapshot_daily_index(
        self,
        limit: int = 1000,
        out_path: Path | None = None,
        root_dir: Path | None = None,
    ) -> Path:
        """Persist daily snapshot summary index JSON."""
        summary = self.summarize_snapshots_by_day(limit=limit, root_dir=root_dir)
        target = out_path or (self.default_snapshot_dir / "snapshot-daily-index.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return target

    @staticmethod
    def snapshot_daily_index_markdown(summary: dict) -> str:
        """Render a compact per-day markdown index."""
        lines = [
            "# Snapshot Daily Index",
            "",
            "- `date | snapshots | prompts | commands | files`",
        ]

        if not isinstance(summary, dict) or not summary:
            lines.append("- (none)")
            return "\n".join(lines) + "\n"

        for day in sorted(summary.keys(), reverse=True):
            counts = summary.get(day, {})
            if not isinstance(counts, dict):
                counts = {}
            snapshots = int(counts.get("snapshots", 0) or 0)
            prompts = int(counts.get("prompts", 0) or 0)
            commands = int(counts.get("commands", 0) or 0)
            files = int(counts.get("files", 0) or 0)
            lines.append(f"- `{day} | {snapshots} | {prompts} | {commands} | {files}`")

        return "\n".join(lines) + "\n"

    def export_snapshot_daily_index_markdown(
        self,
        limit: int = 1000,
        out_path: Path | None = None,
        root_dir: Path | None = None,
    ) -> Path:
        """Persist daily snapshot index markdown."""
        summary = self.summarize_snapshots_by_day(limit=limit, root_dir=root_dir)
        target = out_path or (self.default_snapshot_dir / "snapshot-daily-index.md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.snapshot_daily_index_markdown(summary), encoding="utf-8")
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
