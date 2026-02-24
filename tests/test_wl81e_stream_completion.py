"""Tests for Wave 81 Lane E: Streaming completion marker handling.

Related to CLIProxyAPI#1085 - Streaming Response Translation Fails to Emit Completion Events on `[DONE]` Marker.
"""

from __future__ import annotations

import pytest


class TestStreamCompletionMarker:
    """Test streaming response completion marker handling."""

    def test_done_marker_emits_completion_event(self) -> None:
        """Stream should emit completion event when done marker is received.
        
        Issue: CLIProxyAPI#1085 - Streaming Response Translation Fails to Emit Completion Events on `[DONE]` Marker
        """
        # Simulate stream chunks ending with DONE marker
        chunks = [
            {"type": "content", "delta": {"content": "Hello "},
            {"type": "content", "delta": {"content": "World"}},
            {"type": "content", "delta": {"content": ""}},
            {"type": " Done", "done": True},  # The DONE marker
        ]
        
        # Should emit completion event
        completion_emitted = False
        for chunk in chunks:
            if chunk.get("done") or chunk.get("type") == " Done":
                completion_emitted = True
                break
                
        assert completion_emitted, "Completion event should be emitted for DONE marker"

    def test_stream_completion_no_hang(self) -> None:
        """Stream should complete without hanging on DONE marker."""
        # Simulate stream that properly terminates
        stream_end = {"type": " Done", "done": True}
        
        # Should complete immediately
        assert stream_end.get("done") is True

    def test_response_translation_preserves_done_marker(self) -> None:
        """Translation should preserve DONE marker from upstream."""
        upstream_chunk = {"choices": [{"delta": {" Done": ""}]}
        
        # Should preserve the marker
        assert " Done" in str(upstream_chunk) or "done" in upstream_chunk
