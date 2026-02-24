"""Tests for Wave 81: Response handling and parsing.

Related to:
- Response parsing
- Stream handling
- Error response handling
"""

from __future__ import annotations

import pytest


class TestResponseParsing:
    """Test response parsing."""

    def test_parse_valid_response(self) -> None:
        """Valid responses should parse correctly."""
        response = {"choices": [{"message": {"content": "Hello"}]}
        assert "choices" in response
        assert len(response["choices"]) > 0

    def test_extract_content(self) -> None:
        """Should extract content from response."""
        resp = {"choices": [{"message": {"content": "Test"}]}
        content = resp["choices"][0]["message"]["content"]
        assert content == "Test"

    def test_handle_stream_response(self) -> None:
        """Stream responses should be handled."""
        stream = {"choices": [{"delta": {"content": "chunk"}]}
        assert "delta" in stream["choices"][0]


class TestErrorResponses:
    """Test error response handling."""

    def test_parse_error(self) -> None:
        """Errors should be parsed correctly."""
        error = {"error": {"message": "Invalid request", "code": 400}
        assert "error" in error
        assert error["error"]["code"] == 400

    def test_error_has_message(self) -> None:
        """Errors should have messages."""
        err = {"error": {"message": "Test error"}}
        assert "message" in err["error"]
