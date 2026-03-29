// Auto-generated TypeScript declarations for test_cache
// Source: generate-api-docs.py

export declare class TestL1Cache {
  test_clear(): void;
  test_lru_eviction(): void;
  test_set_and_get(): void;
  test_stats(): void;
  test_ttl_expiration(): void;
}

export declare class TestL2Cache {
  test_clear(): void;
  test_persistence(): void;
  test_set_and_get(): void;
  test_stats(): void;
  test_ttl_expiration(): void;
}

export declare class TestLayeredCache {
  test_clear_both_layers(): void;
  test_l1_hit(): void;
  test_l2_fallback(): void;
  test_l2_miss(): void;
  test_set_stores_both_layers(): void;
}

export declare class TestPerformance {
  test_l1_sub_millisecond(): void;
  test_l2_sub_10ms(): void;
}

export declare function test_clear(): void;
export declare function test_clear_both_layers(): void;
export declare function test_l1_hit(): void;
export declare function test_l1_sub_millisecond(): void;
export declare function test_l2_fallback(): void;
export declare function test_l2_miss(): void;
export declare function test_l2_sub_10ms(): void;
export declare function test_lru_eviction(): void;
export declare function test_persistence(): void;
export declare function test_set_and_get(): void;
export declare function test_set_stores_both_layers(): void;
export declare function test_stats(): void;
export declare function test_ttl_expiration(): void;
