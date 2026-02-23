"""Constants and static mappings used by install workflows."""

VALID_TARGETS = {
    "claude-code",
    "claude-desktop",
    "cursor",
    "codex",
    "droid",
    "envrc",
    "shell",
    "harness",
    "system",
    "git-lock-cleanup",
    "all",
    "auto",
    "claude",
    "factory",
    "both",
}

# Actual installable targets (excludes meta-targets like "all", "both", "claude")
INSTALLABLE_TARGETS = [
    "claude-code",
    "claude-desktop",
    "cursor",
    "codex",
    "droid",
    "envrc",
    "shell",
    "harness",
    "factory",
    "system",
    "git-lock-cleanup",
]

# Mapping of harness names to their config directories
HARNESS_CONFIG_PATHS = {
    "claude-code": "~/.claude",
    "claude-desktop": "~/.config/Claude",  # Linux, or ~/Library/Application Support/Claude on macOS
    "cursor": "~/.cursor",
    "codex": "~/.codex",
    "droid": "~/.factory",
    "factory": "~/.factory",
}


def detect_installed_harnesses() -> list[str]:
    """Auto-detect which harnesses are installed on the system.

    Returns list of detected harness names (e.g., ["claude-code", "codex", "droid"])
    """
    import os
    from pathlib import Path

    detected = []
    home = Path.home()

    for harness, config_path in HARNESS_CONFIG_PATHS.items():
        expanded = Path(config_path).expanduser()
        if expanded.exists():
            detected.append(harness)

    # Check for Codex CLI
    if os.environ.get("CODEX_AVAILABLE") or (home / ".codex" / "mcp.json").exists():
        if "codex" not in detected:
            detected.append("codex")

    # Check for Claude CLI
    if (home / ".claude" / "settings.json").exists() or (home / ".claude.json").exists():
        if "claude-code" not in detected:
            detected.append("claude-code")

    # Check for Cursor
    if (home / ".cursor" / "settings.json").exists():
        if "cursor" not in detected:
            detected.append("cursor")

    # Check for Factory Droid
    if (home / ".factory" / "settings.json").exists() or (home / ".factory" / "config.json").exists():
        if "droid" not in detected:
            detected.append("droid")
        if "factory" not in detected:
            detected.append("factory")

    return detected


def get_targets_for_install(
    target: str,
    auto_detect: bool = True,
) -> list[str]:
    """Get list of targets to install based on target parameter.

    Args:
        target: Target string ("all", "auto", specific target, or comma-separated list)
        auto_detect: If True and target="auto", detect installed harnesses

    Returns:
        List of target names to install
    """
    if target == "all":
        return INSTALLABLE_TARGETS.copy()

    if target == "auto" and auto_detect:
        return detect_installed_harnesses()

    # Handle comma-separated list
    if "," in target:
        targets = [t.strip() for t in target.split(",")]
        result = []
        for t in targets:
            if t == "all":
                result.extend(INSTALLABLE_TARGETS)
            elif t == "auto" and auto_detect:
                result.extend(detect_installed_harnesses())
            else:
                result.append(t)
        return result

    return [target]

SHELL_FILES = {
    ".zshenv": ".zshenv",
    ".zsh_bundle.zsh": ".zsh_bundle.zsh",
    ".zsh_safeguards.zsh": ".zsh_safeguards.zsh",
    ".zsh_optimization.zsh": ".zsh_optimization.zsh",
    ".zsh_advanced.zsh": ".zsh_advanced.zsh",
    ".zsh_worktree_governance.zsh": ".zsh_worktree_governance.zsh",
    ".zshrc": ".zshrc",
}
SHELL_LOCAL_TEMPLATE = "zshrc.local.template"

EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "history.jsonl",
    "session-env",
    "debug",
    "todos",
    "tasks",
    "teams",
    "shell-snapshots",
    "file-history",
    "paste-cache",
    ".git",
    ".venv",
    "node_modules",
}

CLAUDE_CODE_FILES = {
    "skills/thegent-skills": "skills/thegent-skills",
    "skills/sitback-agent": "skills/sitback-agent",
    "hooks": "hooks",
    "templates": "templates",
    "agents": "agents",
    "commands": "commands",
    "contracts": "contracts",
    "CLAUDE.md": "CLAUDE.md",
    "mcp_servers.json": "mcp_servers.json",
    "qa-config.json": "qa-config.json",
}

CURSOR_FILES = {
    "skills/thegent-skills": "skills-cursor/thegent-skills",
}

FACTORY_FILES = {
    ".factory/hooks": "hooks",
    ".factory/skills": "skills",
    ".factory/commands": "commands",
    ".factory/droids": "droids",
    ".factory/plugins": "plugins",
    ".factory/mcp.json": "mcp.json",
    ".factory/config.json": "config.json",
    ".factory/settings.json": "settings.json",
}

# Project-level scaffold files (go to project_dir/.client)
FACTORY_PROJECT_FILES = {
    ".factory/hooks": ".factory/hooks",
    ".factory/skills": ".factory/skills",
    ".factory/commands": ".factory/commands",
    ".factory/droids": ".factory/droids",
    ".factory/plugins": ".factory/plugins",
    ".factory/mcp.json": ".factory/mcp.json",
    ".factory/config.json": ".factory/config.json",
    ".factory/settings.json": ".factory/settings.json",
}

CODEX_PROJECT_FILES = {
    ".codex/hooks": ".codex/hooks",
    ".codex/skills": ".codex/skills",
    ".codex/commands": ".codex/commands",
    ".codex/droids": ".codex/droids",
    ".codex/plugins": ".codex/plugins",
    ".codex/mcp.json": ".codex/mcp.json",
    ".codex/config.json": ".codex/config.json",
    ".codex/settings.json": ".codex/settings.json",
}

CLAUDE_PROJECT_FILES = {
    ".claude/hooks": ".claude/hooks",
    ".claude/skills": ".claude/skills",
    ".claude/commands": ".claude/commands",
    ".claude/agents": ".claude/agents",
    ".claude/contracts": ".claude/contracts",
    ".claude/templates": ".claude/templates",
    ".claude/mcp_servers.json": ".claude/mcp_servers.json",
    ".claude/qa-config.json": ".claude/qa-config.json",
    "CLAUDE.md": "CLAUDE.md",
}

CURSOR_PROJECT_FILES = {
    ".cursor/hooks": ".cursor/hooks",
    ".cursor/skills-cursor": ".cursor/skills",
    ".cursor/mcp_servers.json": ".cursor/mcp_servers.json",
    ".cursor/qa-config.json": ".cursor/qa-config.json",
}

THEGENT_TOOLS = [
    "thegent_run",
    "thegent_bg",
    "thegent_ps",
    "thegent_status",
    "thegent_logs",
    "thegent_inspect",
    "thegent_stop",
    "thegent_wait",
    "thegent_list_agents",
    "thegent_list_droids",
    "thegent_list_models",
    "thegent_dag_list",
    "thegent_observe_summary",
    "thegent_sitback_dashboard",
    "thegent_session_contracts",
    "thegent_session_contract_health_gate",
    "thegent_session_contract_health_report",
    "thegent_session_contract_health_trend",
    "thegent_resolve_model_route",
    "thegent_suggest_prompt",
]

CLAUDE_MAPPING = CLAUDE_CODE_FILES
FACTORY_MAPPING = FACTORY_FILES

ROOT_FILES = {"CLAUDE.md", "mcp_servers.json", "qa-config.json"}
