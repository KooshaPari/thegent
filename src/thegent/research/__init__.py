"""Research implementations."""

from thegent.research.agent_hierarchy import AgentHierarchyManager
from thegent.research.always_dumps import ConversationDumpWriter
from thegent.research.cost_sensitivity import CostSensitivityFramework
from thegent.research.governance_dlq import EscalationQueueDLQ
from thegent.research.library_replacements import (
    check_tomlkit_available,
    replace_md5_with_sha256,
    use_diskcache,
    use_psutil_monitoring,
)
from thegent.research.remote_compute import RemoteComputeClient

__all__ = [
    "AgentHierarchyManager",
    "AutonomousLearningSurface",
    "ConversationDumpWriter",
    "CostSensitivityFramework",
    "EscalationQueueDLQ",
    "RemoteComputeClient",
    "check_tomlkit_available",
    "replace_md5_with_sha256",
    "use_diskcache",
    "use_psutil_monitoring",
]

from thegent.research.cost_routing import CostRoutingResearch

__all__.append("CostRoutingResearch")

from thegent.research.economic_governance import EconomicGovernance
from thegent.research.idea_seed_system import IdeaSeedSystem
from thegent.research.maif_artifacts import MAIFArtifact
from thegent.research.pareto_routing import ParetoRouting
from thegent.research.supermemory_integration import SupermemoryIntegration

__all__.extend(
    [
        "EconomicGovernance",
        "IdeaSeedSystem",
        "MAIFArtifact",
        "ParetoRouting",
        "SupermemoryIntegration",
    ]
)
