"""thegent-mesh: Coordination mesh for multi-agent orchestration."""

__version__ = "0.1.0"

from .cache import MeshCache, Singleflight
from .coordination import (
    ConflictPrediction,
    EditIntent,
    FileClaimsRegistry,
    HLCTimestamp,
    IntentRegistry,
    OptimisticConcurrencyControl,
    predict_merge_conflicts,
)
from .smart_merge import (
    MergeResult,
    SmartMergeConfig,
    SmartMerger,
    configure_mergiraf_driver,
    is_mergiraf_available,
    make_smart_merger,
    merge_files,
)
from .task_queue import MaildirQueue

__all__ = [
    # Coordination
    "HLCTimestamp",
    "OptimisticConcurrencyControl",
    "FileClaimsRegistry",
    "EditIntent",
    "ConflictPrediction",
    "IntentRegistry",
    "predict_merge_conflicts",
    # Cache
    "MeshCache",
    "Singleflight",
    # Task Queue
    "MaildirQueue",
    # Smart Merge
    "SmartMergeConfig",
    "MergeResult",
    "SmartMerger",
    "is_mergiraf_available",
    "configure_mergiraf_driver",
    "merge_files",
    "make_smart_merger",
]
