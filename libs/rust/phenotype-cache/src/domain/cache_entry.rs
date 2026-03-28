//! Cache entry - Pure domain type for cached values.
//!
//! Pure domain type with no external dependencies.

use std::fmt;
use chrono::{DateTime, Utc};

/// Cache entry containing value and metadata.
#[derive(Debug, Clone)]
pub struct CacheEntry<V> {
    /// The cached value
    value: V,
    /// When the entry was created
    created_at: DateTime<Utc>,
    /// When the entry was last accessed
    accessed_at: DateTime<Utc>,
    /// Number of times accessed
    access_count: u64,
    /// Time-to-live in seconds (None = no expiration)
    ttl_seconds: Option<u64>,
}

impl<V> CacheEntry<V> {
    /// Create a new cache entry.
    pub fn new(value: V) -> Self {
        let now = Utc::now();
        Self {
            value,
            created_at: now,
            accessed_at: now,
            access_count: 0,
            ttl_seconds: None,
        }
    }

    /// Create a new cache entry with TTL.
    pub fn with_ttl(value: V, ttl_seconds: u64) -> Self {
        Self::new(value).with_ttl(ttl_seconds)
    }

    /// Set the TTL for this entry.
    pub fn with_ttl(mut self, ttl_seconds: u64) -> Self {
        self.ttl_seconds = Some(ttl_seconds);
        self
    }

    /// Get the cached value.
    pub fn value(&self) -> &V {
        &self.value
    }

    /// Get a mutable reference to the cached value.
    pub fn value_mut(&mut self) -> &mut V {
        &mut self.value
    }

    /// Get the creation timestamp.
    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }

    /// Get the last access timestamp.
    pub fn accessed_at(&self) -> DateTime<Utc> {
        self.accessed_at
    }

    /// Get the access count.
    pub fn access_count(&self) -> u64 {
        self.access_count
    }

    /// Get the TTL in seconds.
    pub fn ttl_seconds(&self) -> Option<u64> {
        self.ttl_seconds
    }

    /// Check if the entry has expired.
    pub fn is_expired(&self) -> bool {
        if let Some(ttl) = self.ttl_seconds {
            let elapsed = Utc::now()
                .signed_duration_since(self.accessed_at)
                .num_seconds();
            elapsed >= ttl as i64
        } else {
            false
        }
    }

    /// Record an access to this entry.
    pub fn touch(&mut self) {
        self.accessed_at = Utc::now();
        self.access_count += 1;
    }

    /// Get the remaining TTL in seconds.
    pub fn remaining_ttl(&self) -> Option<i64> {
        if let Some(ttl) = self.ttl_seconds {
            let elapsed = Utc::now()
                .signed_duration_since(self.accessed_at)
                .num_seconds();
            Some((ttl as i64) - elapsed)
        } else {
            None
        }
    }
}

impl<V: fmt::Debug> fmt::Display for CacheEntry<V> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CacheEntry")
            .field("value", &"...")
            .field("created_at", &self.created_at)
            .field("accessed_at", &self.accessed_at)
            .field("access_count", &self.access_count)
            .field("ttl_seconds", &self.ttl_seconds)
            .field("is_expired", &self.is_expired())
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_entry_creation() {
        let entry = CacheEntry::new("value");
        assert_eq!(entry.value(), &"value");
        assert_eq!(entry.access_count(), 0);
        assert!(!entry.is_expired());
    }

    #[test]
    fn test_cache_entry_with_ttl() {
        let entry = CacheEntry::new("value").with_ttl(3600);
        assert_eq!(entry.ttl_seconds(), Some(3600));
        assert!(!entry.is_expired());
    }

    #[test]
    fn test_cache_entry_touch() {
        let mut entry = CacheEntry::new("value");
        entry.touch();
        assert_eq!(entry.access_count(), 1);
    }
}
