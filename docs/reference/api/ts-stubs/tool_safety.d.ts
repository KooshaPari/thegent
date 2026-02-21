// Auto-generated TypeScript declarations for tool_safety
// Source: generate-api-docs.py

export declare class SafetyViolation extends BaseModel {
}

export declare class ToolSafetyChecker {
  constructor();
  analyze_chain(tool_chain: Array<string>): void;
  check_pre_flight(proposed_chain: Array<string>): void;
}

export declare function analyze_chain(tool_chain: Array<string>): void;
export declare function check_pre_flight(proposed_chain: Array<string>): void;
