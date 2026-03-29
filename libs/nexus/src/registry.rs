//! Service registry module

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use crate::{Service, NexusError};

/// Service registry for managing service registrations
pub struct Registry {
    services: Arc<RwLock<HashMap<String, Vec<Service>>>>,
}

impl Registry {
    /// Create a new registry instance
    pub fn new() -> Self {
        Self {
            services: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Register a service
    pub async fn register(&self, service: Service) -> Result<(), NexusError> {
        let mut services = self.services.write().await;
        let entries = services.entry(service.name.clone()).or_insert_with(Vec::new);
        entries.push(service);
        Ok(())
    }

    /// Deregister a service by name and endpoint
    pub async fn deregister(&self, name: &str, endpoint: &str) -> Result<(), NexusError> {
        let mut services = self.services.write().await;
        if let Some(entries) = services.get_mut(name) {
            entries.retain(|s| s.endpoint.addr != endpoint);
        }
        Ok(())
    }

    /// Discover services by name
    pub async fn discover(&self, name: &str) -> Result<Vec<Service>, NexusError> {
        let services = self.services.read().await;
        Ok(services.get(name).cloned().unwrap_or_default())
    }
}

impl Default for Registry {
    fn default() -> Self {
        Self::new()
    }
}
