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
    # Claude Code / Codex / Droid / etc.
    if any(
        x in c
        for x in (
            "claude-code",
            "claude code",
            "clode",
            "cursor-agent",
            "cursor agent",
            "opencode",
            "copilot",
            "gemini",
            "droid",
            "roid",
            "anen",
            "antigma",
            "fanta",
            "ante",
            "factory",
        )
    ):
        return True
    if exe in ("claude", "codex", "clode", "dex", "droid", "roid", "anen", "antigma", "fanta", "ante", "opencode", "copilot", "gemini"):
        return True
    if exe.startswith(("claude", "clode", "droid", "roid", "anen", "antigma", "fanta", "ante", "opencode")) or any(
        x in c for x in ("/claude", "/droid", "/anen", "/antigma", "/fanta", "/ante", "/opencode")
    ):
        return True
    if ("codex" in c and ("codex" in exe or exe.endswith("codex"))) or "dex" in c:
        return True
    # thegent spawns droid/codex; Python running thegent is a valid parent
    if exe in ("python", "python3", "python3.12", "python3.14"):
        if "thegent" in c or "uv run" in c or "uv run thegent" in c:
            return True
    # System / Terminal parents (to avoid killing user shells)
    if exe in ("iterm2", "iterm", "terminal", "tmux", "screen", "login", "sshd", "zsh", "bash", "sh"):
        return True
    if "iterm" in c or "terminal.app" in c or "tmux" in c or "sshd" in c:
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
