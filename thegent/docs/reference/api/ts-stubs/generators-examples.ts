// Auto-generated usage examples for generators
// Source: generate-api-docs.py

import { ArtifactGeneratorFactory, CodeArtifactGenerator, DecisionArtifactGenerator, ToolArtifactGenerator, code, create_branching_point, create_code_change, create_decision, create_file_operation, create_mcp_call, create_tool_invocation, decision, tool } from "./generators";

// Create a ArtifactGeneratorFactory instance
const artifactgeneratorfactory = new ArtifactGeneratorFactory(undefined as unknown as MAIFArtifactGenerator);
artifactgeneratorfactory.code();
artifactgeneratorfactory.decision();
artifactgeneratorfactory.tool();

// Create a CodeArtifactGenerator instance
const codeartifactgenerator = new CodeArtifactGenerator(undefined as unknown as MAIFArtifactGenerator);
codeartifactgenerator.create_code_change("example_agent_id", "example_session_id", "example_file_path", undefined as unknown as CodeChangeType, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array, undefined as unknown as any);
codeartifactgenerator.create_file_operation("example_agent_id", "example_session_id", undefined as unknown as FileOperationType, "example_source_path", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);

// Create a DecisionArtifactGenerator instance
const decisionartifactgenerator = new DecisionArtifactGenerator(undefined as unknown as MAIFArtifactGenerator);
decisionartifactgenerator.create_branching_point("example_agent_id", "example_session_id", "example_condition", false, "example_true_branch", "example_false_branch", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
decisionartifactgenerator.create_decision("example_agent_id", "example_session_id", undefined as unknown as DecisionType, undefined as unknown as Array<string>, "example_selected_option", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);

// Create a ToolArtifactGenerator instance
const toolartifactgenerator = new ToolArtifactGenerator(undefined as unknown as MAIFArtifactGenerator);
toolartifactgenerator.create_mcp_call("example_agent_id", "example_session_id", "example_mcp_server", "example_mcp_tool", undefined as unknown as ToolResultStatus, undefined as unknown as Record<(str, Any)>, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
toolartifactgenerator.create_tool_invocation("example_agent_id", "example_session_id", undefined as unknown as ToolType, "example_tool_name", undefined as unknown as Record<(str, Any)>, undefined as unknown as ToolResultStatus, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);

// Call code
code(undefined as unknown as any);
// Call create_branching_point
create_branching_point(undefined as unknown as any, "example_agent_id", "example_session_id", "example_condition", false, "example_true_branch", "example_false_branch", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
// Call create_code_change
create_code_change(undefined as unknown as any, "example_agent_id", "example_session_id", "example_file_path", undefined as unknown as CodeChangeType, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array, undefined as unknown as any);
// Call create_decision
create_decision(undefined as unknown as any, "example_agent_id", "example_session_id", undefined as unknown as DecisionType, undefined as unknown as Array<string>, "example_selected_option", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
// Call create_file_operation
create_file_operation(undefined as unknown as any, "example_agent_id", "example_session_id", undefined as unknown as FileOperationType, "example_source_path", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call create_mcp_call
create_mcp_call(undefined as unknown as any, "example_agent_id", "example_session_id", "example_mcp_server", "example_mcp_tool", undefined as unknown as ToolResultStatus, undefined as unknown as Record<(str, Any)>, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
// Call create_tool_invocation
create_tool_invocation(undefined as unknown as any, "example_agent_id", "example_session_id", undefined as unknown as ToolType, "example_tool_name", undefined as unknown as Record<(str, Any)>, undefined as unknown as ToolResultStatus, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
// Call decision
decision(undefined as unknown as any);
// Call tool
tool(undefined as unknown as any);
