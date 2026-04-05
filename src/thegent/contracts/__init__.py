"""Contracts module for thegent - SLA, SLO, and compliance contracts.

Provides data models and validation for:
- Service Level Agreements (SLA)
- Service Level Objectives (SLO)
- Compliance contracts and attestations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class ContractStatus(Enum):
    """Status of a contract or agreement."""

    DRAFT = auto()
    ACTIVE = auto()
    EXPIRED = auto()
    VIOLATED = auto()
    TERMINATED = auto()


class ContractType(Enum):
    """Types of contracts supported."""

    SLA = "sla"  # Service Level Agreement
    SLO = "slo"  # Service Level Objective
    COMPLIANCE = "compliance"  # Compliance contract
    DATA_PROCESSING = "data_processing"  # GDPR/data processing


@dataclass
class SLOTarget:
    """A single SLO target metric."""

    metric: str
    threshold: float
    operator: str = "<="  # <=, >=, ==, <, >
    window: str = "1h"  # time window: 1h, 24h, 7d, 30d
    description: str = ""

    def evaluate(self, value: float) -> bool:
        """Evaluate if value meets the SLO target."""
        if self.operator == "<=":
            return value <= self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">":
            return value > self.threshold
        return False


@dataclass
class SLODefinition:
    """Definition of Service Level Objectives."""

    name: str
    description: str = ""
    targets: list[SLOTarget] = field(default_factory=list)
    burn_rate_alerts: list[float] = field(default_factory=lambda: [2.0, 4.0, 8.0])
    alert_channels: list[str] = field(default_factory=list)

    def add_target(self, target: SLOTarget) -> None:
        """Add an SLO target."""
        self.targets.append(target)


@dataclass
class SLAAgreement:
    """Service Level Agreement definition."""

    id: str
    name: str
    provider: str = ""  # Who provides the service
    consumer: str = ""  # Who consumes the service
    description: str = ""
    slos: list[SLODefinition] = field(default_factory=list)
    penalties: dict[str, Any] = field(default_factory=dict)
    credits: dict[str, Any] = field(default_factory=dict)
    status: ContractStatus = ContractStatus.DRAFT
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def add_slo(self, slo: SLODefinition) -> None:
        """Add an SLO to this SLA."""
        self.slos.append(slo)

    def is_active(self) -> bool:
        """Check if SLA is currently active."""
        if self.status != ContractStatus.ACTIVE:
            return False
        now = datetime.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True


@dataclass
class ComplianceRequirement:
    """A single compliance requirement."""

    id: str
    framework: str  # e.g., "GDPR", "HIPAA", "SOC2"
    control: str  # Control identifier
    description: str
    severity: str = "medium"  # critical, high, medium, low
    evidence_required: list[str] = field(default_factory=list)


@dataclass
class ComplianceContract:
    """Compliance contract for regulatory requirements."""

    id: str
    name: str
    framework: str
    version: str
    description: str = ""
    requirements: list[ComplianceRequirement] = field(default_factory=list)
    status: ContractStatus = ContractStatus.DRAFT
    attestations: list[Attestation] = field(default_factory=list)

    def add_requirement(self, req: ComplianceRequirement) -> None:
        """Add a compliance requirement."""
        self.requirements.append(req)


@dataclass
class Attestation:
    """An attestation of compliance."""

    id: str
    contract_id: str
    timestamp: datetime
    attester: str
    scope: str
    evidence: dict[str, Any] = field(default_factory=dict)
    signature: str = ""


@dataclass
class ContractRegistry:
    """Registry for managing contracts."""

    contracts: dict[str, SLAAgreement | ComplianceContract] = field(
        default_factory=dict
    )

    def register(self, contract: SLAAgreement | ComplianceContract) -> None:
        """Register a contract."""
        self.contracts[contract.id] = contract

    def get(self, contract_id: str) -> SLAAgreement | ComplianceContract | None:
        """Get a contract by ID."""
        return self.contracts.get(contract_id)

    def list_by_type(self, contract_type: ContractType) -> list:
        """List contracts by type."""
        if contract_type == ContractType.SLA:
            return [c for c in self.contracts.values() if isinstance(c, SLAAgreement)]
        elif contract_type == ContractType.COMPLIANCE:
            return [
                c for c in self.contracts.values() if isinstance(c, ComplianceContract)
            ]
        return []

    def active_slas(self) -> list[SLAAgreement]:
        """Get all active SLAs."""
        return [
            c for c in self.contracts.values()
            if isinstance(c, SLAAgreement) and c.is_active()
        ]


__all__ = [
    # Enums
    "ContractStatus",
    "ContractType",
    # SLO
    "SLOTarget",
    "SLODefinition",
    # SLA
    "SLAAgreement",
    # Compliance
    "ComplianceRequirement",
    "ComplianceContract",
    "Attestation",
    # Registry
    "ContractRegistry",
]
