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
