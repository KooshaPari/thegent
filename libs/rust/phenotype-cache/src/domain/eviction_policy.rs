//! Eviction policy - Pure domain type for cache eviction strategies.
//!
//! Pure domain type with no external dependencies.

use std::fmt;

/// Cache eviction policies.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvictionPolicy {
    /// Least Recently Used - evict least recently accessed items first
    LRU,
    /// Least Frequently Used - evict least frequently accessed items first
    LFU,
    /// First In First Out - evict oldest items first
    FIFO,
    /// First Recently Used - evict most recently accessed items first
    MRU,
    /// No eviction - items are never automatically evicted
    NoEviction,
    /// Random Replacement - evict random items
    Random,
}

impl Default for EvictionPolicy {
    fn default() -> Self {
        EvictionPolicy::LRU
    }
}

impl fmt::Display for EvictionPolicy {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EvictionPolicy::LRU => write!(f, "LRU"),
            EvictionPolicy::LFU => write!(f, "LFU"),
            EvictionPolicy::FIFO => write!(f, "FIFO"),
            EvictionPolicy::MRU => write!(f, "MRU"),
            EvictionPolicy::NoEviction => write!(f, "NoEviction"),
            EvictionPolicy::Random => write!(f, "Random"),
        }
    }
}

impl EvictionPolicy {
    /// Check if this policy requires tracking access time.
    pub fn tracks_access_time(&self) -> bool {
        matches!(self, EvictionPolicy::LRU | EvictionPolicy::MRU)
    }

    /// Check if this policy requires tracking access count.
    pub fn tracks_access_count(&self) -> bool {
        matches!(self, EvictionPolicy::LFU)
    }

    /// Check if this policy requires tracking creation time.
    pub fn tracks_creation_time(&self) -> bool {
        matches!(self, EvictionPolicy::FIFO)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_policy() {
        assert_eq!(EvictionPolicy::default(), EvictionPolicy::LRU);
    }

    #[test]
    fn test_policy_tracking() {
        assert!(EvictionPolicy::LRU.tracks_access_time());
        assert!(EvictionPolicy::LFU.tracks_access_count());
        assert!(EvictionPolicy::FIFO.tracks_creation_time());
        assert!(!EvictionPolicy::Random.tracks_access_time());
    }
}
