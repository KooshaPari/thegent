"""MAIF Artifact Generator - Creating and signing artifacts.

Implements the MAIFArtifactGenerator class for creating cryptographically signed
MAIF artifacts with hash chain tracking.
"""

import logging
import time
import uuid
from difflib import HtmlDiff

from thegent.integrations.confidential_report import ConfidentialReportFilter
from thegent.maif.crypto import SigningKey, hash_data
from thegent.maif.models import ActionType, MAIFArtifact

logger = logging.getLogger(__name__)


class MAIFArtifactGenerator:
    """Generator for creating signed MAIF artifacts with hash chain tracking.

    Attributes:
        signer: The RSA-2048 signing key
        last_hash: Dictionary mapping session_id to last artifact hash
    """

    def __init__(self, signer: SigningKey) -> None:
        """Initialize the artifact generator.

        Args:
            signer: SigningKey instance for signing artifacts.
        """
        self.signer = signer
        self.last_hash: dict[str, str] = {}  # session_id -> last_artifact_hash

    def create_artifact(
        self,
        action_type: ActionType,
        agent_id: str,
        session_id: str,
        input_data: bytes,
        output_data: bytes,
        metadata: dict | None = None,
    ) -> MAIFArtifact:
        """Create a signed MAIF artifact with hash chain.

        Args:
            action_type: Type of action (ActionType enum)
            agent_id: Identifier of the agent performing the action
            session_id: Session identifier for grouping artifacts
            input_data: Input bytes (e.g., file before edit)
            output_data: Output bytes (e.g., file after edit)
            metadata: Optional metadata dictionary

        Returns:
            MAIFArtifact instance with signature and hash chain.

        Raises:
            ValueError: If parameters are invalid.
        """
        if not agent_id or not session_id:
            raise ValueError("agent_id and session_id are required")

        # Get previous hash for this session
        prev_hash = self.last_hash.get(session_id, "")

        # Generate artifact ID (128-bit UUID as hex)
        artifact_id = uuid.uuid4().hex

        # Compute input/output hashes
        input_hash = hash_data(input_data)
        output_hash = hash_data(output_data)
        metadata_payload = ConfidentialReportFilter.redact_artifact_payload(metadata or {})

        # Create unsigned artifact
        artifact = MAIFArtifact(
            id=artifact_id,
            timestamp=int(time.time()),
            action_type=action_type,
            agent_id=agent_id,
            session_id=session_id,
            input_hash=input_hash,
            output_hash=output_hash,
            previous_hash=prev_hash,
            signature="",  # Will be filled after signing
            metadata=metadata_payload,
        )

        # Sign the artifact
        artifact_bytes = artifact.serialize_for_signing()
        signature_bytes = self.signer.sign(artifact_bytes)
        artifact.signature = signature_bytes.hex()

        # Update hash chain for this session
        artifact_hash = artifact.get_hash()
        self.last_hash[session_id] = artifact_hash

        logger.debug(f"Created artifact {artifact.id} for session {session_id}, hash: {artifact_hash[:16]}...")

        return artifact

    def get_last_hash(self, session_id: str) -> str:
        """Get the last artifact hash for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Hash of the last artifact in the session, or empty string if no artifacts.
        """
        return self.last_hash.get(session_id, "")

    def reset_session(self, session_id: str) -> None:
        """Reset hash chain for a session.

        Args:
            session_id: Session identifier.
        """
        if session_id in self.last_hash:
            del self.last_hash[session_id]
            logger.debug(f"Reset hash chain for session {session_id}")

    @staticmethod
    def build_html_diff_artifact(local_snapshot: dict, remote_snapshot: dict) -> str:
        """Create a deterministic side-by-side HTML diff artifact."""
        import json

        local_json = json.dumps(local_snapshot, indent=2, sort_keys=True).splitlines()
        remote_json = json.dumps(remote_snapshot, indent=2, sort_keys=True).splitlines()
        return HtmlDiff(tabsize=2, wrapcolumn=120).make_file(
            fromlines=local_json,
            tolines=remote_json,
            fromdesc="local",
            todesc="remote",
            context=False,
            numlines=0,
        )
