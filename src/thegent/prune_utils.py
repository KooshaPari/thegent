"""Orphan detection for prune (orphan-by-ppid).

Conservative: only treat as orphan when we are confident the process has no
live Cursor/Claude/Codex/thegent parent. False positives (killing live sessions)
are worse than false negatives (leaving some orphans)."""


def is_agent_in_cmd(cmd: str) -> bool:
    """True if command indicates Cursor/Claude/Codex/thegent (agent parent).
    Conservative: include all known IDE and agent parent process names."""
    if not cmd:
        return False
    c = cmd.lower()
    parts = cmd.split(maxsplit=1)
    exe = (parts[0].split("/")[-1] if parts else "").lower()
    # Cursor IDE and helpers (Electron-based); cursor-agent = node process that IS Cursor agent
    if "cursor" in c or "cursor-agent" in c or "cursor agent" in c:
        return True
    if "electron" in c or exe == "electron":
        return True
    if "cursor helper" in c or "cursorhelper" in c:
        return True
    # Claude Code / Codex
    if "claude-code" in c or "claude code" in c or "clode" in c:
        return True
    if exe in ("claude", "codex", "clode", "dex"):
        return True
    if exe.startswith(("claude", "clode")) or "/claude" in c:
        return True
    if ("codex" in c and ("codex" in exe or exe.endswith("codex"))) or "dex" in c:
        return True
    # thegent spawns droid/codex; Python running thegent is a valid parent
    if exe in ("python", "python3", "python3.12", "python3.14"):
        if "thegent" in c or "uv run" in c or "uv run thegent" in c:
            return True
    return False


def is_orphan_by_ppid(
    pid: int,
    parent_map: dict[int, int],
    cmd_map: dict[int, str],
) -> bool:
    """True if process has no Cursor/Claude/Codex in parent chain (true orphan)."""
    seen: set[int] = set()
    p = pid
    while p and p not in seen:
        seen.add(p)
        ppid = parent_map.get(p)
        if ppid is None:
            return True  # Parent unknown → treat as orphan
        if ppid == 1:
            return True  # Reached init without finding agent
        cmd = cmd_map.get(ppid, "")
        if is_agent_in_cmd(cmd):
            return False  # Has agent parent → keep
        p = ppid
    return True  # Cycle or unknown → treat as orphan
