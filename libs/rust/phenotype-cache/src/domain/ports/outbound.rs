//! Outbound ports - Interfaces for infrastructure access.
//!
//! These ports define what the domain needs from external systems.
//! Implementation is in the adapters layer.

use async_trait::async_trait;

use super::{CacheEntry, CacheError, CacheKey, EvictionPolicy, Result};

/// Cache port interface.
///
/// This is the primary outbound port for cache operations.
/// Implementation can be in-memory, Redis, Memcached, etc.
#[async_trait]
pub trait CachePort: Send + Sync {
    /// Get a value from the cache.
    async fn get(&self, key: &CacheKey) -> Result<Option<CacheEntry<Vec<u8>>>>;

    /// Set a value in the cache.
    async fn set(&self, key: &CacheKey, value: Vec<u8>, ttl_seconds: Option<u64>) -> Result<()>;

    /// Delete a value from the cache.
    async fn delete(&self, key: &CacheKey) -> Result<bool>;

    /// Check if a key exists in the cache.
    async fn contains(&self, key: &CacheKey) -> Result<bool>;

    /// Clear all entries from the cache.
    async fn clear(&self) -> Result<()>;

    /// Get the number of entries in the cache.
    async fn len(&self) -> Result<usize>;

    /// Check if the cache is empty.
    async fn is_empty(&self) -> Result<bool>;

    /// Get the eviction policy.
    fn eviction_policy(&self) -> EvictionPolicy;

    /// Get the maximum capacity.
    fn capacity(&self) -> Option<usize>;

    /// Get keys matching a pattern.
    async fn keys(&self, pattern: Option<&str>) -> Result<Vec<CacheKey>>;

    /// Get multiple values at once (batch operation).
    async fn get_many(&self, keys: &[CacheKey]) -> Result<Vec<Option<CacheEntry<Vec<u8>>>>> {
        let mut results = Vec::with_capacity(keys.len());
        for key in keys {
            results.push(self.get(key).await?);
        }
        Ok(results)
    }

    /// Set multiple values at once (batch operation).
    async fn set_many(&self, entries: &[(CacheKey, Vec<u8>, Option<u64>)]) -> Result<()> {
        for (key, value, ttl) in entries {
            self.set(key, value.clone(), *ttl).await?;
        }
        Ok(())
    }

    /// Delete multiple values at once (batch operation).
    async fn delete_many(&self, keys: &[CacheKey]) -> Result<usize> {
        let mut deleted = 0;
        for key in keys {
            if self.delete(key).await? {
                deleted += 1;
            }
        }
        Ok(deleted)
    }
}
