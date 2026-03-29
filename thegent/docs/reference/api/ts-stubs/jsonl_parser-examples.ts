// Auto-generated usage examples for jsonl_parser
// Source: generate-api-docs.py

import { JsonlParser, count, filter, sample, stream } from "./jsonl_parser";

// Create a JsonlParser instance
const jsonlparser = new JsonlParser();
jsonlparser.count("example_path");
jsonlparser.filter("example_path", "example_key", "example_value");
jsonlparser.sample("example_path", 0);
jsonlparser.stream("example_path");

// Call count
count(undefined as unknown as any, "example_path");
// Call filter
filter(undefined as unknown as any, "example_path", "example_key", "example_value");
// Call sample
sample(undefined as unknown as any, "example_path", 0);
// Call stream
stream(undefined as unknown as any, "example_path");
