"""MAIF (Model-Aware Information Flow) action artifacts.

Provides signed, immutable records of agent actions (WP-3002).
"""

from __future__ import annotations

import base64
import hashlib
import orjson as json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

if TYPE_CHECKING:
    from pathlib import Path

_log = logging.getLogger(__name__)
MAIF_ARTIFACT_SCHEMA_VERSION = "wl277.maif.v1"
SUPPORTED_MAIF_ARTIFACT_SCHEMA_VERSIONS = {MAIF_ARTIFACT_SCHEMA_VERSION}


# ---------------------------------------------------------------------------
# High-level MAIFArtifact dataclass (for test_maif.py API)
# ---------------------------------------------------------------------------


@dataclass
class MAIFArtifact:
    """Mutable artifact record used by MAIFManager and tests.

    Attributes:
        action_type: Type of agent action recorded.
        payload: Action payload dict.
        agent_id: Agent that performed the action.
        session_id: Session in which the action occurred.
        artifact_id: Unique identifier (auto-generated if not supplied).
        signature: Base64-encoded RSA signature; None until signed.
        timestamp: ISO-8601 timestamp.
        chain_of_thought: Optional chain-of-thought text.
        verification_key_id: Optional key identifier.
        previous_artifact_id: ID of the prior artifact in the chain.
    """

    action_type: str
    payload: dict[str, Any]
    agent_id: str
    session_id: str
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signature: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    chain_of_thought: str | None = None
    verification_key_id: str | None = None
    previous_artifact_id: str | None = None


def require_supported_schema_version(payload: dict[str, Any]) -> str:
    """Validate required schema_version field for MAIF artifacts."""
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version:
        raise ValueError("MAIF artifact payload missing required schema_version")
    if schema_version not in SUPPORTED_MAIF_ARTIFACT_SCHEMA_VERSIONS:
        raise ValueError(f"Unsupported MAIF artifact schema_version: {schema_version}")
    return schema_version


def generate_key_pair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate an RSA key pair for signing MAIF artifacts.

    Returns:
        Tuple of (private_key, public_key).
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def sign_artifact(artifact: MAIFArtifact, private_key: rsa.RSAPrivateKey) -> str:
    """Sign a MAIFArtifact in-place and return the base64-encoded signature.

    Sets artifact.signature to the computed signature string.

    Args:
        artifact: The artifact to sign (mutated in-place).
        private_key: RSA private key used for signing.

    Returns:
        Base64-encoded signature string.
    """
    canonical = json.dumps(
        {"payload": artifact.payload, "timestamp": artifact.timestamp, "agent_id": artifact.agent_id},
        sort_keys=True,
    )
    message_hash = hashlib.sha256(canonical.encode()).digest()
    raw_signature = private_key.sign(message_hash, padding.PKCS1v15(), hashes.SHA256())
    sig_str = base64.b64encode(raw_signature).decode()
    artifact.signature = sig_str
    return sig_str


def verify_artifact(artifact: MAIFArtifact, public_key: rsa.RSAPublicKey) -> bool:
    """Verify a MAIFArtifact's signature.

    Args:
        artifact: Artifact to verify.
        public_key: RSA public key corresponding to the signing private key.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if artifact.signature is None:
        return False
    try:
        raw_signature = base64.b64decode(artifact.signature)
        canonical = json.dumps(
            {"payload": artifact.payload, "timestamp": artifact.timestamp, "agent_id": artifact.agent_id},
            sort_keys=True,
        )
        message_hash = hashlib.sha256(canonical.encode()).digest()
        public_key.verify(raw_signature, message_hash, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception as exc:
        _log.debug("MAIF artifact verification failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Key Management
# ---------------------------------------------------------------------------


def generate_signing_key() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """Generate RSA key pair for signing (MAIF)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()
    return private_key, public_key


def load_private_key(path: Path, password: bytes | None = None) -> rsa.RSAPrivateKey:
    """Load private key from PEM file."""
    with open(path, "rb") as key_file:
        pk = serialization.load_pem_private_key(key_file.read(), password=password)
    if not isinstance(pk, rsa.RSAPrivateKey):
        raise ValueError("Only RSA keys are supported for MAIF artifacts")
    return pk


def save_private_key(private_key: rsa.RSAPrivateKey, path: Path, password: bytes | None = None) -> None:
    """Save private key to PEM file."""
    encryption = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=encryption
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(pem)


# ---------------------------------------------------------------------------
# Signing & Verification
# ---------------------------------------------------------------------------


def _sign_artifact_dict(payload: dict[str, Any], timestamp: str, agent_id: str, private_key: rsa.RSAPrivateKey) -> str:
    """Sign raw artifact dict fields with RSA private key (MAIF internal)."""
    # Create canonical payload
    canonical = json.dumps({"payload": payload, "timestamp": timestamp, "agent_id": agent_id}, sort_keys=True).decode()

    # Calculate SHA-256 hash
    message_hash = hashlib.sha256(canonical.encode()).digest()

    # Sign with PKCS#1 v1.5 padding
    signature = private_key.sign(message_hash, padding.PKCS1v15(), hashes.SHA256())

    return base64.b64encode(signature).decode()


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class MAIFArtifactStore:
    """SQLite-backed storage for MAIF artifacts (FR-MAIF-001)."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database for artifacts."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    action_type TEXT,
                    payload TEXT,
                    signature TEXT,
                    timestamp TEXT,
                    agent_id TEXT,
                    session_id TEXT,
                    chain_of_thought TEXT,
                    verification_key_id TEXT,
                    previous_artifact_id TEXT
                )
            """)
            conn.commit()

    def store(self, artifact: dict[str, Any]) -> None:
        """Store artifact in local cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    artifact["artifact_id"],
                    artifact["action_type"],
                    json.dumps(artifact["payload"]).decode(),
                    artifact["signature"],
                    artifact["timestamp"],
                    artifact["agent_id"],
                    artifact["session_id"],
                    artifact.get("chain_of_thought"),
                    artifact.get("verification_key_id"),
                    artifact.get("previous_artifact_id"),
                ),
            )
            conn.commit()

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        """Retrieve artifact by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)).fetchone()

            if row:
                d = dict(row)
                d["payload"] = json.loads(d["payload"])
                return d
        return None


# ---------------------------------------------------------------------------
# Hook
# ---------------------------------------------------------------------------


class MAIFHook:
    """Intercepts agent actions to record MAIF artifacts (WP-3002)."""

    def __init__(
        self, artifact_store: MAIFArtifactStore, private_key: rsa.RSAPrivateKey, agent_id: str, session_id: str
    ) -> None:
        self.store = artifact_store
        self.private_key = private_key
        self.agent_id = agent_id
        self.session_id = session_id
        self.last_artifact_id: str | None = None

    def record_action(self, action_type: str, payload: dict[str, Any], chain_of_thought: str | None = None) -> str:
        """Record an action as a signed MAIF artifact."""
        artifact_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        signature = _sign_artifact_dict(payload, timestamp, self.agent_id, self.private_key)

        artifact = {
            "artifact_id": artifact_id,
            "action_type": action_type,
            "payload": payload,
            "signature": signature,
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "chain_of_thought": chain_of_thought,
            "previous_artifact_id": self.last_artifact_id,
        }

        self.store.store(artifact)
        self.last_artifact_id = artifact_id
        return artifact_id
