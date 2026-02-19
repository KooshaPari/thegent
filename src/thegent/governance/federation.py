"""WP-13001: Multi-org policy federation."""

import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class PolicyNamespace:
    """Namespace identifier for org/project/env."""

    def __init__(
        self,
        org: str,
        project: str = "default",
        environment: str = "production",
    ) -> None:
        self.org = org
        self.project = project
        self.env = environment

    def get_hierarchy(self) -> list[str]:
        """Return resolution order: specific -> org default -> root default."""
        return [
            f"{self.org}.{self.project}.{self.env}",
            f"{self.org}.{self.project}.default",
            f"{self.org}.default.default",
        ]

    def __repr__(self) -> str:
        return f"{self.org}.{self.project}.{self.env}"


class FederatedPolicyManager:
    """Manages federated policy resolution and health."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)

    def get_federation_health(self) -> dict[str, Any]:
        """Return federation health status."""
        namespaces: list[str] = []
        if self.base_dir.exists():
            for org_p in self.base_dir.iterdir():
                if org_p.is_dir():
                    for proj_p in org_p.iterdir():
                        if proj_p.is_dir():
                            for env_p in proj_p.iterdir():
                                if env_p.is_dir():
                                    namespaces.append(f"{org_p.name}.{proj_p.name}.{env_p.name}")
        status = "healthy" if namespaces else "empty"
        return {
            "status": status,
            "namespace_count": len(namespaces),
            "namespaces": namespaces,
        }

    def resolve_policy(self, ns: "PolicyNamespace", policy_id: str) -> dict[str, Any]:
        """Resolve policy by traversing namespace hierarchy."""
        for ns_str in ns.get_hierarchy():
            parts = ns_str.split(".")
            if len(parts) >= 3:
                path = self.base_dir / parts[0] / parts[1] / parts[2] / f"{policy_id}.json"
                if path.exists():
                    return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def apply_jurisdiction_constraints(self, policy: dict[str, Any], region: str) -> dict[str, Any]:
        """Apply jurisdiction overlay (EU-AI-ACT, US-SEC)."""
        out = dict(policy)
        if region == "EU":
            out["jurisdiction_profile"] = "EU-AI-ACT"
            out["human_in_loop_required"] = True
            out["risk_threshold"] = min(out.get("risk_threshold", 1.0), 0.7)
        elif region == "US":
            out["jurisdiction_profile"] = "US-SEC"
            out["audit_retention_days"] = 2555
        return out

    def relay_consent(
        self, ns1: "PolicyNamespace", ns2: "PolicyNamespace", run_id: str, approver: str
    ) -> dict[str, Any]:
        """WP-13003: Relay approval consent between namespaces with provenance signatures."""
        import hashlib
        import time

        payload = f"{ns1}:{ns2}:{run_id}:{approver}:{time.time()}"
        signature = hashlib.sha256(payload.encode()).hexdigest()

        relay_artifact = {
            "type": "consent_relay",
            "version": "1.0",
            "run_id": run_id,
            "source_namespace": str(ns1),
            "target_namespace": str(ns2),
            "approver": approver,
            "timestamp": time.time(),
            "provenance_signature": signature,
            "status": "active",
        }

        # In a real impl, we would persist this to a shared ledger
        _log.info("Relayed consent from %s to %s for run %s", ns1, ns2, run_id)
        return relay_artifact

    def arbitrate_conflict(self, policies: list[dict[str, Any]]) -> dict[str, Any]:
        """Arbitrate conflicts using 'most restrictive wins'."""
        if not policies:
            return {}
        out: dict[str, Any] = {}
        for p in policies:
            for k, v in p.items():
                if k not in out:
                    out[k] = v
                elif k == "risk_threshold":
                    out[k] = min(out[k], v)
                elif k == "human_in_loop_required":
                    out[k] = out[k] or v
                else:
                    out[k] = v
        out["arbitration_applied"] = True
        return out


class FederationManager:
    """Manages policy federation across multiple organizations."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.peers_path = session_dir / "federation_peers.json"

    def sync_policies(self, peer_id: str):
        """Sync governance policies from a peer organization."""
        _log.info("Syncing policies from federation peer %s", peer_id)
        # In a real impl, this would perform a secure handshake and download signed policies

    def get_effective_policy(self, policy_id: str) -> dict[str, Any]:
        """Resolve a policy, considering federated overrides."""
        # Simple local-first resolution
        local_path = self.session_dir / "contracts" / f"{policy_id}.json"
        if local_path.exists():
            return json.loads(local_path.read_text(encoding="utf-8"))
        return {}
