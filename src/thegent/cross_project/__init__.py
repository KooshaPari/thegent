"""Cross-project integrations."""

from thegent.cross_project.dex_flash_agents import DexFlashAgents
from thegent.cross_project.ipc import CrossProjectIPC
from thegent.cross_project.plangent_subagents import PlangentSubagents
from thegent.cross_project.registry import CrossProjectRegistry

__all__ = [
    "CrossProjectIPC",
    "CrossProjectRegistry",
    "DexFlashAgents",
    "PlangentSubagents",
]
