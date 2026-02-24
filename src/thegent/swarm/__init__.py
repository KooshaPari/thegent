"""
Multi-Agent Swarm Orchestration

Swarm intelligence for parallel agent execution with:
- Agent specialization
- Fast communication protocols
- Dynamic task decomposition
- Load balancing
"""

from .orchestrator import SwarmOrchestrator
from .communication import SwarmChannel
from .balancer import LoadBalancer

__all__ = ["SwarmOrchestrator", "SwarmChannel", "LoadBalancer"]
