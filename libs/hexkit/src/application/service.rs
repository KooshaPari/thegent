//! Application Service - Orchestration Layer
//!
//! Application services coordinate domain objects and ports to accomplish
//! specific tasks. They are the entry points for use cases.
//!
//! ## Responsibilities
//!
//! - Coordinate domain objects
//! - Manage transactions
//! - Handle cross-cutting concerns
//! - Delegate to domain services
//!
//! ## Example
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::application::service::{ApplicationService, ServiceRegistry};
//!
//! #[derive(Debug, Clone)]
//! pub struct CreateOrderService;
//!
//! impl ApplicationService for CreateOrderService {
//!     fn service_name(&self) -> &'static str {
//!         "CreateOrder"
//!     }
//! }
//! ```
use crate::ports::inbound::InputPort;
use crate::HexResult;
use std::sync::Arc;

/// Marker trait for application services
pub trait ApplicationService: InputPort + Send + Sync {}

/// Trait for transaction management
pub trait TransactionManager: Send + Sync {
    async fn begin(&self) -> HexResult<Box<dyn Transaction>>;
    async fn commit(&self, transaction: Box<dyn Transaction>) -> HexResult<()>;
    async fn rollback(&self, transaction: Box<dyn Transaction>) -> HexResult<()>;
}

/// Transaction interface
pub trait Transaction: Send + Sync {
    fn id(&self) -> &str;
    fn is_active(&self) -> bool;
}

/// Unit of Work pattern for batching operations
pub trait UnitOfWork: Send + Sync {
    fn add<T: crate::domain::AggregateRoot + 'static>(&mut self, aggregate: T);
    fn commit(&mut self) -> impl std::future::Future<Output = HexResult<()>> + Send;
    fn rollback(&mut self) -> impl std::future::Future<Output = HexResult<()>> + Send;
}

/// Application service registry for dependency injection
pub struct ServiceRegistry {
    services: std::collections::HashMap<&'static str, Box<dyn std::any::Any + Send + Sync>>,
}

impl ServiceRegistry {
    pub fn new() -> Self {
        Self {
            services: Default::default(),
        }
    }

    pub fn register<T: Send + Sync + 'static>(&mut self, service: Arc<T>) {
        let key = std::any::type_name::<T>();
        self.services.insert(key, Box::new(service));
    }

    pub fn resolve<T: Send + Sync + 'static>(&self) -> Option<Arc<T>> {
        let key = std::any::type_name::<T>();
        self.services.get(key).and_then(|s| s.downcast_ref::<Arc<T>>().cloned())
    }
}

impl Default for ServiceRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_registry() {
        let mut registry = ServiceRegistry::new();
        let service = Arc::new(String::from("test"));
        registry.register(service.clone());

        let resolved = registry.resolve::<String>();
        assert!(resolved.is_some());
    }
}
