"""MAIF Hash Chain Validator - Verifying artifact integrity.

Implements the HashChainValidator class for verifying artifact chains and
detecting tampering.
"""

import logging

from thegent.maif.crypto import VerifyingKey
from thegent.maif.models import MAIFArtifact

logger = logging.getLogger(__name__)


class HashChainValidator:
    """Validator for MAIF artifact chains.

    Verifies the integrity of artifact chains by checking:
    - Hash chain continuity (each artifact's previous_hash matches prior artifact's hash)
    - Signature validity (each artifact is properly signed)
    - Chain heads (latest artifact hash per session)

    Attributes:
        verifying_key: The RSA-2048 public key for signature verification
        chain_heads: Dictionary mapping session_id to latest artifact hash
    """

    def __init__(self, verifying_key: VerifyingKey) -> None:
        """Initialize the hash chain validator.

        Args:
            verifying_key: VerifyingKey instance for signature verification.
        """
        self.verifying_key = verifying_key
        self.chain_heads: dict[str, str] = {}  # session_id -> latest_artifact_hash

    def verify_chain(
        self,
        artifacts: list[MAIFArtifact],
    ) -> tuple[bool, str]:
        """Verify integrity of an artifact chain.

        Checks that:
        1. Hash chain is continuous (each artifact's previous_hash matches prior)
        2. All signatures are valid
        3. Chain is internally consistent

        Args:
            artifacts: List of MAIFArtifacts to verify (should be sorted by timestamp).

        Returns:
            Tuple of (is_valid, message) where is_valid is True if chain is valid.
        """
        if not artifacts:
            return True, "Empty chain is valid"

        session_id = artifacts[0].session_id

        # Verify all artifacts are from the same session
        for artifact in artifacts:
            if artifact.session_id != session_id:
                return False, "Artifacts from different sessions"

        # Verify each artifact
        for i, artifact in enumerate(artifacts):
            # Check hash chain continuity
            expected_prev = "" if i == 0 else artifacts[i - 1].get_hash()

            if artifact.previous_hash != expected_prev:
                return (
                    False,
                    f"Artifact {i}: hash chain broken "
                    f"(expected {expected_prev[:16]}..., got {artifact.previous_hash[:16]}...)",
                )

            # Verify signature
            if not self._verify_signature(artifact):
                return False, f"Artifact {i}: signature invalid"

        # Update chain head
        self.chain_heads[session_id] = artifacts[-1].get_hash()
        logger.debug(
            f"Verified chain for session {session_id}: {len(artifacts)} artifacts, "
            f"head: {self.chain_heads[session_id][:16]}..."
        )

        return True, "OK"

    def verify_artifact(self, artifact: MAIFArtifact) -> bool:
        """Verify a single artifact's signature.

        Args:
            artifact: MAIFArtifact to verify.

        Returns:
            True if signature is valid, False otherwise.
        """
        return self._verify_signature(artifact)

    def _verify_signature(self, artifact: MAIFArtifact) -> bool:
        """Verify artifact signature using public key.

        Args:
            artifact: MAIFArtifact with signature to verify.

        Returns:
            True if signature is valid, False otherwise.
        """
        if not artifact.signature:
            logger.warning(f"Artifact {artifact.id} has no signature")
            return False

        try:
            artifact_bytes = artifact.serialize_for_signing()
            signature_bytes = bytes.fromhex(artifact.signature)
            return self.verifying_key.verify(artifact_bytes, signature_bytes)
        except Exception as e:
            logger.warning(f"Signature verification failed for {artifact.id}: {e}")
            return False

    def verify_chain_from_head(
        self,
        session_id: str,
        artifacts: list[MAIFArtifact],
    ) -> tuple[bool, str]:
        """Verify chain starting from known chain head.

        Verifies that the provided artifacts extend or match the known chain head
        for the session.

        Args:
            session_id: Session identifier.
            artifacts: List of artifacts to verify.

        Returns:
            Tuple of (is_valid, message).
        """
        if not artifacts:
            return True, "Empty chain is valid"

        # Check if first artifact links to known head
        if session_id in self.chain_heads:
            expected_prev = self.chain_heads[session_id]
            if artifacts[0].previous_hash != expected_prev:
                return (
                    False,
                    f"First artifact doesn't link to known head "
                    f"(expected {expected_prev[:16]}..., got {artifacts[0].previous_hash[:16]}...)",
                )

        return self.verify_chain(artifacts)

    def get_chain_head(self, session_id: str) -> str | None:
        """Get the latest artifact hash for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Hash of the latest artifact in the session, or None if not known.
        """
        return self.chain_heads.get(session_id)

    def has_chain_head(self, session_id: str) -> bool:
        """Check if chain head is known for a session.

        Args:
            session_id: Session identifier.

        Returns:
            True if chain head is known, False otherwise.
        """
        return session_id in self.chain_heads

    def reset_session(self, session_id: str) -> None:
        """Reset chain head for a session.

        Args:
            session_id: Session identifier.
        """
        if session_id in self.chain_heads:
            del self.chain_heads[session_id]
            logger.debug(f"Reset chain head for session {session_id}")
