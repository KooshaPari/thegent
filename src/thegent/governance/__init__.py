"""Governance modules: cost, policy, sandbox, economic routing (G-GP, WP-5003)."""

from thegent.cost.aggregator import CostAggregator, CostEstimator
from thegent.governance.input_guardrails import GuardrailResult, InputGuardrails

# Phase 2.1: Provider Scoring System (WP-5003)
from thegent.governance.metrics import (
    AggregatedMetrics,
    MetricsCollector,
    ProviderMetricsSnapshot,
    get_metrics_collector,
    initialize_metrics_collector,
)
from thegent.governance.providers import (
    ProviderConfig,
    ProviderRegistry,
    ProviderType,
)
from thegent.governance.scoring import (
    DefaultProviderScorer,
    ProviderMetrics,
    ProviderScore,
    ProviderScorer,
)

__all__ = [
    # Phase 2.1: Provider Scoring System (WP-5003)
    "AggregatedMetrics",
    # Cost governance
    "CostAggregator",
    "CostEstimator",
    "DefaultProviderScorer",
    # Input guardrails
    "GuardrailResult",
    "InputGuardrails",
    "MetricsCollector",
    "ProviderConfig",
    "ProviderMetrics",
    "ProviderMetricsSnapshot",
    "ProviderRegistry",
    "ProviderScore",
    "ProviderScorer",
    "ProviderType",
    "get_metrics_collector",
    "initialize_metrics_collector",
]

from thegent.governance.compliance_reports import ComplianceReporter
from thegent.governance.federated_policy import FederatedPolicyEngine, PolicyRule, PolicyScope
from thegent.governance.override_events import (
    OverrideActivatedEvent,
    OverrideEventEmitter,
    OverrideExpiredEvent,
    OverrideExpiryMonitor,
)

__all__.append("ComplianceReporter")
__all__ += ["FederatedPolicyEngine", "PolicyRule", "PolicyScope"]
__all__ += [
    # Override expiry event emission (research-governance-override-events)
    "OverrideActivatedEvent",
    "OverrideEventEmitter",
    "OverrideExpiredEvent",
    "OverrideExpiryMonitor",
]

from thegent.governance.vetter import (
    RuffVetterCheck,
    TestPassVetterCheck,
    VetterCheck,
    VetterCheckResult,
    VetterOutcome,
    VetterPolicy,
    VetterResult,
    VetterSeverity,
)

__all__ += [
    # Vetter core types (FR-VET-090) and WL-097 code checks
    "RuffVetterCheck",
    "TestPassVetterCheck",
    "VetterCheck",
    "VetterCheckResult",
    "VetterOutcome",
    "VetterPolicy",
    "VetterResult",
    "VetterSeverity",
]
