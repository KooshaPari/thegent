// Auto-generated TypeScript declarations for universal_adapter
// Source: generate-api-docs.py

export declare class UniversalToolAdapter {
  constructor();
  call_tool(command: string): void;
  register_adapter(command: string, adapter_fn: Callable<(Ellipsis, Any)>): void;
}

export declare function call_tool(command: string): void;
export declare function register_adapter(command: string, adapter_fn: Callable<(Ellipsis, Any)>): void;
export declare function validate_tool_schema(operation: Operation, payload: Record<(str, Any)>): void;
