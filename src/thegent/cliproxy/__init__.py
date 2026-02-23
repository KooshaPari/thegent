"""CLIProxy adapter - pure transformation functions.

This package contains pure functions that can be used independently of
ThegentSettings or external services.
"""

from .transforms import *

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
