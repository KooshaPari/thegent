// Auto-generated TypeScript declarations for cache_provider
// Source: generate-api-docs.py

export declare class CacheItem {
  is_expired(): void;
  ttl_remaining(): void;
}

export declare class CacheProvider extends ABC {
}

export declare function is_expired(): void;
export declare function ttl_remaining(): void;
