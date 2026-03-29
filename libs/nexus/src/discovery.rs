//! Service discovery module

use std::hash::{Hash, Hasher};
use crate::{Registry, Service, NexusError};

/// Discovery strategies for load balancing
#[derive(Debug, Clone)]
pub enum Strategy {
    /// Round-robin selection
    RoundRobin,
    /// Random selection
    Random,
    /// Consistent hash
    ConsistentHash,
}

/// Discovery for finding and selecting services
pub struct Discovery {
    registry: Registry,
    strategy: Strategy,
}

impl Discovery {
    /// Create a new discovery instance
    pub fn new(registry: Registry, strategy: Strategy) -> Self {
        Self { registry, strategy }
    }

    /// Find the next endpoint using the configured strategy
    pub async fn next(&self, name: &str) -> Result<Option<Service>, NexusError> {
        let services = self.registry.discover(name).await?;
        if services.is_empty() {
            return Ok(None);
        }

        match self.strategy {
            Strategy::RoundRobin => Ok(services.into_iter().next()),
            Strategy::Random => {
                use std::collections::hash_map::RandomState;
                use std::hash::BuildHasher;
                let mut hasher = RandomState::new().build_hasher();
                name.hash(&mut hasher);
                let idx = (hasher.finish() as usize) % services.len();
                Ok(services.into_iter().nth(idx))
            }
            Strategy::ConsistentHash => Ok(services.into_iter().next()),
        }
    }
}
