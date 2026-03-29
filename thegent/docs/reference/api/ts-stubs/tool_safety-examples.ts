// Auto-generated usage examples for tool_safety
// Source: generate-api-docs.py

import { SafetyViolation, ToolSafetyChecker, analyze_chain, check_pre_flight } from "./tool_safety";

// Create a SafetyViolation instance
const safetyviolation = new SafetyViolation();

// Create a ToolSafetyChecker instance
const toolsafetychecker = new ToolSafetyChecker();
toolsafetychecker.analyze_chain(undefined as unknown as Array<string>);
toolsafetychecker.check_pre_flight(undefined as unknown as Array<string>);

// Call analyze_chain
analyze_chain(undefined as unknown as any, undefined as unknown as Array<string>);
// Call check_pre_flight
check_pre_flight(undefined as unknown as any, undefined as unknown as Array<string>);
