// Auto-generated usage examples for redaction
// Source: generate-api-docs.py

import { PIIRedactor, contains_pii, redact } from "./redaction";

// Create a PIIRedactor instance
const piiredactor = new PIIRedactor(undefined as unknown as any);
piiredactor.contains_pii("example_text");
piiredactor.redact("example_text", "example_mode");

// Call contains_pii
contains_pii(undefined as unknown as any, "example_text");
// Call redact
redact(undefined as unknown as any, "example_text", "example_mode");
