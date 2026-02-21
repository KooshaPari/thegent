// Auto-generated TypeScript declarations for generators
// Source: generate-api-docs.py

export declare class ArtifactGeneratorFactory {
  constructor(maif_generator: MAIFArtifactGenerator);
  code(): void;
  decision(): void;
  tool(): void;
}

export declare class CodeArtifactGenerator {
  constructor(maif_generator: MAIFArtifactGenerator);
  create_code_change(agent_id: string, session_id: string, file_path: string, change_type: CodeChangeType, before_content: Uint8Array, after_content: Uint8Array, language: any): void;
  create_file_operation(agent_id: string, session_id: string, operation_type: FileOperationType, source_path: string, dest_path: any, before_content: any, after_content: any): void;
}

export declare class DecisionArtifactGenerator {
  constructor(maif_generator: MAIFArtifactGenerator);
  create_branching_point(agent_id: string, session_id: string, condition: string, condition_result: boolean, true_branch: string, false_branch: string, input_data: Uint8Array, output_data: Uint8Array): void;
  create_decision(agent_id: string, session_id: string, decision_type: DecisionType, options_considered: Array<string>, selected_option: string, input_data: Uint8Array, output_data: Uint8Array): void;
}

export declare class ToolArtifactGenerator {
  constructor(maif_generator: MAIFArtifactGenerator);
  create_mcp_call(agent_id: string, session_id: string, mcp_server: string, mcp_tool: string, call_status: ToolResultStatus, request_parameters: Record<(str, Any)>, input_data: Uint8Array, output_data: Uint8Array): void;
  create_tool_invocation(agent_id: string, session_id: string, tool_type: ToolType, tool_name: string, arguments: Record<(str, Any)>, result_status: ToolResultStatus, input_data: Uint8Array, output_data: Uint8Array): void;
}

export declare function code(): void;
export declare function create_branching_point(agent_id: string, session_id: string, condition: string, condition_result: boolean, true_branch: string, false_branch: string, input_data: Uint8Array, output_data: Uint8Array): void;
export declare function create_code_change(agent_id: string, session_id: string, file_path: string, change_type: CodeChangeType, before_content: Uint8Array, after_content: Uint8Array, language: any): void;
export declare function create_decision(agent_id: string, session_id: string, decision_type: DecisionType, options_considered: Array<string>, selected_option: string, input_data: Uint8Array, output_data: Uint8Array): void;
export declare function create_file_operation(agent_id: string, session_id: string, operation_type: FileOperationType, source_path: string, dest_path: any, before_content: any, after_content: any): void;
export declare function create_mcp_call(agent_id: string, session_id: string, mcp_server: string, mcp_tool: string, call_status: ToolResultStatus, request_parameters: Record<(str, Any)>, input_data: Uint8Array, output_data: Uint8Array): void;
export declare function create_tool_invocation(agent_id: string, session_id: string, tool_type: ToolType, tool_name: string, arguments: Record<(str, Any)>, result_status: ToolResultStatus, input_data: Uint8Array, output_data: Uint8Array): void;
export declare function decision(): void;
export declare function tool(): void;
