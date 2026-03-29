// Auto-generated usage examples for pre_warmer
// Source: generate-api-docs.py

import { CachePreWarmer, WarmingStrategy, _StrategyState, get_stats, is_running, model_list_strategy, register_strategy, session_list_strategy, start_background, stop_background, unregister_strategy, warm_all, warm_key } from "./pre_warmer";

// Create a CachePreWarmer instance
const cacheprewarmer = new CachePreWarmer(undefined as unknown as MultiLevelCache);
cacheprewarmer.get_stats();
cacheprewarmer.is_running();
cacheprewarmer.register_strategy(undefined as unknown as WarmingStrategy);
cacheprewarmer.start_background();
cacheprewarmer.stop_background(0);
cacheprewarmer.unregister_strategy("example_name");
cacheprewarmer.warm_all();
cacheprewarmer.warm_key("example_key", undefined as unknown as Callable<(Any, Any)>);

// Create a WarmingStrategy instance
const warmingstrategy = new WarmingStrategy();

// Create a _StrategyState instance
const _strategystate = new _StrategyState();

// Call get_stats
get_stats(undefined as unknown as any);
// Call is_running
is_running(undefined as unknown as any);
// Call model_list_strategy
model_list_strategy(undefined as unknown as Callable<(Any, Any)>, undefined as unknown as any, 0);
// Call register_strategy
register_strategy(undefined as unknown as any, undefined as unknown as WarmingStrategy);
// Call session_list_strategy
session_list_strategy(undefined as unknown as Callable<(Any, Any)>, undefined as unknown as any, 0);
// Call start_background
start_background(undefined as unknown as any);
// Call stop_background
stop_background(undefined as unknown as any, 0);
// Call unregister_strategy
unregister_strategy(undefined as unknown as any, "example_name");
// Call warm_all
warm_all(undefined as unknown as any);
// Call warm_key
warm_key(undefined as unknown as any, "example_key", undefined as unknown as Callable<(Any, Any)>);
