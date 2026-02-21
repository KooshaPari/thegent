// Auto-generated usage examples for input_guardrails
// Source: generate-api-docs.py

import { GuardrailResult, InputGuardrails, check, guardrails_from_settings } from "./input_guardrails";

// Create a GuardrailResult instance
const guardrailresult = new GuardrailResult();

// Create a InputGuardrails instance
const inputguardrails = new InputGuardrails();
inputguardrails.check("example_prompt", "example_agent", undefined as unknown as any, undefined as unknown as any);

// Call check
check(undefined as unknown as any, "example_prompt", "example_agent", undefined as unknown as any, undefined as unknown as any);
// Call guardrails_from_settings
guardrails_from_settings(undefined as unknown as any);
