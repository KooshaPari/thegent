// Auto-generated TypeScript declarations for graph
// Source: generate-api-docs.py

export declare class KnowledgeGraph {
  constructor(api_token: string);
  add_relation(source: string, relation: string, target: string): void;
  query(query_text: string): void;
}

export declare function add_relation(source: string, relation: string, target: string): void;
export declare function query(query_text: string): void;
