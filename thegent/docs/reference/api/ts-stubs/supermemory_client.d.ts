// Auto-generated TypeScript declarations for supermemory_client
// Source: generate-api-docs.py

export declare class MemoryEntry {
  from_api_dict(data: Record<(str, Any)>): void;
}

export declare class SupermemoryAPIError extends Exception {
  constructor(status_code: number, message: string);
}

export declare class SupermemoryClient {
  constructor(api_key: any, base_url: any);
}

export declare class SupermemoryConfigError extends Exception {
}

export declare function from_api_dict(data: Record<(str, Any)>): void;
