//! In-memory cache adapter.
//!
//! A thread-safe in-memory cache implementation using DashMap.

use std::collections::HashMap;
use std::sync::Arc;

use async_trait::async_trait;
use dashmap::DashMap;
use tokio::sync::RwLock;
use tokio::time::{Duration, Instant};

use crate::domain::{
    CacheEntry, CacheKey, CachePort, EvictionPolicy, Result,
};
use crate::domain::ports::outbound::CachePort;

/// Configuration for the in-memory cache.
#[derive(Debug, Clone)]
pub struct InMemoryCacheConfig {
    /// Maximum number of entries (None = unlimited).
    pub max_entries: Option<usize>,
    /// Default TTL in seconds (None = no expiration).
    pub default_ttl_seconds: Option<u64>,
    /// Eviction policy to use when cache is full.
    pub eviction_policy: EvictionPolicy,
    /// Enable automatic cleanup of expired entries.
    pub cleanup_enabled: bool,
    /// Interval for cleanup task (if enabled).
    pub cleanup_interval: Duration,
}

impl Default for InMemoryCacheConfig {
    fn default() -> Self {
        Self {
            max_entries: None,
            default_ttl_seconds: Some(3600), // 1 hour
            eviction_policy: EvictionPolicy::LRU,
            cleanup_enabled: true,
            cleanup_interval: Duration::from_secs(60),
        }
    }
}

/// Thread-safe in-memory cache implementation.
pub struct InMemoryCache {
    entries: Arc<DashMap<String, CacheEntry<Vec<u8>>>>,
    access_order: Arc<RwLock<Vec<(String, Instant)>>>,
    config: InMemoryCacheConfig,
}

impl InMemoryCache {
    /// Create a new in-memory cache with default configuration.
    pub fn new() -> Self {
        Self::with_config(InMemoryCacheConfig::default())
    }

    /// Create a new in-memory cache with custom configuration.
    pub fn with_config(config: InMemoryCacheConfig) -> Self {
        Self {
            entries: Arc::new(DashMap::new()),
            access_order: Arc::new(RwLock::new(Vec::new())),
            config,
        }
    }

    /// Get the number of entries.
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// Check if empty.
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// Clear all entries.
    pub fn clear(&self) {
        self.entries.clear();
    }

    /// Evict entries based on the configured policy.
    async fn evict_if_needed(&self) {
        if let Some(max) = self.config.max_entries {
            while self.entries.len() >= max {
                self.evict_one().await;
            }
        }
    }

    /// Evict a single entry based on eviction policy.
    async fn evict_one(&self) {
        match self.config.eviction_policy {
            EvictionPolicy::LRU | EvictionPolicy::FIFO => {
                let key = {
                    let mut order = self.access_order.write().await;
                    order.sort_by_key(|(_, time)| *time);
                    order.pop().map(|(k, _)| k)
                };
                if let Some(key) = key {
                    self.entries.remove(&key);
                }
            }
            EvictionPolicy::LFU => {
                // Find entry with lowest access count
                let key = self.entries.iter()
                    .min_by_key(|e| e.value().access_count())
                    .map(|e| e.key().clone());
                if let Some(key) = key {
                    self.entries.remove(&key);
                }
            }
            EvictionPolicy::Random => {
                let key = self.entries.iter()
                    .nth(rand_index(self.entries.len()))
                    .map(|e| e.key().clone());
                if let Some(key) = key {
                    self.entries.remove(&key);
                }
            }
            EvictionPolicy::NoEviction => {
                // Do nothing
            }
            EvictionPolicy::MRU => {
                let key = {
                    let mut order = self.access_order.write().await;
                    order.sort_by_key(|(_, time)| std::cmp::Reverse(*time));
                    order.pop().map(|(k, _)| k)
                };
                if let Some(key) = key {
                    self.entries.remove(&key);
                }
            }
        }
    }
}

fn rand_index(max: usize) -> usize {
    use std::time::SystemTime;
    let seed = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap()
        .subsec_nanos() as usize;
    seed % max.max(1)
}

