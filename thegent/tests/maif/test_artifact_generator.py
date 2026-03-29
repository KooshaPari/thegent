"""Unit tests for MAIF artifact generator.

Tests the MAIFArtifactGenerator class for artifact creation, signing, and hash chain.
"""

import hashlib
import time

import pytest

from thegent.maif.artifact_generator import MAIFArtifactGenerator
from thegent.maif.crypto import SigningKey
from thegent.maif.models import ActionType


class TestArtifactGeneratorCreation:
    """Tests for artifact generator creation."""

    def test_create_generator(self):
        """Test creating an artifact generator."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)
        assert generator is not None
        assert generator.signer is signing_key
        assert generator.last_hash == {}


class TestArtifactGeneration:
    """Tests for artifact generation."""

    def test_create_minimal_artifact(self):
        """Test creating a minimal artifact."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifact = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"input",
            output_data=b"output",
        )

        assert artifact is not None
        assert artifact.action_type == ActionType.WRITE
        assert artifact.agent_id == "agent-1"
        assert artifact.session_id == "session-1"
        assert artifact.input_hash == hashlib.sha256(b"input").hexdigest()
        assert artifact.output_hash == hashlib.sha256(b"output").hexdigest()
        assert artifact.previous_hash == ""  # First artifact
        assert artifact.signature != ""  # Should be signed

    def test_create_artifact_with_metadata(self):
        """Test creating artifact with metadata."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        metadata = {"file": "/path/to/file.py", "lines": 42}
        artifact = generator.create_artifact(
            action_type=ActionType.EDIT,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"before",
            output_data=b"after",
            metadata=metadata,
        )

        assert artifact.metadata == metadata

    def test_create_artifact_empty_data(self):
        """Test creating artifact with empty input/output."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifact = generator.create_artifact(
            action_type=ActionType.DELETE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"",
            output_data=b"",
        )

        assert artifact.input_hash == hashlib.sha256(b"").hexdigest()
        assert artifact.output_hash == hashlib.sha256(b"").hexdigest()

    def test_create_artifact_missing_agent_id(self):
        """Test that missing agent_id raises ValueError."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        with pytest.raises(ValueError, match="agent_id and session_id are required"):
            generator.create_artifact(
                action_type=ActionType.WRITE,
                agent_id="",
                session_id="session-1",
                input_data=b"x",
                output_data=b"y",
            )

    def test_create_artifact_missing_session_id(self):
        """Test that missing session_id raises ValueError."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        with pytest.raises(ValueError, match="agent_id and session_id are required"):
            generator.create_artifact(
                action_type=ActionType.WRITE,
                agent_id="agent-1",
                session_id="",
                input_data=b"x",
                output_data=b"y",
            )

    def test_artifact_has_valid_signature(self):
        """Test that created artifact has valid signature."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)
        verifying_key = signing_key.get_public_key()

        artifact = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"input",
            output_data=b"output",
        )

        # Verify signature
        artifact_bytes = artifact.serialize_for_signing()
        signature_bytes = bytes.fromhex(artifact.signature)
        assert verifying_key.verify(artifact_bytes, signature_bytes)


class TestHashChainTracking:
    """Tests for hash chain tracking."""

    def test_first_artifact_no_previous_hash(self):
        """Test that first artifact has no previous hash."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifact = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        assert artifact.previous_hash == ""

    def test_hash_chain_tracks_sessions(self):
        """Test that generator tracks hash chains per session."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        # Create artifacts in session 1
        artifact1a = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        # Create artifacts in session 2
        artifact2a = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-2",
            input_data=b"a",
            output_data=b"b",
        )

        # Both should have empty previous_hash
        assert artifact1a.previous_hash == ""
        assert artifact2a.previous_hash == ""

        # Create second artifact in session 1
        artifact1b = generator.create_artifact(
            action_type=ActionType.EDIT,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"y",
            output_data=b"z",
        )

        # Should link to first artifact in session 1
        assert artifact1b.previous_hash == artifact1a.get_hash()

        # Create second artifact in session 2
        artifact2b = generator.create_artifact(
            action_type=ActionType.EDIT,
            agent_id="agent-1",
            session_id="session-2",
            input_data=b"b",
            output_data=b"c",
        )

        # Should link to first artifact in session 2
        assert artifact2b.previous_hash == artifact2a.get_hash()

    def test_get_last_hash(self):
        """Test retrieving last hash for a session."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        # Empty session has no hash
        assert generator.get_last_hash("unknown-session") == ""

        # Create artifact
        artifact1 = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        # Check last hash matches
        assert generator.get_last_hash("session-1") == artifact1.get_hash()

        # Create another artifact
        artifact2 = generator.create_artifact(
            action_type=ActionType.EDIT,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"y",
            output_data=b"z",
        )

        # Check last hash updated
        assert generator.get_last_hash("session-1") == artifact2.get_hash()

    def test_reset_session(self):
        """Test resetting session hash chain."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        # Create artifact
        artifact1 = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        assert generator.get_last_hash("session-1") == artifact1.get_hash()

        # Reset session
        generator.reset_session("session-1")
        assert generator.get_last_hash("session-1") == ""

        # Create new artifact (should have no previous hash)
        artifact2 = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"a",
            output_data=b"b",
        )

        assert artifact2.previous_hash == ""


class TestArtifactTimestamps:
    """Tests for artifact timestamps."""

    def test_artifact_has_timestamp(self):
        """Test that artifacts have reasonable timestamps."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        before = int(time.time())
        artifact = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )
        after = int(time.time())

        assert before <= artifact.timestamp <= after + 1

    def test_artifact_timestamps_increase(self):
        """Test that successive artifacts have increasing timestamps."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifact1 = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        artifact2 = generator.create_artifact(
            action_type=ActionType.EDIT,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"y",
            output_data=b"z",
        )

        assert artifact2.timestamp >= artifact1.timestamp


class TestArtifactIDs:
    """Tests for artifact ID generation."""

    def test_artifact_ids_unique(self):
        """Test that generated artifact IDs are unique."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifacts = []
        for i in range(10):
            artifact = generator.create_artifact(
                action_type=ActionType.WRITE,
                agent_id="agent-1",
                session_id=f"session-{i}",
                input_data=f"x{i}".encode(),
                output_data=f"y{i}".encode(),
            )
            artifacts.append(artifact)

        ids = [a.id for a in artifacts]
        assert len(ids) == len(set(ids))  # All unique

    def test_artifact_id_format(self):
        """Test that artifact IDs are valid hex strings."""
        signing_key = SigningKey.generate()
        generator = MAIFArtifactGenerator(signing_key)

        artifact = generator.create_artifact(
            action_type=ActionType.WRITE,
            agent_id="agent-1",
            session_id="session-1",
            input_data=b"x",
            output_data=b"y",
        )

        # Should be 32-char hex (128-bit UUID)
        assert len(artifact.id) == 32
        assert all(c in "0123456789abcdef" for c in artifact.id)
