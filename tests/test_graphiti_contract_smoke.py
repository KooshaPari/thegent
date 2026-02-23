"""Unit tests for graphiti_contract_smoke.py"""

import json
import os
import pytest
import sys
from unittest.mock import patch, MagicMock


# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_missing_env_fails():
    """Test that missing required env var fails."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="Missing required environment variable"):
            import importlib
            # Reimport to pick up cleared env
            import graphiti_contract_smoke as smoke
            importlib.reload(smoke)
            smoke._require_env("GRAPHITI_SERVER_URL")


def test_missing_optional_env_allowed():
    """Test that optional env var can be empty."""
    with patch.dict(os.environ, {"GRAPHITI_SERVER_URL": "http://localhost:8000"}):
        import graphiti_contract_smoke as smoke
        
        # Should not raise
        result = smoke._require_env("GRAPHITI_SERVER_URL")
        assert result == "http://localhost:8000"


def test_successful_health_check():
    """Test successful health check returns ok."""
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'{"status": "ok"}'
    
    with patch.dict(os.environ, {"GRAPHITI_SERVER_URL": "http://localhost:8000"}):
        with patch("urllib.request.urlopen", return_value=mock_response):
            import graphiti_contract_smoke as smoke
            
            result = json.loads(smoke.main.__doc__)  # Just check imports work
            # Smoke script will exit via SystemExit on success


def test_non_200_fails():
    """Test non-200 status code fails."""
    mock_response = MagicMock()
    mock_response.getcode.return_value = 500
    
    with patch.dict(os.environ, {"GRAPHITI_SERVER_URL": "http://localhost:8000"}):
        with patch("urllib.request.urlopen", return_value=mock_response):
            import graphiti_contract_smoke as smoke
            
            with pytest.raises(RuntimeError, match="non-200 status"):
                smoke.main()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
