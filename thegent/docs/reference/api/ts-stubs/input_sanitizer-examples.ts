// Auto-generated usage examples for input_sanitizer
// Source: generate-api-docs.py

import { InputSanitizer, detect_command_injection, detect_sql_injection, detect_xss, sanitize_input, sanitize_string, validate_filename } from "./input_sanitizer";

// Create a InputSanitizer instance
const inputsanitizer = new InputSanitizer();
inputsanitizer.detect_command_injection("example_value");
inputsanitizer.detect_sql_injection("example_value");
inputsanitizer.detect_xss("example_value");
inputsanitizer.sanitize_input(undefined as unknown as any, "example_input_type");
inputsanitizer.sanitize_string("example_value", undefined as unknown as any);
inputsanitizer.validate_filename("example_filename");

// Call detect_command_injection
detect_command_injection("example_value");
// Call detect_sql_injection
detect_sql_injection("example_value");
// Call detect_xss
detect_xss("example_value");
// Call sanitize_input
sanitize_input(undefined as unknown as any, "example_input_type");
// Call sanitize_string
sanitize_string("example_value", undefined as unknown as any);
// Call validate_filename
validate_filename("example_filename");
