# Plan: research-library-cache

## Objective

Consolidate all custom cache implementations into `cachetools` equivalents (LRU, TTL, LFU), reducing code duplication and improving thread safety and cache governance.

## Approach

1. Audit existing custom cache implementations across the codebase
2. Map each custom cache to its `cachetools` equivalent
3. Replace implementations with thin wrappers following project conventions
4. Validate thread safety and eviction behavior under test
