"""MAIF (Model-Aware Information Flow) action artifacts.

Provides signed, immutable records of agent actions (WP-3002).
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

_log = logging.getLogger(__name__)


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
        return serialization.load_pem_private_key(key_file.read(), password=password)


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


def sign_artifact(payload: dict[str, Any], timestamp: str, agent_id: str, private_key: rsa.RSAPrivateKey) -> str:
    """Sign artifact with RSA private key (MAIF)."""
    # Create canonical payload
    canonical = json.dumps({"payload": payload, "timestamp": timestamp, "agent_id": agent_id}, sort_keys=True)

    # Calculate SHA-256 hash
    message_hash = hashlib.sha256(canonical.encode()).digest()

    # Sign with PKCS#1 v1.5 padding
    signature = private_key.sign(message_hash, padding.PKCS1v15(), hashes.SHA256())

    return base64.b64encode(signature).decode()


def verify_artifact(artifact: dict[str, Any], public_key: rsa.RSAPublicKey) -> bool:
    """Verify artifact signature (MAIF)."""
    try:
        signature = base64.b64decode(artifact["signature"])

        canonical = json.dumps(
            {"payload": artifact["payload"], "timestamp": artifact["timestamp"], "agent_id": artifact["agent_id"]},
            sort_keys=True,
        )

        message_hash = hashlib.sha256(canonical.encode()).digest()

        public_key.verify(signature, message_hash, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception as e:
        _log.debug("MAIF verification failed: %s", e)
        return False


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
                    json.dumps(artifact["payload"]),
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

        signature = sign_artifact(payload, timestamp, self.agent_id, self.private_key)

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
