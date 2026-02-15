"""Planning simulation overlays (G-CA-04).

PERT uncertainty, resource contention, continuity risk scoring.
"""

from thegent.planning.simulation import (
    ContentionResult,
    ContinuityRiskInput,
    ContinuityRiskResult,
    PERTNode,
    PERTResult,
    ResourceProfile,
    TaskResourceDemand,
    pert_forward_pass,
    score_continuity_risk,
    simulate_resource_contention,
)

__all__ = [
    "ContentionResult",
    "ContinuityRiskInput",
    "ContinuityRiskResult",
    "PERTNode",
    "PERTResult",
    "ResourceProfile",
    "TaskResourceDemand",
    "pert_forward_pass",
    "score_continuity_risk",
    "simulate_resource_contention",
]
