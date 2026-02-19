"""RouterManager for cost/performance/balanced routing."""

from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any

from .agent import CrewAgent


class RoutingStrategy(StrEnum):
    """Routing strategies."""

    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"


@dataclass
class RouteMetrics:
    """Metrics for routing decisions."""

    cost_per_token: float = 0.0
    latency_ms: float = 0.0
    success_rate: float = 1.0
    availability: float = 1.0


class RouterManager:
    """
    Unified routing interface for agent selection.

    Manages:
    - Cost-optimized routing
    - Performance-optimized routing
    - Balanced routing
    - Route caching
    - Statistics tracking
    """

    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.BALANCED) -> None:
        """
        Initialize RouterManager.

        Args:
            strategy: Routing strategy to use
        """
        self.strategy = strategy
        self.route_cache: dict[str, str] = {}  # task_signature -> agent_id
        self.statistics: dict[str, Any] = {
            "routes_made": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        self.agent_metrics: dict[str, RouteMetrics] = {}

    def update_agent_metrics(self, agent_id: str, metrics: RouteMetrics) -> None:
        """Update metrics for an agent."""
        self.agent_metrics[agent_id] = metrics

    def select_agent(
        self,
        task_description: str,
        available_agents: list[CrewAgent],
    ) -> CrewAgent | None:
        """
        Select best agent for a task based on routing strategy.

        Args:
            task_description: Task description
            available_agents: List of available agents

        Returns:
            Selected agent or None
        """
        if not available_agents:
            return None

        # Check cache
        cache_key = f"{self.strategy.value}:{task_description[:50]}"
        if cache_key in self.route_cache:
            cached_agent_id = self.route_cache[cache_key]
            cached_agent = next((a for a in available_agents if a.id == cached_agent_id), None)
            if cached_agent:
                self.statistics["cache_hits"] += 1
                return cached_agent

        self.statistics["cache_misses"] += 1

        # Route based on strategy
        if self.strategy == RoutingStrategy.COST_OPTIMIZED:
            agent = self._select_cost_optimized(task_description, available_agents)
        elif self.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            agent = self._select_performance_optimized(task_description, available_agents)
        else:
            agent = self._select_balanced(task_description, available_agents)

        # Cache result
        if agent:
            self.route_cache[cache_key] = agent.id
            self.statistics["routes_made"] += 1

        return agent

    def _select_cost_optimized(
        self,
        task_description: str,
        agents: list[CrewAgent],
    ) -> CrewAgent | None:
        """Select agent with lowest cost."""
        if not agents:
            return None

        best_agent = None
        best_cost = float("inf")

        for agent in agents:
            metrics = self.agent_metrics.get(agent.id, RouteMetrics())
            if metrics.cost_per_token < best_cost:
                best_cost = metrics.cost_per_token
                best_agent = agent

        return best_agent or agents[0]

    def _select_performance_optimized(
        self,
        task_description: str,
        agents: list[CrewAgent],
    ) -> CrewAgent | None:
        """Select agent with best performance (lowest latency)."""
        if not agents:
            return None

        best_agent = None
        best_latency = float("inf")

        for agent in agents:
            metrics = self.agent_metrics.get(agent.id, RouteMetrics())
            if metrics.latency_ms < best_latency:
                best_latency = metrics.latency_ms
                best_agent = agent

        return best_agent or agents[0]

    def _select_balanced(
        self,
        task_description: str,
        agents: list[CrewAgent],
    ) -> CrewAgent | None:
        """Select agent with balanced cost/performance."""
        if not agents:
            return None

        # Simple balanced: prefer agents with good success rate and availability
        best_agent = None
        best_score = -1.0

        for agent in agents:
            metrics = self.agent_metrics.get(agent.id, RouteMetrics())
            # Score = success_rate * availability / (cost_per_token + latency_ms/1000)
            score = (metrics.success_rate * metrics.availability) / (
                max(metrics.cost_per_token, 0.001) + max(metrics.latency_ms / 1000, 0.001)
            )
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent or agents[0]
