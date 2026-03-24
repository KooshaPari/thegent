use dashmap::DashMap;
use lru::LruCache;
use serde::{Deserialize, Serialize};
use std::num::NonZeroUsize;
use std::sync::{Arc, RwLock};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct CacheEntry<T> {
    value: T,
    expires_at: u64,
    created_at: u64,
    access_count: u64,
}

impl<T> CacheEntry<T> {
    fn new(value: T, ttl: Duration) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        Self {
            value,
            expires_at: now + ttl.as_secs(),
            created_at: now,
            access_count: 0,
        }
    }

    fn is_expired(&self) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now >= self.expires_at
    }
}

/// Two-tier cache with L1 (LRU) for hot data and L2 (DashMap) for warm data
pub struct Cache<K, V>
where
    K: std::hash::Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    l1: Arc<RwLock<LruCache<K, CacheEntry<V>>>>,
    l2: Arc<DashMap<K, CacheEntry<V>>>,
    default_ttl: Duration,
}

impl<K, V> Cache<K, V>
where
    K: std::hash::Hash + Eq + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
{
    pub fn new(ttl_seconds: u64) -> Self {
        Self::with_capacity_and_ttl(1000, Duration::from_secs(ttl_seconds))
    }

    pub fn with_capacity_and_ttl(l1_capacity: usize, default_ttl: Duration) -> Self {
        Self {
            l1: Arc::new(RwLock::new(LruCache::new(
                NonZeroUsize::new(l1_capacity.max(1)).unwrap(),
            ))),
            l2: Arc::new(DashMap::new()),
            default_ttl,
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        // Try L1 first (hottest data)
        {
            let mut l1 = self.l1.write().unwrap();
            if let Some(entry) = l1.get_mut(key) {
                if !entry.is_expired() {
                    entry.access_count += 1;
                    return Some(entry.value.clone());
                } else {
                    l1.pop(key);
                }
            }
        }

        // Try L2 (warm data) - clone entry first to avoid borrow conflicts
        if let Some(entry_ref) = self.l2.get(key) {
            if !entry_ref.is_expired() {
                // Clone the entire entry first
                let entry_cloned = (*entry_ref).clone();

                // Promote to L1 using the cloned entry
                {
                    let mut l1 = self.l1.write().unwrap();
                    l1.put(key.clone(), entry_cloned.clone());
                }
                // Return the value from cloned entry
                return Some(entry_cloned.value);
            }
        }

        None
    }

    pub fn set(&self, key: K, value: V) {
        self.set_with_ttl(key, value, self.default_ttl);
    }

    pub fn set_with_ttl(&self, key: K, value: V, ttl: Duration) {
        let entry = CacheEntry::new(value.clone(), ttl);
        let entry_for_l2 = CacheEntry::new(value, ttl);

        // Insert into L1
        {
            let mut l1 = self.l1.write().unwrap();
            l1.put(key.clone(), entry);
        }

        // Also store in L2
        self.l2.insert(key, entry_for_l2);
    }

    pub fn remove(&self, key: &K) {
        let mut l1 = self.l1.write().unwrap();
        l1.pop(key);
        self.l2.remove(key);
    }

    pub fn clear(&self) {
        let mut l1 = self.l1.write().unwrap();
        l1.clear();
        self.l2.clear();
    }

    pub fn len(&self) -> usize {
        let l1_len = self.l1.read().unwrap().len();
        let l2_len = self.l2.len();
        l1_len + l2_len
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn len_l1(&self) -> usize {
        self.l1.read().unwrap().len()
    }

    pub fn len_l2(&self) -> usize {
        self.l2.len()
    }

    pub fn contains_key(&self, key: &K) -> bool {
        {
            let l1 = self.l1.read().unwrap();
            if l1.contains(key) {
                return true;
            }
        }
        self.l2.contains_key(key)
    }
}

impl<K, V> Default for Cache<K, V>
where
    K: std::hash::Hash + Eq + Clone + Send + Sync + 'static,
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

        // key1 should be evicted from L1
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
