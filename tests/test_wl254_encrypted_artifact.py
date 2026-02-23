"""Tests for WL-254: Encrypted Artifact Option.

Verifies encrypted artifact storage, retrieval, and configuration management.

# @trace WL-254
"""

from __future__ import annotations

import pytest

from thegent.integrations.encrypted_artifact import (
    ArtifactEncryptionConfig,
    EncryptedArtifactStore,
)


@pytest.mark.requirement("WL-254")
class TestEncryptedArtifact:
    """WL-254: Encrypted artifact option."""

    def test_encryption_config_defaults(self):
        """ArtifactEncryptionConfig uses default algorithm and key_id."""
        config = ArtifactEncryptionConfig()
        assert config.algorithm == "AES-256"
        assert config.key_id == "default"

    def test_encryption_config_custom(self):
        """ArtifactEncryptionConfig accepts custom values."""
        config = ArtifactEncryptionConfig(
            algorithm="ChaCha20",
            key_id="prod-key-1",
        )
        assert config.algorithm == "ChaCha20"
        assert config.key_id == "prod-key-1"

    def test_encryption_config_validation_empty_algorithm(self):
        """ArtifactEncryptionConfig rejects empty algorithm."""
        with pytest.raises(ValueError, match="algorithm cannot be empty"):
            ArtifactEncryptionConfig(algorithm="", key_id="default")

    def test_encryption_config_validation_empty_key_id(self):
        """ArtifactEncryptionConfig rejects empty key_id."""
        with pytest.raises(ValueError, match="key_id cannot be empty"):
            ArtifactEncryptionConfig(algorithm="AES-256", key_id="")

    def test_artifact_store_creation(self):
        """EncryptedArtifactStore can be instantiated."""
        store = EncryptedArtifactStore()
        assert store is not None

    def test_artifact_store_store_with_config(self):
        """store() stores artifact with provided config."""
        store = EncryptedArtifactStore()
        config = ArtifactEncryptionConfig(
            algorithm="AES-256",
            key_id="prod-key",
        )
        artifact_id = store.store("art-1", {"data": "sensitive"}, config)

        assert artifact_id == "art-1"

    def test_artifact_store_store_with_default_config(self):
        """store() uses default config when none provided."""
        store = EncryptedArtifactStore()
        artifact_id = store.store("art-1", {"data": "sensitive"})

        assert artifact_id == "art-1"
        config = store.get_config("art-1")
        assert config.algorithm == "AES-256"
        assert config.key_id == "default"

    def test_artifact_store_store_validation_empty_id(self):
        """store() rejects empty artifact_id."""
        store = EncryptedArtifactStore()
        with pytest.raises(ValueError, match="artifact_id cannot be empty"):
            store.store("", {"data": "test"})

    def test_artifact_store_store_validation_none_data(self):
        """store() rejects None data."""
        store = EncryptedArtifactStore()
        with pytest.raises(ValueError, match="data cannot be None"):
            store.store("art-1", None)

    def test_artifact_store_retrieve(self):
        """retrieve() returns stored artifact data."""
        store = EncryptedArtifactStore()
        original_data = {"key": "value", "nested": {"field": 42}}
        store.store("art-1", original_data)

        retrieved_data = store.retrieve("art-1")
        assert retrieved_data == original_data

    def test_artifact_store_retrieve_not_found(self):
        """retrieve() raises KeyError for missing artifact."""
        store = EncryptedArtifactStore()
        with pytest.raises(KeyError, match="Artifact 'art-1' not found"):
            store.retrieve("art-1")

    def test_artifact_store_get_config(self):
        """get_config() returns encryption config for artifact."""
        store = EncryptedArtifactStore()
        config = ArtifactEncryptionConfig(
            algorithm="ChaCha20",
            key_id="test-key",
        )
        store.store("art-1", {}, config)

        retrieved_config = store.get_config("art-1")
        assert retrieved_config.algorithm == "ChaCha20"
        assert retrieved_config.key_id == "test-key"

    def test_artifact_store_get_config_not_found(self):
        """get_config() raises KeyError for missing artifact."""
        store = EncryptedArtifactStore()
        with pytest.raises(KeyError, match="Artifact 'art-1' not found"):
            store.get_config("art-1")

    def test_artifact_store_list_artifacts_empty(self):
        """list_artifacts() returns empty list for new store."""
        store = EncryptedArtifactStore()
        artifacts = store.list_artifacts()
        assert artifacts == []

    def test_artifact_store_list_artifacts_single(self):
        """list_artifacts() returns single artifact ID."""
        store = EncryptedArtifactStore()
        store.store("art-1", {"data": "test"})

        artifacts = store.list_artifacts()
        assert artifacts == ["art-1"]

    def test_artifact_store_list_artifacts_multiple(self):
        """list_artifacts() returns all artifact IDs."""
        store = EncryptedArtifactStore()
        store.store("art-1", {})
        store.store("art-2", {})
        store.store("art-3", {})

        artifacts = sorted(store.list_artifacts())
        assert artifacts == ["art-1", "art-2", "art-3"]

    def test_artifact_store_overwrite_artifact(self):
        """store() can overwrite existing artifact."""
        store = EncryptedArtifactStore()
        config1 = ArtifactEncryptionConfig(algorithm="AES-256", key_id="key-1")
        config2 = ArtifactEncryptionConfig(algorithm="ChaCha20", key_id="key-2")

        store.store("art-1", {"version": 1}, config1)
        store.store("art-1", {"version": 2}, config2)

        data = store.retrieve("art-1")
        config = store.get_config("art-1")

        assert data == {"version": 2}
        assert config.algorithm == "ChaCha20"
        assert config.key_id == "key-2"

    def test_artifact_store_complex_data(self):
        """store() and retrieve() handle complex nested data."""
        store = EncryptedArtifactStore()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
                {"id": 2, "name": "Bob", "roles": ["user"]},
            ],
            "settings": {
                "notifications": {"enabled": True, "frequency": "daily"},
                "privacy": {"show_profile": False},
            },
            "metadata": {
                "created_at": "2026-02-22T00:00:00Z",
                "version": 1,
            },
        }
        store.store("art-1", complex_data)

        retrieved = store.retrieve("art-1")
        assert retrieved == complex_data
        assert retrieved["users"][0]["name"] == "Alice"
        assert retrieved["settings"]["notifications"]["enabled"]

    def test_artifact_store_empty_data(self):
        """store() and retrieve() handle empty dictionaries."""
        store = EncryptedArtifactStore()
        store.store("art-1", {})

        retrieved = store.retrieve("art-1")
        assert retrieved == {}

    def test_artifact_store_multiple_configs(self):
        """Different artifacts can have different configs."""
        store = EncryptedArtifactStore()
        config1 = ArtifactEncryptionConfig(algorithm="AES-256", key_id="key-1")
        config2 = ArtifactEncryptionConfig(algorithm="ChaCha20", key_id="key-2")
        config3 = ArtifactEncryptionConfig(algorithm="RSA-2048", key_id="key-3")

        store.store("art-1", {}, config1)
        store.store("art-2", {}, config2)
        store.store("art-3", {}, config3)

        assert store.get_config("art-1").algorithm == "AES-256"
        assert store.get_config("art-2").algorithm == "ChaCha20"
        assert store.get_config("art-3").algorithm == "RSA-2048"

    def test_artifact_store_config_isolation(self):
        """Changing returned config does not affect stored config."""
        store = EncryptedArtifactStore()
        config = ArtifactEncryptionConfig(algorithm="AES-256", key_id="key-1")
        store.store("art-1", {}, config)

        # Modify the original config object
        config.key_id = "modified-key"

        # Retrieve and verify stored config is unchanged
        stored_config = store.get_config("art-1")
        assert stored_config.key_id == "key-1"

    def test_artifact_store_full_workflow(self):
        """Full workflow: store, retrieve, config, and list."""
        store = EncryptedArtifactStore()

        # Store multiple artifacts
        config1 = ArtifactEncryptionConfig(algorithm="AES-256", key_id="prod")
        config2 = ArtifactEncryptionConfig(algorithm="ChaCha20", key_id="dev")

        store.store("art-prod", {"env": "production"}, config1)
        store.store("art-dev", {"env": "development"}, config2)

        # List and verify
        artifacts = sorted(store.list_artifacts())
        assert artifacts == ["art-dev", "art-prod"]

        # Retrieve and verify data
        prod_data = store.retrieve("art-prod")
        dev_data = store.retrieve("art-dev")
        assert prod_data == {"env": "production"}
        assert dev_data == {"env": "development"}

        # Verify configs
        prod_config = store.get_config("art-prod")
        dev_config = store.get_config("art-dev")
        assert prod_config.key_id == "prod"
        assert dev_config.key_id == "dev"

    def test_artifact_store_case_sensitive_ids(self):
        """Artifact IDs are case-sensitive."""
        store = EncryptedArtifactStore()
        store.store("Art-1", {})
        store.store("art-1", {})

        artifacts = sorted(store.list_artifacts())
        assert len(artifacts) == 2
        assert artifacts == ["Art-1", "art-1"]
