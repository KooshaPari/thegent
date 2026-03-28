"""heliosShield: High-performance agent mesh orchestration package."""

from phenotype_thegent_agents.mesh.audit import AuditManager
from phenotype_thegent_agents.mesh.cache import MeshCache, Singleflight
from phenotype_thegent_agents.mesh.consensus import CausalInfluenceTracker, ConsensusProtocol, EscalationWorkflow
from phenotype_thegent_agents.mesh.coordination import FileClaimsRegistry, HLCTimestamp, OptimisticConcurrencyControl
from phenotype_thegent_agents.mesh.git import GitParallelismManager
from phenotype_thegent_agents.mesh.git_parallelism import WorktreeContext, WorktreePool
from phenotype_thegent_agents.mesh.injection import ContextInjection, ShellInjection
from phenotype_thegent_agents.mesh.isolation import ResourceIsolation
from phenotype_thegent_agents.mesh.merge import SmartMerge
from phenotype_thegent_agents.mesh.mesh import MeshIPC, MeshManager
from phenotype_thegent_agents.mesh.observability import MeshLogger, MetricsAggregator
from phenotype_thegent_agents.mesh.resources import ResourceManager
from phenotype_thegent_agents.mesh.sandbox import AutonomyTier, Sandboxing
from phenotype_thegent_agents.mesh.smart_merge import (
    MergeResult,
    SmartMergeConfig,
    SmartMerger,
    configure_mergiraf_driver,
    is_mergiraf_available,
    make_smart_merger,
    merge_files,
)
from phenotype_thegent_agents.mesh.task_queue import MaildirQueue
from phenotype_thegent_agents.mesh.worktree import BranchCollisionError, WorktreeManager

__all__ = [
    "AuditManager",
    "AutonomyTier",
    "BranchCollisionError",
    "CausalInfluenceTracker",
    "ConsensusProtocol",
    "ContextInjection",
    "EscalationWorkflow",
    "FileClaimsRegistry",
    "GitParallelismManager",
    "HLCTimestamp",
    "MaildirQueue",
    "MaildirQueue",
    "MergeResult",
    "MeshCache",
    "MeshIPC",
    "MeshLogger",
    "MeshManager",
    "MetricsAggregator",
    "OptimisticConcurrencyControl",
    "ResourceIsolation",
    "ResourceManager",
    "Sandboxing",
    "ShellInjection",
    "Singleflight",
    "SmartMerge",
    "SmartMergeConfig",
    "SmartMerger",
    "WorktreeContext",
    "WorktreeManager",
    "WorktreePool",
    "configure_mergiraf_driver",
    "is_mergiraf_available",
    "make_smart_merger",
    "merge_files",
]
