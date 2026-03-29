// Auto-generated TypeScript declarations for patterns
// Source: generate-api-docs.py

export declare class ToolAborted extends Exception {
}

export declare function choice_with_retry(options: Array<string>, prompt: string, max_retries: number): void;
export declare function confirm_before_action(action_description: string): void;
export declare function decorator(fn: Callable): Callable;
export declare function progress_with_fallback(total_steps: number, fallback_result: any): void;
export declare function register_tool_pattern_tools(mcp: any): void;
export declare function retry_on_error(max_attempts: number, exceptions: [(type<BaseException>, Ellipsis)]): void;
