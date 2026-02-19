"""Integration tests for cliproxy_adapter: Responses API bridge."""

import pytest

from thegent.cliproxy_adapter import (
    _process_sse_line,
    _responses_to_chat_completions,
    create_adapter_app,
)


@pytest.mark.integration
class TestAdapterResponsesBridge:
    """Test adapter Responses API transform pipeline."""

    def test_sse_line_transform_pipeline(self) -> None:
        """Chat Completions SSE line -> Responses API format."""
        line = b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n'
        out = _process_sse_line(line, transform=True)
        assert out is not None
        assert b"response.output_item.added" in out
        assert b"Hi" in out

    def test_responses_to_chat_completions_for_backend(self) -> None:
        """Responses API body -> Chat Completions format for backend."""
        body = {
            "model": "glm-5",
            "input": [
                {"type": "message", "role": "user", "content": [{"type": "text", "text": "Hello"}]},
            ],
            "stream": True,
        }
        out = _responses_to_chat_completions(body)
        assert out["model"] == "glm-5"
        assert out["messages"] == [{"role": "user", "content": "Hello"}]
        assert out["stream"] is True

    def test_create_adapter_app_routes(self) -> None:
        """Adapter app has /v1/responses route and proxy handler."""
        app = create_adapter_app("http://127.0.0.1:8318/v1")
        assert hasattr(app, "state")
        assert app.state.backend_url == "http://127.0.0.1:8318/v1"
