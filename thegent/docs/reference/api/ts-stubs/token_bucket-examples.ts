// Auto-generated usage examples for token_bucket
// Source: generate-api-docs.py

import { RateLimitedSwarmRunner, TokenBucket, TokenBucketConfig, available, configure_from_env, consume, consume_blocking, refill, run, try_consume } from "./token_bucket";

// Create a RateLimitedSwarmRunner instance
const ratelimitedswarmrunner = new RateLimitedSwarmRunner(undefined as unknown as any, undefined as unknown as any);
ratelimitedswarmrunner.configure_from_env();
ratelimitedswarmrunner.run();

// Create a TokenBucket instance
const tokenbucket = new TokenBucket(undefined as unknown as TokenBucketConfig);
tokenbucket.available();
tokenbucket.consume(0);
tokenbucket.consume_blocking(0, undefined as unknown as any);
tokenbucket.refill(undefined as unknown as any);
tokenbucket.try_consume(0);

// Create a TokenBucketConfig instance
const tokenbucketconfig = new TokenBucketConfig();

// Call available
available(undefined as unknown as any);
// Call configure_from_env
configure_from_env(undefined as unknown as any);
// Call consume
consume(undefined as unknown as any, 0);
// Call consume_blocking
consume_blocking(undefined as unknown as any, 0, undefined as unknown as any);
// Call refill
refill(undefined as unknown as any, undefined as unknown as any);
// Call run
run();
// Call try_consume
try_consume(undefined as unknown as any, 0);
