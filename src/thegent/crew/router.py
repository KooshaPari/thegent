"""RouterManager with multi-runtime optimized backends."""

import logging
from typing import Any, List, Optional

from thegent.infra.runtime_dispatcher import router_dispatcher

from .router_logic import PurePythonRouter, RouteMetrics, RoutingStrategy

logger = logging.getLogger(__name__)

# Register implementations in the dispatcher
try:
    import thegent_router
    router_dispatcher.register("native", thegent_router.PyParetoRouter())
except ImportError:
    pass

router_dispatcher.register("pypy", PurePythonRouter())
router_dispatcher.register("python", PurePythonRouter())

class RouterManager:
    """
    Unified routing interface that selects the best backend (Rust vs Pure Python).
    """

    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.BALANCED) -> None:
        self.strategy = strategy
        # Get the optimized implementation from the dispatcher
        self._impl = router_dispatcher.get_impl()
        if hasattr(self._impl, "strategy"):
            self._impl.strategy = strategy

    def update_agent_metrics(self, agent_id: str, metrics: RouteMetrics) -> None:
        if hasattr(self._impl, "update_agent_metrics"):
            self._impl.update_agent_metrics(agent_id, metrics)
        elif hasattr(self._impl, "agent_metrics"):
            self._impl.agent_metrics[agent_id] = metrics

    def select_agent(self, task_description: str, available_agents: list) -> Any:
        # Route to the optimized implementation
        if hasattr(self._impl, "select_agent"):
            return self._impl.select_agent(task_description, available_agents)
        if hasattr(self._impl, "route"):
            # Map Rust ParetoRouter interface if needed
            # For now, we assume interfaces are compatible or handled here
            return self._impl.route(task_description)

        return None

    @property
    def backend(self) -> str:
        return self._impl.__class__.__name__
