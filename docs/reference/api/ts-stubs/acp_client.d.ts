// Auto-generated TypeScript declarations for acp_client
// Source: generate-api-docs.py

export declare class ACPClient {
  constructor(base_url: string, agent_id: string);
}

export declare class ACPClientError extends Exception {
  constructor(status_code: number, message: string);
}

export declare class ACPResult {
}

export declare class ACPServerUnreachableError extends Exception {
}
