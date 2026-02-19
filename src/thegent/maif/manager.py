"""MAIF Artifact Manager for thegent."""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .artifacts import MAIFArtifact, generate_key_pair, sign_artifact, verify_artifact
from .store import MAIFArtifactStore


class MAIFManager:
    """High-level manager for MAIF artifacts, handling keys and storage."""

    def __init__(self, db_path: Path, private_key_path: Optional[Path] = None):
        self.store = MAIFArtifactStore(db_path)
        self.private_key_path = private_key_path
        self._private_key: Optional[rsa.RSAPrivateKey] = None
        self._public_key: Optional[rsa.RSAPublicKey] = None

    def load_keys(self, password: Optional[bytes] = None) -> None:
        """Load RSA keys from disk."""
        if not self.private_key_path or not self.private_key_path.exists():
            # Auto-generate if not exists (for dev/test)
            self._private_key, self._public_key = generate_key_pair()
            return

        with open(self.private_key_path, "rb") as key_file:
            key_data = key_file.read()
            # serialization.load_pem_private_key returns RSAPrivateKey, DSAPrivateKey, etc.
            # We assume RSA for MAIF.
            pk = serialization.load_pem_private_key(
                key_data,
                password=password,
            )
            if not isinstance(pk, rsa.RSAPrivateKey):
                raise ValueError("Only RSA keys are supported for MAIF artifacts")
            self._private_key = pk
            self._public_key = self._private_key.public_key()

    def create_artifact(
        self,
        action_type: str,
        payload: Dict[str, Any],
        agent_id: str,
        session_id: str,
        chain_of_thought: Optional[str] = None,
        previous_artifact_id: Optional[str] = None,
    ) -> MAIFArtifact:
        """Create, sign, and store a new MAIF artifact."""
        if self._private_key is None:
            self.load_keys()

        if self._private_key is None:
            raise RuntimeError("Failed to load or generate private key")

        artifact = MAIFArtifact(
            action_type=action_type,
            payload=payload,
            agent_id=agent_id,
            session_id=session_id,
            chain_of_thought=chain_of_thought,
            previous_artifact_id=previous_artifact_id,
        )

        # Sign
        sign_artifact(artifact, self._private_key)

        # Store
        self.store.store(artifact)

        return artifact

    def verify(self, artifact_id: str) -> bool:
        """Retrieve and verify an artifact by ID."""
        artifact = self.store.get(artifact_id)
        if not artifact:
            return False

        if self._public_key is None:
            self.load_keys()

        if self._public_key is None:
            raise RuntimeError("Failed to load or generate public key")

        return verify_artifact(artifact, self._public_key)

    def get_session_history(self, session_id: str) -> List[MAIFArtifact]:
        """Get all artifacts for a session."""
        return self.store.list_by_session(session_id)
