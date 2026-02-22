"""Orchestration: phase transitions, lanes, evidence, recovery (WP-1004, WP-1005, WP-1002, WP-2001+)."""

from thegent.orchestration.budget_tracker import BudgetExceededError, BudgetTracker
from thegent.coordination.hybrid_coordination import (
    CoordinationMetrics,
    CoordinationMode,
    HybridCoordinationStrategy,
)
from thegent.orchestration.consensus.redis_concurrency import (
    RedisConcurrencyController,
    RedisConfig,
    make_redis_concurrency_controller,
)
from thegent.orchestration.consensus.redlock_atomic import (
    RedlockAcquireResult,
    RedlockController,
    make_redlock_controller,
)
from thegent.orchestration.execution.dag_prioritization import (
    DagCycleError,
    DagPrioritizer,
    DagTask,
)
from thegent.orchestration.execution.lanes import Lane, LaneModel
from thegent.orchestration.execution.phases import (
    PHASE_TRANSITIONS,
    PhaseTransitionContract,
    validate_transition,
)
from thegent.orchestration.execution.priority_queue import (
    QueuedRun,
    RunPriorityQueue,
    make_priority_queue,
)
from thegent.orchestration.execution.work_chunking import (
    ChunkConfig,
    chunk_work_items,
    compute_optimal_chunk_size,
)
from thegent.orchestration.resource.load_based_limits import (
    DeadlineMonitor,
    LimitGateConfig,
    ResourceSnapshot,
    SoftDeadline,
    compute_dynamic_limit,
    get_deadline_monitor,
    sample_resources,
)
from thegent.orchestration.resource.resource_management import (
    BottleneckDetector,
    ExtendedResourceSnapshot,
    HarnessCard,
    ResourcePredictionEngine,
    create_harness_cards,
    sample_extended_resources,
)
from thegent.orchestration.resource.token_bucket import (
    RateLimitedSwarmRunner,
    TokenBucket,
    TokenBucketConfig,
)
from thegent.orchestration.strategies.evidence import PromotionGate
from thegent.orchestration.strategies.speculative_strategies import (
    SpeculativeConfig,
    SpeculativeStrategy,
    compute_adaptive_timeout,
    select_speculative_providers,
    should_terminate_early,
)

__all__ = [
    "PHASE_TRANSITIONS",
    "BottleneckDetector",
    "BudgetExceededError",
    "BudgetTracker",
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
