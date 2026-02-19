"""Speculative execution strategies for resource optimization.

WP-5001: Multi-provider racing, adaptive timeouts, cost-quality tradeoffs.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)


class SpeculativeStrategy(Enum):
    """Speculative execution strategies."""
    
    RACE_FIRST = "race_first"  # Race multiple providers, use first result
    RACE_BEST = "race_best"  # Race multiple providers, use best quality
    ADAPTIVE_TIMEOUT = "adaptive_timeout"  # Adjust timeout based on historical performance
    COST_QUALITY_TRADEOFF = "cost_quality_tradeoff"  # Balance cost vs quality
    EARLY_TERMINATION = "early_termination"  # Terminate slow providers early


@dataclass
class SpeculativeConfig:
    """Configuration for speculative execution."""
    
    strategy: SpeculativeStrategy = SpeculativeStrategy.RACE_FIRST
    providers: list[str] = None  # List of providers to race
    timeout_ms: int = 5000
    quality_threshold: float = 0.8
    cost_budget_usd: float = 0.01
    
    # Adaptive parameters
    historical_latency_p95_ms: float = 2000.0
    historical_quality_avg: float = 0.85
    
    def __post_init__(self):
        if self.providers is None:
            self.providers = ["free", "claude", "gemini"]


def compute_adaptive_timeout(
    historical_p95_ms: float,
    base_timeout_ms: int = 5000,
    safety_multiplier: float = 1.5,
) -> int:
    """Compute adaptive timeout based on historical performance."""
    return int(max(base_timeout_ms, historical_p95_ms * safety_multiplier))


def select_speculative_providers(
    available_providers: list[str],
    strategy: SpeculativeStrategy,
    cost_budget: float = 0.01,
) -> list[str]:
    """Select providers for speculative execution based on strategy."""
    # Provider cost estimates (per request, approximate)
    provider_costs = {
        "free": 0.0,
        "gemini": 0.0001,
        "claude": 0.001,
        "codex": 0.0005,
    }
    
    if strategy == SpeculativeStrategy.COST_QUALITY_TRADEOFF:
        # Select providers within budget
        selected = []
        total_cost = 0.0
        for provider in available_providers:
            cost = provider_costs.get(provider, 0.001)
            if total_cost + cost <= cost_budget:
                selected.append(provider)
                total_cost += cost
        return selected[:3]  # Limit to 3 providers
    
    # Default: race top 2-3 providers
    return available_providers[:3]


def should_terminate_early(
    elapsed_ms: float,
    timeout_ms: int,
    other_results: list[Any],
    strategy: SpeculativeStrategy,
) -> bool:
    """Determine if a speculative execution should terminate early."""
    if strategy == SpeculativeStrategy.EARLY_TERMINATION:
        # Terminate if we have a result and elapsed > 50% of timeout
        if other_results and elapsed_ms > timeout_ms * 0.5:
            return True
    
    # Always terminate if timeout exceeded
    if elapsed_ms > timeout_ms:
        return True
    
    return False
