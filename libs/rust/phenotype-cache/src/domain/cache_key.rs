//! Cache key - Pure domain type for cache key identification.
//!
//! Pure domain type with no external dependencies.

use std::fmt;
use std::hash::{Hash, Hasher};
use std::borrow::Cow;

/// Cache key - a type-safe wrapper around string keys.
///
/// Ensures consistent key formatting and prevents typos.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CacheKey(Cow<'static, str>);

impl CacheKey {
    /// Create a new cache key from a string.
    pub fn new<S: Into<Cow<'static, str>>>(key: S) -> Self {
        Self(key.into())
    }

    /// Create a cache key for a namespace and id.
    ///
    /// Example: `CacheKey::from_parts("users", "123")` -> "users:123"
    pub fn from_parts(namespace: &str, id: &str) -> Self {
        Self(format!("{}:{}", namespace, id).into())
    }

    /// Get the string representation.
    pub fn as_str(&self) -> &str {
        &self.0
    }

    /// Get the namespace portion of the key.
    pub fn namespace(&self) -> Option<&str> {
        self.0.split(':').next()
    }

    /// Get the id portion of the key.
    pub fn id(&self) -> Option<&str> {
        let parts: Vec<&str> = self.0.split(':').collect();
        if parts.len() > 1 {
            Some(parts[1])
        } else {
            None
        }
    }
}

impl<T> From<T> for CacheKey
where
    T: Into<String>,
{
    fn from(key: T) -> Self {
        Self(key.into().into())
    }
}

impl AsRef<str> for CacheKey {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for CacheKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl Default for CacheKey {
    fn default() -> Self {
        Self("default".into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_key_creation() {
        let key = CacheKey::new("test-key");
        assert_eq!(key.as_str(), "test-key");
    }

    #[test]
    fn test_cache_key_from_parts() {
        let key = CacheKey::from_parts("users", "123");
        assert_eq!(key.as_str(), "users:123");
        assert_eq!(key.namespace(), Some("users"));
        assert_eq!(key.id(), Some("123"));
    }

    #[test]
    fn test_cache_key_equality() {
        let key1 = CacheKey::new("test");
        let key2 = CacheKey::new("test");
        assert_eq!(key1, key2);
    }

    #[test]
    fn test_cache_key_hash() {
        use std::collections::HashMap;
        let mut map = HashMap::new();
        let key = CacheKey::new("test");
        map.insert(key.clone(), "value");
        assert_eq!(map.get(&key), Some(&"value"));
    }
}
