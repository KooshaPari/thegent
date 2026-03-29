// Auto-generated usage examples for patterns
// Source: generate-api-docs.py

import { ToolAborted, choice_with_retry, confirm_before_action, decorator, progress_with_fallback, register_tool_pattern_tools, retry_on_error } from "./patterns";

// Create a ToolAborted instance
const toolaborted = new ToolAborted();

// Call choice_with_retry
choice_with_retry(undefined as unknown as Array<string>, "example_prompt", 0);
// Call confirm_before_action
confirm_before_action("example_action_description");
// Call decorator
decorator(undefined as unknown as Callable);
// Call progress_with_fallback
progress_with_fallback(0, undefined as unknown as any);
// Call register_tool_pattern_tools
register_tool_pattern_tools(undefined as unknown as any);
// Call retry_on_error
retry_on_error(0, undefined as unknown as [(type<BaseException>, Ellipsis)]);
