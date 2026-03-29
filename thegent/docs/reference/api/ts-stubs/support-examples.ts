// Auto-generated usage examples for support
// Source: generate-api-docs.py

import { SupportModeSession, SupportRedactor, get_view, redact_payload, redact_text } from "./support";

// Create a SupportModeSession instance
const supportmodesession = new SupportModeSession("example_engineer_id");
supportmodesession.get_view("example_raw_output");

// Create a SupportRedactor instance
const supportredactor = new SupportRedactor();
supportredactor.redact_payload(undefined as unknown as Record<(str, Any)>);
supportredactor.redact_text("example_text");

// Call get_view
get_view(undefined as unknown as any, "example_raw_output");
// Call redact_payload
redact_payload(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call redact_text
redact_text(undefined as unknown as any, "example_text");
