// Auto-generated usage examples for rules_loader
// Source: generate-api-docs.py

import { Rule, RulesLoader, get_rule, key, load } from "./rules_loader";

// Create a Rule instance
const rule = new Rule();
rule.key();

// Create a RulesLoader instance
const rulesloader = new RulesLoader(undefined as unknown as any);
rulesloader.get_rule("example_command", undefined as unknown as any);
rulesloader.load(false);

// Call get_rule
get_rule(undefined as unknown as any, "example_command", undefined as unknown as any);
// Call key
key(undefined as unknown as any);
// Call load
load(undefined as unknown as any, false);
