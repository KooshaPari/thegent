from pathlib import Path
import re

mappings = {
    "thegent.orchestration.cost": "thegent.cost.tracker",
    "thegent.orchestration.resource.cost": "thegent.cost.tracker",
    "thegent.governance.cost": "thegent.cost.aggregator",
    "thegent.orchestration.budget_alerts": "thegent.cost.budget_alerts",
    "thegent.cli_impl": "thegent.cli.commands.impl",
    "thegent.cli_legacy": "thegent.cli.commands.cli",
    "thegent.cli.legacy.cli_impl": "thegent.cli.commands.impl",
    "thegent.cli.legacy.cli_legacy": "thegent.cli.commands.cli",
    "thegent.cli.legacy.cli_commands_shared_servers": "thegent.cli.commands.cli_commands_shared_servers",
    "thegent.cli.legacy.cli_concurrency": "thegent.cli.commands.cli_concurrency",
    "thegent.cli.legacy.cli_crew": "thegent.cli.commands.cli_crew",
    "thegent.cli.legacy.cli_custom": "thegent.cli.commands.cli_custom",
    "thegent.cli.legacy.cli_document_queue": "thegent.cli.commands.cli_document_queue",
    "thegent.cli.legacy.cli_git": "thegent.cli.commands.cli_git",
    "thegent.cli.legacy.cli_initiative": "thegent.cli.commands.cli_initiative",
    "thegent.cli.legacy.cli_linkcheck": "thegent.cli.commands.cli_linkcheck",
    "thegent.cli.legacy.cli_swarm": "thegent.cli.commands.cli_swarm",
    "thegent.cli.legacy.cli_sync": "thegent.cli.commands.cli_sync",
    "thegent.cli.legacy.cli_teammates": "thegent.cli.commands.cli_teammates",
    "thegent.cli_commands_shared_servers": "thegent.cli.commands.cli_commands_shared_servers",
    "thegent.cli_concurrency": "thegent.cli.commands.cli_concurrency",
    "thegent.cli_crew": "thegent.cli.commands.cli_crew",
    "thegent.cli_custom": "thegent.cli.commands.cli_custom",
    "thegent.cli_document_queue": "thegent.cli.commands.cli_document_queue",
    "thegent.cli_git": "thegent.cli.commands.cli_git",
    "thegent.cli_initiative": "thegent.cli.commands.cli_initiative",
    "thegent.cli_linkcheck": "thegent.cli.commands.cli_linkcheck",
    "thegent.cli_swarm": "thegent.cli.commands.cli_swarm",
    "thegent.cli_sync": "thegent.cli.commands.cli_sync",
    "thegent.cli_teammates": "thegent.cli.commands.cli_teammates",
}


def replace_in_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    new_content = content
    for old in sorted(mappings.keys(), key=len, reverse=True):
        new = mappings[old]
        new_content = new_content.replace(old, new)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {filepath}")

    for path in Path("src").rglob("*.py"):
        replace_in_file(path)

    for path in Path("tests").rglob("*.py"):
        replace_in_file(path)
