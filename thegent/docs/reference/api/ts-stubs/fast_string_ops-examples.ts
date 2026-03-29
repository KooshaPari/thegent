// Auto-generated usage examples for fast_string_ops
// Source: generate-api-docs.py

import { FastStringOps, fuzzy_match, fuzzy_ratio, regex_findall, regex_search } from "./fast_string_ops";

// Create a FastStringOps instance
const faststringops = new FastStringOps();
faststringops.fuzzy_match("example_query", undefined as unknown as Array<string>, 0, 0);
faststringops.fuzzy_ratio("example_str1", "example_str2");
faststringops.regex_findall("example_pattern", "example_text");
faststringops.regex_search("example_pattern", "example_text");

// Call fuzzy_match
fuzzy_match("example_query", undefined as unknown as Array<string>, 0, 0);
// Call fuzzy_ratio
fuzzy_ratio("example_str1", "example_str2");
// Call regex_findall
regex_findall("example_pattern", "example_text");
// Call regex_search
regex_search("example_pattern", "example_text");
