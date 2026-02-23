"""Pure transformation functions from cliproxy_adapter.

Extractable functions that don't depend on ThegentSettings or bifrost.
"""

from typing import Any

# Re-export for backward compatibility
from .cliproxy_models_transform import transform_models_response, _compute_models_etag
from .cliproxy_request_transform import (
    _extract_delta_content,
    _extract_delta_tool_calls,
    _extract_usage,
    _map_model_for_backend,
    _process_sse_line,
    _responses_to_chat_completions,
)
from .cliproxy_header_utils import (
    extract_websocket_forward_headers,
    filter_inbound_response_headers,
    sanitize_outbound_request_headers,
)
from .cliproxy_stream_state import ResponsesStreamState

__all__ = [
    "ResponsesStreamState",
    "_compute_models_etag",
    "_extract_delta_content",
    "_extract_delta_tool_calls",
    "_extract_usage",
    "_map_model_for_backend",
    "_process_sse_line",
    "_responses_to_chat_completions",
    "extract_websocket_forward_headers",
    "filter_inbound_response_headers",
    "sanitize_outbound_request_headers",
    "transform_models_response",
]
