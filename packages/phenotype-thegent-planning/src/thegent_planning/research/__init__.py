"""Research implementations."""

from thegent_planning.research.agent_hierarchy import AgentHierarchyManager
from thegent_planning.research.always_dumps import ConversationDumpWriter
from thegent_planning.research.cost_sensitivity import CostSensitivityFramework
from thegent_planning.research.governance_dlq import EscalationQueueDLQ
from thegent_planning.research.library_replacements import (
    check_tomlkit_available,
    replace_md5_with_sha256,
    use_diskcache,
    use_psutil_monitoring,
)
from thegent_planning.research.remote_compute import RemoteComputeClient

__all__ = [
    "AgentHierarchyManager",
    "ConversationDumpWriter",
    "CostSensitivityFramework",
    "EscalationQueueDLQ",
    "RemoteComputeClient",
    "check_tomlkit_available",
    "replace_md5_with_sha256",
    "use_diskcache",
    "use_psutil_monitoring",
]

from thegent_planning.research.cost_routing import CostRoutingResearch

__all__.append("CostRoutingResearch")

from thegent_planning.research.economic_governance import EconomicGovernance
from thegent_planning.research.idea_seed_system import IdeaSeedSystem
from thegent_planning.research.maif_artifacts import MAIFArtifact
from thegent_planning.research.pareto_routing import ParetoRouting
from thegent_planning.research.supermemory_integration import SupermemoryIntegration

__all__.extend(
    [
        "EconomicGovernance",
        "IdeaSeedSystem",
        "MAIFArtifact",
        "ParetoRouting",
        "SupermemoryIntegration",
    ]
)
