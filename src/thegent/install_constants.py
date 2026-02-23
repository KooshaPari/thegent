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
    "claude",
    "factory",
    "both",
}

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
