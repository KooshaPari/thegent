// Auto-generated usage examples for test_cache
// Source: generate-api-docs.py

import { TestL1Cache, TestL2Cache, TestLayeredCache, TestPerformance, test_clear, test_clear_both_layers, test_l1_hit, test_l1_sub_millisecond, test_l2_fallback, test_l2_miss, test_l2_sub_10ms, test_lru_eviction, test_persistence, test_set_and_get, test_set_stores_both_layers, test_stats, test_ttl_expiration } from "./test_cache";

// Create a TestL1Cache instance
const testl1cache = new TestL1Cache();
testl1cache.test_clear();
testl1cache.test_lru_eviction();
testl1cache.test_set_and_get();
testl1cache.test_stats();
testl1cache.test_ttl_expiration();

// Create a TestL2Cache instance
const testl2cache = new TestL2Cache();
testl2cache.test_clear();
testl2cache.test_persistence();
testl2cache.test_set_and_get();
testl2cache.test_stats();
testl2cache.test_ttl_expiration();

// Create a TestLayeredCache instance
const testlayeredcache = new TestLayeredCache();
testlayeredcache.test_clear_both_layers();
testlayeredcache.test_l1_hit();
testlayeredcache.test_l2_fallback();
testlayeredcache.test_l2_miss();
testlayeredcache.test_set_stores_both_layers();

// Create a TestPerformance instance
const testperformance = new TestPerformance();
testperformance.test_l1_sub_millisecond();
testperformance.test_l2_sub_10ms();

// Call test_clear
test_clear(undefined as unknown as any);
// Call test_clear_both_layers
test_clear_both_layers(undefined as unknown as any);
// Call test_l1_hit
test_l1_hit(undefined as unknown as any);
// Call test_l1_sub_millisecond
test_l1_sub_millisecond(undefined as unknown as any);
// Call test_l2_fallback
test_l2_fallback(undefined as unknown as any);
// Call test_l2_miss
test_l2_miss(undefined as unknown as any);
// Call test_l2_sub_10ms
test_l2_sub_10ms(undefined as unknown as any);
// Call test_lru_eviction
test_lru_eviction(undefined as unknown as any);
// Call test_persistence
test_persistence(undefined as unknown as any);
// Call test_set_and_get
test_set_and_get(undefined as unknown as any);
// Call test_set_stores_both_layers
test_set_stores_both_layers(undefined as unknown as any);
// Call test_stats
test_stats(undefined as unknown as any);
// Call test_ttl_expiration
test_ttl_expiration(undefined as unknown as any);
