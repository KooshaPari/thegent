// Auto-generated usage examples for redis_concurrency
// Source: generate-api-docs.py

import { RedisConcurrencyController, RedisConfig, _InMemoryStore, count_with_prefix_sync, from_env, from_settings, get_active_count, is_available, list_active, make_redis_concurrency_controller } from "./redis_concurrency";

// Create a RedisConcurrencyController instance
const redisconcurrencycontroller = new RedisConcurrencyController(undefined as unknown as any, undefined as unknown as any, 0);
redisconcurrencycontroller.get_active_count();
redisconcurrencycontroller.is_available();
redisconcurrencycontroller.list_active();

// Create a RedisConfig instance
const redisconfig = new RedisConfig();
redisconfig.from_env();
redisconfig.from_settings();

// Create a _InMemoryStore instance
const _inmemorystore = new _InMemoryStore();
_inmemorystore.count_with_prefix_sync("example_prefix");

// Call count_with_prefix_sync
count_with_prefix_sync(undefined as unknown as any, "example_prefix");
// Call from_env
from_env(undefined as unknown as any);
// Call from_settings
from_settings(undefined as unknown as any);
// Call get_active_count
get_active_count(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call list_active
list_active(undefined as unknown as any);
// Call make_redis_concurrency_controller
make_redis_concurrency_controller(undefined as unknown as any, 0);
