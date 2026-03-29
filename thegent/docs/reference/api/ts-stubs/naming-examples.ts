// Auto-generated usage examples for naming
// Source: generate-api-docs.py

import { NamingConvention, suggest_name, validate } from "./naming";

// Create a NamingConvention instance
const namingconvention = new NamingConvention();
namingconvention.suggest_name("example_name", "example_convention_type");
namingconvention.validate("example_name", "example_convention_type");

// Call suggest_name
suggest_name(undefined as unknown as any, "example_name", "example_convention_type");
// Call validate
validate(undefined as unknown as any, "example_name", "example_convention_type");
