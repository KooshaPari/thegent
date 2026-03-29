// Auto-generated usage examples for checker
// Source: generate-api-docs.py

import { CheckerAgent, CheckerDecision, CheckerResult, decide } from "./checker";

// Create a CheckerAgent instance
const checkeragent = new CheckerAgent(undefined as unknown as ThegentSettings, "example_agent_name");
checkeragent.decide(undefined as unknown as Record<(str, Any, str)>, "example_todo_spec", undefined as unknown as Record<(str, Any, str)>, "example_agent_response");

// Create a CheckerDecision instance
const checkerdecision = new CheckerDecision();

// Create a CheckerResult instance
const checkerresult = new CheckerResult();

// Call decide
decide(undefined as unknown as any, undefined as unknown as Record<(str, Any, str)>, "example_todo_spec", undefined as unknown as Record<(str, Any, str)>, "example_agent_response");
