//! Backward-compatible cache API backed by `phenotype_cache_adapter::TieredCache`.
//!
//! This crate delegates all caching logic to the shared `phenotype-cache-adapter`
//! crate, exposing the same public `Cache<K,V>` API that existing consumers expect.

use phenotype_cache_adapter::TieredCache;
use std::hash::Hash;
use std::time::Duration;

/// Two-tier cache with L1 (LRU) for hot data and L2 (DashMap) for warm data.
///
/// Thin wrapper around [`phenotype_cache_adapter::TieredCache`] that preserves
/// the original `Cache<K,V>` method signatures (`set`, `set_with_ttl`, `len`, etc.).
pub struct Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    inner: TieredCache<K, V>,
}

impl<K, V> Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    pub fn new(ttl_seconds: u64) -> Self {
        Self::with_capacity_and_ttl(1000, Duration::from_secs(ttl_seconds))
    }

    pub fn with_capacity_and_ttl(l1_capacity: usize, default_ttl: Duration) -> Self {
        Self {
            inner: TieredCache::new(l1_capacity, default_ttl),
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        self.inner.get(key)
    }

    pub fn set(&self, key: K, value: V) {
        self.inner.insert(key, value);
    }

    pub fn set_with_ttl(&self, key: K, value: V, ttl: Duration) {
        self.inner.insert_with_ttl(key, value, ttl);
    }

    pub fn remove(&self, key: &K) {
        self.inner.remove(key);
    }

    pub fn clear(&self) {
        self.inner.clear();
    }

    pub fn len(&self) -> usize {
        self.inner.l1_len() + self.inner.l2_len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn len_l1(&self) -> usize {
        self.inner.l1_len()
    }

    pub fn len_l2(&self) -> usize {
        self.inner.l2_len()
    }

    pub fn contains_key(&self, key: &K) -> bool {
        self.inner.contains_key(key)
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
        let cache = Cache::new(3600);
        cache.set("key1".to_string(), "value1".to_string());
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));
    }

    #[test]
    fn test_cache_expiration() {
        let cache = Cache::with_capacity_and_ttl(100, Duration::from_secs(1));
        cache.set("key1".to_string(), "value1".to_string());
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));
        std::thread::sleep(Duration::from_secs(2));
        assert_eq!(cache.get(&"key1".to_string()), None);
    }

    #[test]
    fn test_l1_l2_tier() {
        let cache = Cache::with_capacity_and_ttl(2, Duration::from_secs(60));
        cache.set("key1".to_string(), "value1".to_string());
        cache.set("key2".to_string(), "value2".to_string());
        cache.set("key3".to_string(), "value3".to_string());

        // key1 should be evicted from L1 but still in L2
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));

        // All should be in L2
        assert!(cache.len_l2() >= 3);
    }
}

#[cfg(all(feature = "python", not(test)))]
use pyo3::prelude::*;
#[cfg(all(feature = "python", not(test)))]
use pyo3::types::PyModule;

#[cfg(all(feature = "python", not(test)))]
#[pyclass]
struct PythonCache {
    cache: Cache<String, String>,
}

#[cfg(all(feature = "python", not(test)))]
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

#[cfg(all(feature = "python", not(test)))]
#[pymodule]
fn thegent_cache(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonCache>()?;
    Ok(())
}