impl Default for InMemoryCache {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl CachePort for InMemoryCache {
    async fn get(&self, key: &CacheKey) -> Result<Option<CacheEntry<Vec<u8>>>> {
        let key_str = key.to_string();
        
        if let Some(mut entry) = self.entries.get(&key_str).map(|e| e.clone()) {
            if entry.is_expired() {
                self.entries.remove(&key_str);
                return Ok(None);
            }
            entry.touch();
            
            // Update access order for LRU
            let mut order = self.access_order.write().await;
            if let Some(pos) = order.iter().position(|(k, _)| k == &key_str) {
                order[pos].1 = Instant::now();
            }
            
            Ok(Some(entry))
        } else {
            Ok(None)
        }
    }

    async fn set(&self, key: &CacheKey, value: Vec<u8>, ttl_seconds: Option<u64>) -> Result<()> {
        let ttl = ttl_seconds.or(self.config.default_ttl_seconds);
        let entry = CacheEntry::new(value).with_ttl_opt(ttl);
        
        // Update access order
        let key_str = key.to_string();
        {
            let mut order = self.access_order.write().await;
            if let Some(pos) = order.iter().position(|(k, _)| k == &key_str) {
                order[pos].1 = Instant::now();
            } else {
                order.push((key_str.clone(), Instant::now()));
            }
        }
        
        // Evict if needed before inserting
        self.evict_if_needed().await;
        
        self.entries.insert(key_str, entry);
        Ok(())
    }

    async fn delete(&self, key: &CacheKey) -> Result<bool> {
        let key_str = key.to_string();
        let removed = self.entries.remove(&key_str).is_some();
        
        if removed {
            let mut order = self.access_order.write().await;
            order.retain(|(k, _)| k != &key_str);
        }
        
        Ok(removed)
    }

    async fn contains(&self, key: &CacheKey) -> Result<bool> {
        Ok(self.entries.contains_key(&key.to_string()))
    }

    async fn clear(&self) -> Result<()> {
        self.entries.clear();
        self.access_order.write().await.clear();
        Ok(())
    }

    async fn len(&self) -> Result<usize> {
        Ok(self.entries.len())
    }

    async fn is_empty(&self) -> Result<bool> {
        Ok(self.entries.is_empty())
    }

    fn eviction_policy(&self) -> EvictionPolicy {
        self.config.eviction_policy
    }

    fn capacity(&self) -> Option<usize> {
        self.config.max_entries
    }

    async fn keys(&self, pattern: Option<&str>) -> Result<Vec<CacheKey>> {
        let keys: Vec<CacheKey> = self.entries.iter()
            .filter(|entry| {
                match pattern {
                    Some(p) => entry.key().contains(p),
                    None => true,
                }
            })
            .map(|e| CacheKey::new(e.key().clone()))
            .collect();
        Ok(keys)
    }
}

// Add helper method for optional TTL
impl<V> CacheEntry<V> {
    /// Set TTL only if Some is provided.
    pub fn with_ttl_opt(self, ttl_seconds: Option<u64>) -> Self {
        match ttl_seconds {
            Some(ttl) => self.with_ttl(ttl),
            None => self,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_cache_basic_operations() {
        let cache = InMemoryCache::new();
        
        let key = CacheKey::new("test");
        cache.set(&key, b"value".to_vec(), None).await.unwrap();
        
        let result = cache.get(&key).await.unwrap();
        assert!(result.is_some());
        assert_eq!(result.unwrap().value(), &b"value".to_vec());
    }

    #[tokio::test]
    async fn test_cache_delete() {
        let cache = InMemoryCache::new();
        
        let key = CacheKey::new("test");
        cache.set(&key, b"value".to_vec(), None).await.unwrap();
        
        let deleted = cache.delete(&key).await.unwrap();
        assert!(deleted);
        
        let result = cache.get(&key).await.unwrap();
        assert!(result.is_none());
    }

    #[tokio::test]
    async fn test_cache_eviction() {
        let config = InMemoryCacheConfig {
            max_entries: Some(2),
            ..Default::default()
        };
        let cache = InMemoryCache::with_config(config);
        
        cache.set(&CacheKey::new("1"), b"1".to_vec(), None).await.unwrap();
        cache.set(&CacheKey::new("2"), b"2".to_vec(), None).await.unwrap();
        cache.set(&CacheKey::new("3"), b"3".to_vec(), None).await.unwrap();
        
        // One of the first two should be evicted
        assert!(cache.len() <= 2);
    }
}
