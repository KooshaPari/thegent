"""Stub module."""
from dataclasses import dataclass


@dataclass
class PromotionGate:
    """Gate for evidence-based promotion decisions."""
    threshold: float = 0.8
    min_evidence: int = 3

    def should_promote(self, evidence_score: float) -> bool:
        """Determine if evidence score warrants promotion."""
        return evidence_score >= self.threshold


__all__ = ["PromotionGate"]
