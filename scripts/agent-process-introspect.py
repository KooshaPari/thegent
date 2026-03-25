#!/usr/bin/env python3
"""Agent process introspection and optimization analysis.

Identifies Python, node, droid, claude, codex processes; checks parent chain
for true orphans (no Cursor/Claude/Codex parent); aggregates memory/CPU.
Does NOT assume leak—reports facts. Use --dry-run before any prune action.

Usage:
  python scripts/agent-process-introspect.py              # Full report
  python scripts/agent-process-introspect.py --json       # Machine-readable
  python scripts/agent-process-introspect.py --optimize   # Suggest optimizations
"""

from __future__ import annotations

import argparse
import orjson as json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class ProcessInfo:
    pid: int
    ppid: int
    rss_kb: int
    rss_mb: float
    cpu_pct: float
    cpu_time: str
    command: str
    exe: str
    is_orphan: bool | None = None
    parent_chain: list[str] = field(default_factory=list)


@dataclass
class ProcessGroup:
    exe: str
    count: int
    total_rss_mb: float
    total_cpu_pct: float
    processes: list[ProcessInfo]
    orphan_count: int = 0
    orphan_rss_mb: float = 0.0


def _run_ps() -> str:
    """Run ps with pid,ppid,rss,pcpu,time,command."""
    try:
        res = subprocess.run(
            ["ps", "-eo", "pid,ppid,rss,pcpu,time,command"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return res.stdout or ""
    except Exception as e:
        print(f"Error running ps: {e}", file=sys.stderr)
        return ""


def _parse_ps_line(line: str) -> ProcessInfo | None:
    """Parse a single ps line. Returns None if unparseable."""
    parts = line.split(None, 5)
    if len(parts) < 6:
        return None
    try:
        pid = int(parts[0])
        ppid = int(parts[1])
        rss_kb = int(parts[2])
        cpu_pct = float(parts[3].replace(",", ".") or 0)
        cpu_time = parts[4]
        cmd = parts[5]
    except (ValueError, IndexError):
        return None
    rss_mb = rss_kb / 1024
    exe = _extract_exe(cmd)
    return ProcessInfo(
        pid=pid,
        ppid=ppid,
        rss_kb=rss_kb,
        rss_mb=rss_mb,
        cpu_pct=cpu_pct,
        cpu_time=cpu_time,
        command=cmd,
        exe=exe,
    )


def _extract_exe(cmd: str) -> str:
    """Extract executable name from command."""
    if not cmd:
        return "unknown"
    first = cmd.split(maxsplit=1)[0]
    return Path(first).name if "/" in first else first


def _is_agent_parent(cmd: str) -> bool:
    """True if command indicates Cursor/Claude/Codex/thegent (agent parent).
    Must match prune_utils.is_agent_in_cmd for consistency."""
    if not cmd:
        return False
    c = cmd.lower()
    exe = _extract_exe(cmd).lower()
    if "cursor" in c or "cursor-agent" in c or "cursor agent" in c:
        return True
    if "electron" in c or exe == "electron":
        return True
    if "cursor helper" in c or "cursorhelper" in c:
        return True
    if "claude-code" in c or "claude code" in c or "clode" in c:
        return True
    if exe in ("claude", "codex", "clode", "dex", "ante", "anen", "antigma", "fanta"):
        return True
    if exe.startswith(("claude", "clode", "ante", "anen", "antigma", "fanta")) or any(
        x in c for x in ("/claude", "/ante", "/anen", "/antigma", "/fanta")
    ):
        return True
    if ("codex" in c and "codex" in exe) or "dex" in c:
        return True
    if exe in ("python", "python3", "python3.12", "python3.14"):
        if "thegent" in c or "uv run" in c:
            return True
    return False


def _check_orphan(
    pid: int,
    parent_map: dict[int, int],
    cmd_map: dict[int, str],
) -> tuple[bool, list[str]]:
    """Check if process is orphan (no agent parent in chain). Returns (is_orphan, parent_chain)."""
    chain: list[str] = []
    seen: set[int] = set()
    p = pid
    while p and p not in seen:
        seen.add(p)
        ppid = parent_map.get(p)
        cmd = cmd_map.get(p, "")
        chain.append(f"{p}:{_extract_exe(cmd)}")
        if ppid is None:
            return True, chain
        if ppid == 1:
            return True, chain
        if _is_agent_parent(cmd):
            return False, chain
        p = ppid
    return True, chain


# Agent-related executables to group
AGENT_EXES = frozenset(
    {
        "python",
        "python3",
        "python3.12",
        "python3.14",
        "Python",
        "node",
        "nodejs",
        "droid",
        "roid",
        "claude",
        "clode",
        "codex",
        "dex",
        "cli-proxy-api-plus",
        "process-compose",
        "cursor-shell",
    }
)


def _is_agent_process(exe: str, cmd: str) -> bool:
    """True if process is agent-related."""
    exe_lower = exe.lower()
    cmd_lower = cmd.lower()
    if exe_lower in ("python", "python3", "python3.12", "python3.14"):
        if "thegent" in cmd_lower or "claude" in cmd_lower or "codex" in cmd_lower:
            return True
        if "uv" in cmd_lower and "run" in cmd_lower:
            return True
    if exe_lower in ("node", "nodejs"):
        if any(x in cmd_lower for x in ("mcp", "tsserver", "pyright", "cc-status", "playwright", "context7")):
            return True
        if "npm" in cmd_lower or "bun" in cmd_lower:
            return True
    if exe_lower in ("droid", "roid", "claude", "clode", "codex", "dex", "ante", "anen", "antigma", "fanta"):
        return True
    if "cli-proxy" in cmd_lower or "process-compose" in cmd_lower:
        return True
    return False


def introspect() -> dict:
    """Run full introspection. Returns structured report."""
    stdout = _run_ps()
    lines = stdout.strip().splitlines()
    if not lines:
        return {"error": "No ps output", "groups": [], "summary": {}}

    parent_map: dict[int, int] = {}
    cmd_map: dict[int, str] = {}
    all_procs: list[ProcessInfo] = []

    for line in lines[1:]:
        proc = _parse_ps_line(line)
        if proc and _is_agent_process(proc.exe, proc.command):
            parent_map[proc.pid] = proc.ppid
            cmd_map[proc.pid] = proc.command
            all_procs.append(proc)

    for proc in all_procs:
        is_orphan, chain = _check_orphan(proc.pid, parent_map, cmd_map)
        proc.is_orphan = is_orphan
        proc.parent_chain = chain

    groups: dict[str, ProcessGroup] = {}
    for proc in all_procs:
        key = proc.exe
        if key not in groups:
            groups[key] = ProcessGroup(
                exe=key,
                count=0,
                total_rss_mb=0,
                total_cpu_pct=0,
                processes=[],
                orphan_count=0,
                orphan_rss_mb=0,
            )
        g = groups[key]
        g.count += 1
        g.total_rss_mb += proc.rss_mb
        g.total_cpu_pct += proc.cpu_pct
        g.processes.append(proc)
        if proc.is_orphan:
            g.orphan_count += 1
            g.orphan_rss_mb += proc.rss_mb

    for g in groups.values():
        g.processes.sort(key=lambda p: p.rss_mb, reverse=True)

    total_rss = sum(p.rss_mb for p in all_procs)
    orphan_rss = sum(p.rss_mb for p in all_procs if p.is_orphan)
    orphan_count = sum(1 for p in all_procs if p.is_orphan)

    return {
        "groups": [asdict(g) for g in sorted(groups.values(), key=lambda x: -x.total_rss_mb)],
        "summary": {
            "total_processes": len(all_procs),
            "total_rss_mb": round(total_rss, 1),
            "total_rss_gb": round(total_rss / 1024, 2),
            "orphan_count": orphan_count,
            "orphan_rss_mb": round(orphan_rss, 1),
            "orphan_rss_gb": round(orphan_rss / 1024, 2),
        },
    }


def _optimization_strategies() -> dict[str, list[str]]:
    """Per-process-type optimization strategies."""
    return {
        "Python": [
            "Reduce THGENT_MAX_CONCURRENCY to limit parallel sessions",
            "Run 'thegent mcp prune --force' to kill orphan node processes first",
            "Close idle Cursor/IDE tabs; each tab can hold LSP/MCP",
            "Use 'thegent ps --all' to identify long-idle sessions; stop with thegent stop <session_id>",
        ],
        "node": [
            "Run 'thegent mcp prune --force' (kills orphan LSP/MCP/cc-status)",
            "Run 'thegent mcp spotlight-exclude' to reduce mds_stores overhead",
            "Disable unused MCP servers in Cursor settings",
            "Consider THGENT_AUTO_PRUNE=1 for auto-prune on session stop",
        ],
        "droid": [
            "Droid runs are per-request; multiple droids = parallel work",
            "Check if droids are stuck: ps -p <pid> -o etime= for elapsed time",
            "Stop idle thegent sessions: thegent stop <session_id>",
            "Factory droid may cache context; restart droid CLI if memory grows",
        ],
        "claude": [
            "Claude Code sessions; close unused IDE windows",
            "thegent stop <session_id> for background sessions",
            "Long CPU time may indicate active inference—not necessarily leak",
        ],
        "codex": [
            "Codex sessions; close unused dex/codex windows",
            "thegent stop <session_id> for background sessions",
        ],
        "cli-proxy-api-plus": [
            "CLI proxy for OAuth; one per cliproxy port",
            "Normal to have 2–3; many may indicate restarts—check cliproxy logs",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Agent process introspection")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    ap.add_argument("--optimize", action="store_true", help="Include optimization strategies")
    ap.add_argument("--dry-run", action="store_true", help="Alias for introspect-only (no actions)")
    args = ap.parse_args()

    report = introspect()
    if "error" in report:
        print(json.dumps(report).decode().decode() if args.json else report["error"], file=sys.stderr)
        sys.exit(1)

    if args.optimize:
        report["strategies"] = _optimization_strategies()

    if args.json:
        print(json.dumps(report, indent=2).decode().decode())
        return

    # Human-readable output
    s = report["summary"]
    print("=== Agent Process Introspection ===\n")
    print(f"Total: {s['total_processes']} processes, {s['total_rss_gb']} GB RSS")
    print(f"Orphans (no Cursor/Claude/Codex parent): {s['orphan_count']} processes, {s['orphan_rss_gb']} GB\n")

    for g in report["groups"]:
        exe = g["exe"]
        print(f"--- {exe} ({g['count']} procs, {g['total_rss_mb']:.0f} MB) ---")
        if g["orphan_count"] > 0:
            print(f"  Orphans: {g['orphan_count']} ({g['orphan_rss_mb']:.0f} MB)")
        for p in g["processes"][:5]:
            orphan_mark = " [ORPHAN]" if p.get("is_orphan") else ""
            print(f"  PID {p['pid']}: {p['rss_mb']:.0f} MB, {p['cpu_pct']}% CPU, {p['cpu_time']}{orphan_mark}")
        if len(g["processes"]) > 5:
            print(f"  ... and {len(g['processes']) - 5} more")
        print()

    if args.optimize:
        print("=== Optimization Strategies ===\n")
        for exe, strategies in report.get("strategies", {}).items():
            print(f"{exe}:")
            for strat in strategies:
                print(f"  • {strat}")
            print()


if __name__ == "__main__":
    main()
