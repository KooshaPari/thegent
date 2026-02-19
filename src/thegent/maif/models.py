"""MAIF Action Artifacts - Data Models.

Defines the core data structures for MAIF (Multi-Agent Immutable Fabric) artifacts,
which capture and cryptographically sign agent actions for replay and auditing.
"""

import hashlib
import json
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionType(StrEnum):
    """Enumeration of action types that generate MAIF artifacts."""

    WRITE = "write"  # File write or edit
    EDIT = "edit"  # File edit
    DELETE = "delete"  # File deletion
    BASH = "bash"  # Bash command execution
    CODE_CHANGE = "code_change"  # Code modification
    DECISION = "decision"  # Agent decision point
    TOOL_USE = "tool_use"  # Tool invocation
    QUERY = "query"  # Information query
    OTHER = "other"  # Other action types


class MAIFArtifact(BaseModel):
    """Immutable artifact representing a single agent action.

    Each artifact is:
    - Deterministically serializable (JSON, sorted keys)
    - Cryptographically signed with RSA-2048
    - Part of a hash chain (previous_hash links to prior artifact)
    - Timestamped and attributed to an agent and session

    Attributes:
        id: Unique identifier for this artifact (hex-encoded UUID)
        timestamp: Unix timestamp (seconds since epoch)
        action_type: Type of action (ActionType enum)
        agent_id: Identifier of the agent that performed the action
        session_id: Session identifier for grouping related artifacts
        input_hash: SHA-256 hash of input data (e.g., file before edit)
        output_hash: SHA-256 hash of output data (e.g., file after edit)
        previous_hash: SHA-256 hash of previous artifact (empty string if first)
        signature: RSA-2048 signature of serialized artifact (hex-encoded)
        metadata: Optional dictionary of additional context
    """

    id: str = Field(..., description="Unique artifact identifier (hex UUID)")
    timestamp: int = Field(..., description="Unix timestamp")
    action_type: ActionType = Field(..., description="Type of action")
    agent_id: str = Field(..., description="Agent identifier")
    session_id: str = Field(..., description="Session identifier")
    input_hash: str = Field(..., description="SHA-256 hash of input data (e.g., file before edit)")
    output_hash: str = Field(..., description="SHA-256 hash of output data (e.g., file after edit)")
    previous_hash: str = Field(default="", description="SHA-256 hash of previous artifact (empty if first)")
    signature: str = Field(default="", description="RSA-2048 signature (hex-encoded)")
    metadata: dict = Field(default_factory=dict, description="Optional metadata (key-value pairs)")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        """Validate artifact ID is valid hex string."""
        try:
            int(v, 16)
            if len(v) != 32:
                raise ValueError("ID must be 32-character hex string (128 bits)")
        except ValueError as e:
            raise ValueError(f"Invalid artifact ID format: {e}")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp is positive integer."""
        if v <= 0:
            raise ValueError("Timestamp must be positive")
        return v

    @field_validator("input_hash", "output_hash", "previous_hash")
    @classmethod
    def validate_hash(cls, v):
        """Validate hash is valid SHA-256 hex string or empty."""
        if v == "":
            return v  # Empty string allowed for previous_hash
        try:
            int(v, 16)
            if len(v) != 64:
                raise ValueError("Hash must be 64-character hex string (SHA-256)")
        except ValueError as e:
            raise ValueError(f"Invalid hash format: {e}")
        return v

    @field_validator("signature")
    @classmethod
    def validate_signature(cls, v):
        """Validate signature is valid hex string or empty."""
        if v == "":
            return v  # Empty string allowed before signing
        try:
            int(v, 16)
            # RSA-2048 signature is 256 bytes = 512 hex chars
            if len(v) != 512:
                raise ValueError("Signature must be 512-character hex string (RSA-2048)")
        except ValueError as e:
            raise ValueError(f"Invalid signature format: {e}")
        return v

    def serialize_for_signing(self) -> bytes:
        """Return deterministic JSON serialization for signing.

        Excludes the signature field and uses sorted keys for consistency.

        Returns:
            JSON bytes with sorted keys, no whitespace.
        """
        artifact_dict = self.model_dump(exclude={"signature"})
        return json.dumps(artifact_dict, sort_keys=True, separators=(",", ":")).encode()

    def get_hash(self) -> str:
        """Compute SHA-256 hash of this artifact.

        Returns:
            Hex-encoded SHA-256 hash of serialized artifact.
        """
        return hashlib.sha256(self.serialize_for_signing()).hexdigest()

    def verify_hash_chain(self, previous_artifact: Optional["MAIFArtifact"]) -> bool:
        """Verify that this artifact's previous_hash matches the prior artifact.

        Args:
            previous_artifact: The prior artifact in the chain (None if first).

        Returns:
            True if hash chain is valid, False otherwise.
        """
        if previous_artifact is None:
            return self.previous_hash == ""
        return self.previous_hash == previous_artifact.get_hash()
