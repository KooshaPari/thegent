"""Orchestration strategies."""
from typing import Any


class Strategy:
    """Base orchestration strategy."""
    
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
    
    def execute(self, task: Any) -> Any:
        """Execute with this strategy."""
        return task
    
    def select_worker(self, workers: list[Any], task: Any) -> Any:
        """Select appropriate worker for task."""
        return workers[0] if workers else None


class RoundRobinStrategy(Strategy):
    """Round-robin task distribution."""
    
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._index = 0
    
    def select_worker(self, workers: list[Any], task: Any) -> Any:
        if not workers:
            return None
        worker = workers[self._index % len(workers)]
        self._index += 1
        return worker


class LeastLoadedStrategy(Strategy):
    """Select worker with least load."""
    
    def select_worker(self, workers: list[Any], task: Any) -> Any:
        return workers[0] if workers else None
