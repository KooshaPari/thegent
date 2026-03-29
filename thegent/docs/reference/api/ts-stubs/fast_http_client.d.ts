// Auto-generated TypeScript declarations for fast_http_client
// Source: generate-api-docs.py

export declare class FastHTTPClient {
  constructor(impersonate: any);
  backend(): void;
  close(): void;
  get(url: string): void;
  post(url: string): void;
  request(method: string, url: string): void;
}

export declare function backend(): void;
export declare function close(): void;
export declare function get(url: string): void;
export declare function get_http_client(impersonate: any): void;
export declare function http_get(url: string): void;
export declare function http_post(url: string): void;
export declare function http_request(method: string, url: string): void;
export declare function post(url: string): void;
export declare function request(method: string, url: string): void;
