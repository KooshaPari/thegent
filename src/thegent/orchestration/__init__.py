"""Orchestration: phase transitions, lanes, evidence, recovery (WP-1004, WP-1005, WP-1002, WP-2001+)."""

from thegent.orchestration import (
    dag_prioritization,
    load_based_limits,
    resource_management,
    speculative_strategies,
    work_chunking,
)
from thegent.orchestration.dag_prioritization import (
    DagCycleError,
    DagPrioritizer,
    DagTask,
)
from thegent.orchestration.evidence import PromotionGate
from thegent.orchestration.hybrid_coordination import (
    CoordinationMetrics,
    CoordinationMode,
    HybridCoordinationStrategy,
)
from thegent.orchestration.lanes import Lane, LaneModel
from thegent.orchestration.load_based_limits import (
    DeadlineMonitor,
    LimitGateConfig,
    ResourceSnapshot,
    SoftDeadline,
    compute_dynamic_limit,
    get_deadline_monitor,
    sample_resources,
)
from thegent.orchestration.phases import (
    PHASE_TRANSITIONS,
    PhaseTransitionContract,
    validate_transition,
)
from thegent.orchestration.priority_queue import (
    QueuedRun,
    RunPriorityQueue,
    make_priority_queue,
)
from thegent.orchestration.redis_concurrency import (
    RedisConcurrencyController,
    RedisConfig,
    make_redis_concurrency_controller,
)
from thegent.orchestration.redlock_atomic import (
    RedlockAcquireResult,
    RedlockController,
    make_redlock_controller,
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
from thegent.orchestration.token_bucket import (
    RateLimitedSwarmRunner,
    TokenBucket,
    TokenBucketConfig,
)
from thegent.orchestration.work_chunking import (
    ChunkConfig,
    chunk_work_items,
    compute_optimal_chunk_size,
)

__all__ = [
    "PHASE_TRANSITIONS",
    "BottleneckDetector",
    "ChunkConfig",
    "CoordinationMetrics",
    "CoordinationMode",
    "DagCycleError",
    "DagPrioritizer",
    "DagTask",
    "DeadlineMonitor",
    "ExtendedResourceSnapshot",
    "HarnessCard",
    "HybridCoordinationStrategy",
    "Lane",
    "LaneModel",
    "LimitGateConfig",
    "PhaseTransitionContract",
    "PromotionGate",
    "QueuedRun",
    "RateLimitedSwarmRunner",
    "RedisConcurrencyController",
    "RedisConfig",
    "RedlockAcquireResult",
    "RedlockController",
    "ResourcePredictionEngine",
    "ResourceSnapshot",
    "RunPriorityQueue",
    "SoftDeadline",
    "SpeculativeConfig",
    "SpeculativeStrategy",
    "TokenBucket",
    "TokenBucketConfig",
    "chunk_work_items",
    "compute_adaptive_timeout",
    "compute_dynamic_limit",
    "compute_optimal_chunk_size",
    "create_harness_cards",
    "get_deadline_monitor",
    "make_priority_queue",
    "make_redis_concurrency_controller",
    "make_redlock_controller",
    "sample_extended_resources",
    "sample_resources",
    "select_speculative_providers",
    "should_terminate_early",
    "validate_transition",
]
