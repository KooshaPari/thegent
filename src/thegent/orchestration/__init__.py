"""Orchestration: phase transitions, lanes, evidence, recovery (WP-1004, WP-1005, WP-1002, WP-2001+)."""

from thegent.orchestration.evidence import PromotionGate
from thegent.orchestration.lanes import Lane, LaneModel
from thegent.orchestration import (
    load_based_limits,
    resource_management,
    speculative_strategies,
    work_chunking,
)

from thegent.orchestration.load_based_limits import (
    LimitGateConfig,
    ResourceSnapshot,
    compute_dynamic_limit,
    sample_resources,
)
from thegent.orchestration.resource_management import (
    BottleneckDetector,
    ExtendedResourceSnapshot,
    HarnessCard,
    ResourcePredictionEngine,
    create_harness_cards,
    sample_extended_resources,
)
from thegent.orchestration.speculative_strategies import (
    SpeculativeConfig,
    SpeculativeStrategy,
    compute_adaptive_timeout,
    select_speculative_providers,
    should_terminate_early,
)
from thegent.orchestration.work_chunking import (
    ChunkConfig,
    chunk_work_items,
    compute_optimal_chunk_size,
)
from thegent.orchestration.phases import (
    PHASE_TRANSITIONS,
    PhaseTransitionContract,
    validate_transition,
)

__all__ = [
    "PHASE_TRANSITIONS",
    "Lane",
    "LaneModel",
    "LimitGateConfig",
    "PhaseTransitionContract",
    "PromotionGate",
    "ResourceSnapshot",
    "compute_dynamic_limit",
    "sample_resources",
    "validate_transition",
    # Advanced resource management
    "ExtendedResourceSnapshot",
    "HarnessCard",
    "ResourcePredictionEngine",
    "BottleneckDetector",
    "sample_extended_resources",
    "create_harness_cards",
    # Speculative strategies
    "SpeculativeStrategy",
    "SpeculativeConfig",
    "compute_adaptive_timeout",
    "select_speculative_providers",
    "should_terminate_early",
    # Work chunking
    "ChunkConfig",
    "compute_optimal_chunk_size",
    "chunk_work_items",
]
