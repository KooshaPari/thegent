"""Tests for LiteLLM config settings."""

import pytest
from thegent.config import ThegentSettings


class TestLiteLLMConfig:
    """Test LiteLLM configuration settings."""

    def test_litellm_routing_policy_default(self):
        """Default routing policy is 'cheapest'."""
        settings = ThegentSettings()
        assert settings.litellm_routing_policy == "cheapest"

    def test_litellm_timeout_default(self):
        """Default LiteLLM timeout is 300 seconds."""
        settings = ThegentSettings()
        assert settings.litellm_timeout == 300

    def test_litellm_retries_default(self):
        """Default LiteLLM retries is 2."""
        settings = ThegentSettings()
        assert settings.litellm_num_retries == 2
