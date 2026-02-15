"""Planning simulation overlays (G-CA-04).

PERT uncertainty, resource contention, continuity risk scoring.
"""

from thegent.planning.simulation import (
    PERTNode,
    PERTResult,
    ResourceProfile,
    TaskResourceDemand,
    ContentionResult,
    ContinuityRiskInput,
    ContinuityRiskResult,
    pert_forward_pass,
    simulate_resource_contention,
    score_continuity_risk,
)

__all__ = [
    "PERTNode",
    "PERTResult",
    "ResourceProfile",
    "TaskResourceDemand",
    "ContentionResult",
    "ContinuityRiskInput",
    "ContinuityRiskResult",
    "pert_forward_pass",
    "simulate_resource_contention",
    "score_continuity_risk",
]
