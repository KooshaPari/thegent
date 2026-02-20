"""Tests for the Mojo Bridge module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from thegent.infra.mojo_bridge import (
    MojoBridge,
    MojoNotAvailableError,
    MojoTask,
    check_mojo_status,
    get_bridge,
)


class TestMojoBridge:
    """Test suite for MojoBridge."""
    
    def test_bridge_initialization(self, tmp_path):
        """Test that MojoBridge initializes correctly."""
        bridge = MojoBridge(
            mojo_root=tmp_path / "mojo",
            cache_root=tmp_path / "cache",
        )
        
        assert bridge.mojo_root == tmp_path / "mojo"
        assert bridge.cache_root == tmp_path / "cache"
        assert bridge.default_timeout > 0
        
    def test_mojo_not_available_error(self):
        """Test MojoNotAvailableError can be raised."""
        with pytest.raises(MojoNotAvailableError):
            raise MojoNotAvailableError("Test error")
            
    def test_mojo_task_creation(self):
        """Test MojoTask creation."""
        task = MojoTask(
            task_id="test_001",
            module="test_module",
            function="test_function",
            args={"arg1": "value1"},
            timeout=30.0,
        )
        
        assert task.task_id == "test_001"
        assert task.module == "test_module"
        assert task.function == "test_function"
        assert task.args == {"arg1": "value1"}
        assert task.timeout == 30.0
        
    def test_get_bridge_singleton(self):
        """Test that get_bridge returns a singleton."""
        bridge1 = get_bridge()
        bridge2 = get_bridge()
        
        assert bridge1 is bridge2
        
    def test_install_instructions_darwin(self):
        """Test install instructions on Darwin."""
        bridge = MojoBridge()
        
        # This test just verifies the method exists and returns a string
        instructions = bridge.install_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 0
        
    @pytest.mark.asyncio
    async def test_check_mojo_status_returns_dict(self):
        """Test that check_mojo_status returns proper dict structure."""
        status = await check_mojo_status()
        
        assert isinstance(status, dict)
        assert "available" in status
        assert "version" in status
        assert "install_instructions" in status
        
    @pytest.mark.asyncio
    async def test_dispatch_returns_graceful_error_when_not_available(self):
        """Test that dispatch handles unavailable Mojo gracefully."""
        bridge = MojoBridge()
        
        # Mock is_available to return False
        with patch.object(bridge, 'is_available', False):
            task = MojoTask(
                task_id="test_001",
                module="test",
                function="hello",
                args={},
            )
            
            result = await bridge.dispatch(task)
            
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "mojo_not_available"


class TestMojoBridgeAvailability:
    """Tests for Mojo availability checking."""
    
    def test_check_mojo_returns_boolean(self):
        """Test that _check_mojo returns a boolean."""
        bridge = MojoBridge()
        result = bridge._check_mojo()
        
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
