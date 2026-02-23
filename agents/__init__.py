# thegent-agents
# Agent execution engine sub-project
# Extracted from main repo - Phase 2 P2.2

__version__ = "0.1.0"

from .executor import AgentExecutor
from .pool import AgentPool

__all__ = ["AgentExecutor", "AgentPool"]
