//! Inbound ports - Primary/driving ports (use cases)

#[cfg(feature = "async")]
use async_trait::async_trait;
use std::sync::Arc;

/// Marker trait for inbound ports
pub trait InboundPort: Send + Sync {}

/// Marker trait for use cases
pub trait UseCase: Send + Sync {
    /// The input type for the use case
    type Input: Send + Sync;
    /// The output type for the use case
    type Output: Send + Sync;
    /// The error type for the use case
    type Error: Send + Sync;
}

/// Marker trait for command handlers
pub trait CommandHandler: Send + Sync {
    /// The command type
    type Command: Send + Sync;
    /// The result type
    type Result: Send + Sync;
}

/// Marker trait for query handlers
pub trait QueryHandler: Send + Sync {
    /// The query type
    type Query: Send + Sync;
    /// The result type
    type Result: Send + Sync;
}

/// Marker trait for event handlers
pub trait EventHandler: Send + Sync {
    /// The event type
    type Event: Send + Sync;
}

/// Service trait for application services
#[cfg(feature = "async")]
#[async_trait]
pub trait ApplicationService: Send + Sync {
    /// Initialize the service
    async fn init(&self) -> impl std::future::Future<Output = ()> + Send {
        async {}
    }

    /// Shutdown the service gracefully
    async fn shutdown(&self) -> impl std::future::Future<Output = ()> + Send {
        async {}
    }
}

/// Decorator trait for adding cross-cutting concerns
pub trait Decorated<T: UseCase>: UseCase {
    /// Returns the inner decorated use case
    fn inner(&self) -> Arc<T>;
}
