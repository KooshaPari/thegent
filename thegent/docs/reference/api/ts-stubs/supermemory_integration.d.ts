// Auto-generated TypeScript declarations for supermemory_integration
// Source: generate-api-docs.py

export declare class SupermemoryIntegration {
  constructor(api_key: any);
  retrieve_memory(query: string, level: string): void;
  store_memory(content: string, level: string): void;
}

export declare function retrieve_memory(query: string, level: string): void;
export declare function store_memory(content: string, level: string): void;
