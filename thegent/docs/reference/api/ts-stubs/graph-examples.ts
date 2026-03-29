// Auto-generated usage examples for graph
// Source: generate-api-docs.py

import { KnowledgeGraph, add_relation, query } from "./graph";

// Create a KnowledgeGraph instance
const knowledgegraph = new KnowledgeGraph("example_api_token");
knowledgegraph.add_relation("example_source", "example_relation", "example_target");
knowledgegraph.query("example_query_text");

// Call add_relation
add_relation(undefined as unknown as any, "example_source", "example_relation", "example_target");
// Call query
query(undefined as unknown as any, "example_query_text");
