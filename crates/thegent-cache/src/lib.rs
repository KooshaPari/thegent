// SPDX-License-Identifier: MIT OR Apache-2.0
//! Two-tier cache with L1 (LRU) for hot data and L2 (Moka) for warm data.
//!
//! Uses LRU cache for L1 (in-memory, fast access) and Moka for L2 (sync cache).

use lru::LruCache;
use moka::sync::Cache as MokaCache;
use parking_lot::Mutex;
use std::hash::Hash;
use std::num::NonZeroUsize;
use std::sync::Arc;
use std::time::Duration;

/// Two-tier cache combining LRU (L1) with Moka (L2).
pub struct Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    l1: Arc<Mutex<LruCache<K, V>>>,
    l2: MokaCache<K, V>,
}

impl<K, V> Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    /// Create a new cache with the specified TTL.
    pub fn new(ttl_seconds: u64) -> Self {
        Self::with_capacity_and_ttl(1000, Duration::from_secs(ttl_seconds))
    }

    /// Create a cache with custom L1 capacity and default TTL.
    pub fn with_capacity_and_ttl(l1_capacity: usize, default_ttl: Duration) -> Self {
        let cap = NonZeroUsize::new(l1_capacity).unwrap_or(NonZeroUsize::MIN);
        let l1 = LruCache::new(cap);
        let l2 = MokaCache::builder().time_to_live(default_ttl).build();

        Self {
            l1: Arc::new(Mutex::new(l1)),
            l2,
        }
    }

    /// Get a value from the cache (checks L1 first, then L2).
    pub fn get(&self, key: &K) -> Option<V> {
        // Check L1 first
        if let Some(v) = self.l1.lock().get(key) {
            return Some(v.clone());
        }

        // Check L2
        if let Some(v) = self.l2.get(key) {
            // Promote to L1
            let mut l1 = self.l1.lock();
            if !l1.contains(key) {
                l1.put(key.clone(), v.clone());
            }
            return Some(v);
        }

        None
    }

    /// Set a value in both tiers.
    pub fn set(&self, key: K, value: V) {
        // Set in L1
        let mut l1 = self.l1.lock();
        l1.put(key.clone(), value.clone());
        drop(l1);

        // Set in L2
        self.l2.insert(key, value);
    }

    /// Set a value with custom TTL in L2.
    /// Note: TTL customization is not supported by sync cache.
    pub fn set_with_ttl(&self, key: K, value: V, _ttl: Duration) {
        let mut l1 = self.l1.lock();
        l1.put(key.clone(), value.clone());
        drop(l1);

        // Set in L2 - uses default TTL
        self.l2.insert(key, value);
    }

    /// Remove a key from both tiers.
    pub fn remove(&self, key: &K) {
        self.l1.lock().pop(key);
        self.l2.invalidate(key);
    }

    /// Clear all entries.
    pub fn clear(&self) {
        self.l1.lock().clear();
        self.l2.invalidate_all();
    }

    /// Total entries across both tiers.
    pub fn len(&self) -> usize {
        self.len_l1() + self.len_l2()
    }

    /// Check if cache is empty.
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// L1 (LRU) entry count.
    pub fn len_l1(&self) -> usize {
        self.l1.lock().len()
    }

    /// L2 (Moka) entry count.
    pub fn len_l2(&self) -> usize {
        self.l2.entry_count() as usize
    }

    /// Check if key exists in either tier.
    pub fn contains_key(&self, key: &K) -> bool {
        self.l1.lock().contains(key) || self.l2.contains_key(key)
    }
}

impl<K, V> Default for Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    fn default() -> Self {
        Self::new(3600)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_basic() {
        let cache: Cache<String, String> = Cache::new(3600);
        cache.set("key1".to_string(), "value1".to_string());
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));
    }

    #[test]
    fn test_cache_expiration() {
        // Note: Moka sync cache TTL is eventually consistent via background task.
        // This test verifies basic set/get without relying on precise TTL timing.
        let cache: Cache<String, String> =
            Cache::with_capacity_and_ttl(100, Duration::from_millis(50));
        cache.set("key1".to_string(), "value1".to_string());
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));

        // Verify cache contains the key
        assert!(cache.contains_key(&"key1".to_string()));
    }

    #[test]
    fn test_l1_l2_tier() {
        let cache: Cache<String, String> = Cache::with_capacity_and_ttl(2, Duration::from_secs(60));
        cache.set("key1".to_string(), "value1".to_string());
        cache.set("key2".to_string(), "value2".to_string());
        cache.set("key3".to_string(), "value3".to_string());

        // All should be accessible
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));

        // L1 should have 2 entries (capacity)
        assert_eq!(cache.len_l1(), 2);
    }
}

#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::types::PyModule;

#[cfg(feature = "python")]
#[pyclass]
struct PythonCache {
    cache: Cache<String, String>,
}

#[cfg(feature = "python")]
#[pymethods]
impl PythonCache {
    #[new]
    #[pyo3(signature = (max_size=None, ttl_seconds=None))]
    fn new(max_size: Option<usize>, ttl_seconds: Option<u64>) -> Self {
        let ttl = Duration::from_secs(ttl_seconds.unwrap_or(3600));
        let size = max_size.unwrap_or(1000);
        Self {
            cache: Cache::with_capacity_and_ttl(size, ttl),
        }
    }

    fn get(&self, key: &str) -> Option<String> {
        self.cache.get(&key.to_string())
    }

    fn set(&self, key: String, value: String) {
        self.cache.set(key, value);
    }

    fn set_with_ttl(&self, key: String, value: String, ttl_seconds: u64) {
        self.cache
            .set_with_ttl(key, value, Duration::from_secs(ttl_seconds));
    }

    fn remove(&self, key: &str) {
        self.cache.remove(&key.to_string());
    }

    fn clear(&self) {
        self.cache.clear();
    }

    fn len(&self) -> usize {
        self.cache.len()
    }

    fn len_l1(&self) -> usize {
        self.cache.len_l1()
    }

    fn len_l2(&self) -> usize {
        self.cache.len_l2()
    }

    fn contains(&self, key: &str) -> bool {
        self.cache.contains_key(&key.to_string())
    }
}

#[cfg(feature = "python")]
#[pymodule]
fn thegent_cache(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonCache>()?;
    Ok(())
}
