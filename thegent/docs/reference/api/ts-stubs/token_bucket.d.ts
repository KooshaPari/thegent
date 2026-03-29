// Auto-generated TypeScript declarations for token_bucket
// Source: generate-api-docs.py

export declare class RateLimitedSwarmRunner {
  constructor(bucket: any, default_timeout_s: any);
  configure_from_env(): void;
  run(): void;
}

export declare class TokenBucket {
  constructor(config: TokenBucketConfig);
  available(): void;
  consume(tokens: number): void;
  consume_blocking(tokens: number, timeout_s: any): void;
  refill(tokens: any): void;
  try_consume(tokens: number): void;
}

export declare class TokenBucketConfig {
}

export declare function available(): void;
export declare function configure_from_env(): void;
export declare function consume(tokens: number): void;
export declare function consume_blocking(tokens: number, timeout_s: any): void;
export declare function refill(tokens: any): void;
export declare function run(): void;
export declare function try_consume(tokens: number): void;
