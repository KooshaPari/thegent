"""Evidence capture at every promotion gate (WP-1005, FR-004).

Captures CSM state as evidence before promotion, with hash verification
and completeness audit trail.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from thegent.contracts.policy import FallbackPolicy


class PromotionGate:
    """WP-1005: Evidence capture and validation before state promotion."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = Path(session_dir)
        self.evidence_dir = self.session_dir / "evidence"
        self.audit_path = self.session_dir / "evidence_audit.jsonl"

    def capture_evidence(self, run_id: str, csm: Any) -> str:
        """Capture CSM state as evidence; return SHA-256 hash. Appends to audit trail."""
        evidence_data = json.dumps(csm.to_dict(), sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_data.encode()).hexdigest()

        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        phase_val = getattr(csm.phase, "value", str(csm.phase))
        evidence_path = self.evidence_dir / f"{run_id}_{phase_val}.json"
        evidence_path.write_text(evidence_data, encoding="utf-8")

        # Completeness audit trail (FR-004)
        audit_entry = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": run_id,
            "phase": phase_val,
            "evidence_hash": evidence_hash,
            "evidence_path": str(evidence_path),
        }
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry) + "\n")

        return evidence_hash

    def validate_promotion(self, csm: Any, policy: FallbackPolicy) -> list[str]:
        """Validate if CSM is ready for promotion based on policy."""
        issues: list[str] = []
        if csm.confidence_level < policy.min_confidence_threshold:
            issues.append(f"Confidence {csm.confidence_level} below threshold {policy.min_confidence_threshold}")
        if csm.blockers:
            issues.append(f"Active blockers present: {csm.blockers}")
        return issues

    def verify_evidence_hash(self, run_id: str, phase: str, expected_hash: str) -> bool:
        """Verify stored evidence hash matches expected. Returns True if valid."""
        evidence_path = self.evidence_dir / f"{run_id}_{phase}.json"
        if not evidence_path.exists():
            return False
        evidence_data = evidence_path.read_text(encoding="utf-8")
        computed = hashlib.sha256(evidence_data.encode()).hexdigest()
        return computed == expected_hash
