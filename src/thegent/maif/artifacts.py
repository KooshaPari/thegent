"""MAIF Action Artifacts implementation for thegent."""

import base64
import hashlib
import json
import uuid
from datetime import UTC, datetime, timezone
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pydantic import BaseModel, Field


class MAIFArtifact(BaseModel):
    """
    MAIF (Model-Aware Information Flow) action artifact.
    Provides signed, immutable record of an agent action.
    """

    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # mcp_call | tool_use | message | decision
    payload: dict[str, Any]
    signature: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent_id: str
    session_id: str
    chain_of_thought: str | None = None
    verification_key_id: str | None = None
    previous_artifact_id: str | None = None

    def get_canonical_data(self) -> str:
        """Return canonical JSON representation for signing."""
        return json.dumps(
            {
                "payload": self.payload,
                "timestamp": self.timestamp,
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "action_type": self.action_type,
            },
            sort_keys=True,
        )


def sign_artifact(artifact: MAIFArtifact, private_key: rsa.RSAPrivateKey) -> str:
    """Sign artifact with RSA private key."""
    canonical = artifact.get_canonical_data()
    message_hash = hashlib.sha256(canonical.encode()).digest()

    signature = private_key.sign(
        message_hash,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    sig_b64 = base64.b64encode(signature).decode()
    artifact.signature = sig_b64
    return sig_b64


def verify_artifact(artifact: MAIFArtifact, public_key: rsa.RSAPublicKey) -> bool:
    """Verify artifact signature."""
    if not artifact.signature:
        return False

    try:
        signature = base64.b64decode(artifact.signature)
        canonical = artifact.get_canonical_data()
        message_hash = hashlib.sha256(canonical.encode()).digest()

        public_key.verify(
            signature,
            message_hash,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def generate_key_pair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate a new RSA key pair for MAIF signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    return private_key, private_key.public_key()
