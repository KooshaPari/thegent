//! Two-tier cache with L1 (LRU) for hot data and L2 (DashMap) for warm data.

use lru::LruCache;
use dashmap::DashMap;
use std::hash::Hash;
use std::time::{Duration, Instant};
use std::num::NonZeroUsize;
use parking_lot::Mutex;

/// Two-tier cache with L1 (LRU) for hot data and L2 (DashMap) for warm data.
pub struct Cache<K, V>
where
    K: Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    l1: Mutex<LruCache<K, (V, Instant)>>,
    l2: DashMap<K, (V, Instant)>,
    default_ttl: Duration,
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
            l1: Mutex::new(LruCache::new(NonZeroUsize::new(l1_capacity).unwrap())),
            l2: DashMap::new(),
            default_ttl,
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        let now = Instant::now();
        // Check L1
        if let Some(entry) = self.l1.lock().get(key) {
            if entry.1 + self.default_ttl > now {
                return Some(entry.0.clone());
            }
        }
        // Check L2
        if let Some(entry) = self.l2.get(key) {
            if entry.1 + self.default_ttl > now {
                return Some(entry.0.clone());
            }
            self.l2.remove(key);
        }
        None
    }

    pub fn set(&self, key: K, value: V) {
        let now = Instant::now();
        self.l1.lock().put(key.clone(), (value.clone(), now));
        self.l2.insert(key, (value, now));
    }

    pub fn set_with_ttl(&self, key: K, value: V, ttl: Duration) {
        let expiry = Instant::now() + ttl;
        self.l1.lock().put(key.clone(), (value.clone(), expiry));
        self.l2.insert(key, (value, expiry));
    }

    pub fn remove(&self, key: &K) {
        self.l1.lock().pop(key);
        self.l2.remove(key);
    }

    pub fn clear(&self) {
        self.l1.lock().clear();
        self.l2.clear();
    }

    pub fn len(&self) -> usize {
        self.l1.lock().len() + self.l2.len()
    }

    pub fn is_empty(&self) -> bool {
        self.l1.lock().is_empty() && self.l2.is_empty()
    }

    pub fn len_l1(&self) -> usize {
        self.l1.lock().len()
    }

    pub fn len_l2(&self) -> usize {
        self.l2.len()
    }

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
        let cache: Cache<String, String> = Cache::with_capacity_and_ttl(100, Duration::from_secs(1));
        cache.set("key1".to_string(), "value1".to_string());
        assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));
        std::thread::sleep(Duration::from_secs(2));
        assert_eq!(cache.get(&"key1".to_string()), None);
    }

    #[test]
    fn test_l1_l2_tier() {
        let cache: Cache<String, String> = Cache::with_capacity_and_ttl(2, Duration::from_secs(60));
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
