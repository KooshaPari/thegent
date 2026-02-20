"""Regex-based agent detection using agents.conf."""

import configparser
import os
import re
from pathlib import Path
from typing import Any

try:
    from .process_detection import detect_agents
except ImportError:
    from process_detection import detect_agents

DEFAULT_AGENTS_CONF = """
[agents]
claude = claude-code|clode
cursor = cursor-agent|cursor
thegent = thegent
codex = codex
copilot = copilot
roo = roo-code|roo
kilo = kilo-code|kilo
"""


def get_config_path() -> Path:
    """Get path to agents.conf."""
    # Priority: current dir, then ~/.heliosShield/agents.conf
    local_conf = Path.cwd() / "agents.conf"
    if local_conf.exists():
        return local_conf

    home_conf = Path.home() / ".heliosShield" / "agents.conf"
    if not home_conf.parent.exists():
        home_conf.parent.mkdir(parents=True, exist_ok=True)

    if not home_conf.exists():
        home_conf.write_text(DEFAULT_AGENTS_CONF.strip())

    return home_conf


def load_agent_patterns() -> dict[str, str]:
    """Load agent regex patterns from agents.conf."""
    config_path = get_config_path()
    config = configparser.ConfigParser()

    try:
        config.read(config_path)
        if "agents" in config:
            return dict(config["agents"])
    except Exception as e:
        pass

    return {
        "claude": r"claude-code|clode",
        "cursor": r"cursor-agent|cursor",
        "thegent": r"thegent",
        "codex": r"codex",
        "copilot": r"copilot",
    }


def run_detection() -> list[dict[str, Any]]:
    """Load patterns and detect agents."""
    patterns = load_agent_patterns()
    return detect_agents(patterns)


if __name__ == "__main__":
    # Handle direct execution without relative import issues
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent))
    from thegent.mesh.agent_patterns import run_detection

    agents = run_detection()
    for _a in agents:
        pass
