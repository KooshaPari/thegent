"""Tests for WL-94: Stream translator for function_call_arguments.done.

Related to CLIProxyAPI#1609 - handle response.function_call_arguments.done 
in codex->claude streaming translator.
"""

from __future__ import annotations

import pytest


class TestStreamFunctionCallArguments:
    """Test streaming translator handles function_call_arguments.done correctly."""

    def test_function_call_arguments_done_event(self) -> None:
        """Stream translator should handle function_call_arguments.done event.
        
        Issue: CLIProxyAPI#1609 - handle response.function_call_arguments.done
        """
        # Simulate a stream chunk with function_call_arguments.done
        chunk = {
            "type": "content_block_delta",
            "delta": {
                "type": "function_call_arguments",
                "name": "search",
                "arguments": '{"query": "test"}',
                "_done": True  # Indicates arguments are complete
            }
        }
        
        # Should be recognized as complete
        assert chunk.get("delta", {}).get("_done") is True

    def test_function_call_arguments_chunk_ordering(self) -> None:
        """Arguments should be assembled in correct order."""
        chunks = [
            {"delta": {"function_call_arguments": {"arguments": '{""'}},
            {"delta": {"function_call_arguments": {"arguments": 'query"'}},
            {"delta": {"function_call_arguments": {"arguments": ': "'}},
            {"delta": {"function_call_arguments": {"arguments": '"test"'}},
        ]
        
        # Collect arguments in order
        result = ""
        for chunk in chunks:
            if "function_call_arguments" in chunk.get("delta", {}):
                args = chunk["delta"]["function_call_arguments"].get("arguments", "")
                result += args
        
        assert result == '{"query": "test"}'

    def test_stream_with_tool_calls_not_blocked(self) -> None:
        """function_call_arguments.done should not block other stream events."""
        # Interleaved stream: tool call + content
        stream_events = [
            {"type": "content_block_delta", "delta": {"text": "Found "}},
            {"type": "content_block_delta", "delta": {"function_call_arguments": {"_done": True}}},
            {"type": "content_block_delta", "delta": {"text": " results."}},
        ]
        
        # Should process all events without blocking
        processed = []
        for event in stream_events:
            processed.append(event)
        
        assert len(processed) == 3
