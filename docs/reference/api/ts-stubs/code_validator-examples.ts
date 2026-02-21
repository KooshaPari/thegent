// Auto-generated usage examples for code_validator
// Source: generate-api-docs.py

import { CodeExampleValidator, validate_code_snippet, validate_doc_file } from "./code_validator";

// Create a CodeExampleValidator instance
const codeexamplevalidator = new CodeExampleValidator(false, false);
codeexamplevalidator.validate_code_snippet("example_code", "example_language");
codeexamplevalidator.validate_doc_file("example_file_path");

// Call validate_code_snippet
validate_code_snippet(undefined as unknown as any, "example_code", "example_language");
// Call validate_doc_file
validate_doc_file(undefined as unknown as any, "example_file_path");
