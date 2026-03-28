//! Input Ports - How external systems drive the domain
//!
//! Input ports define the entry points into the application.
//! They are typically implemented by application services.

use crate::HexagonalResult;

/// Marker trait for input ports (driving ports)
pub trait InputPort: Send + Sync {}

/// Command handler trait
pub trait CommandHandler<C, R>: Send + Sync {
    fn handle(&self, command: C) -> R;
}

/// Query handler trait
pub trait QueryHandler<Q, R>: Send + Sync {
    fn handle(&self, query: Q) -> R;
}

/// Use case marker for input ports
pub trait UseCase<I, O>: InputPort {
    fn execute(&self, input: I) -> HexagonalResult<O>;
}

/// Saga orchestrator for distributed transactions
pub trait SagaOrchestrator<S, E>: Send + Sync {
    fn start(&self, saga: S) -> HexagonalResult<String>;
    fn handle_event(&self, correlation_id: &str, event: E) -> HexagonalResult<()>;
    fn compensate(&self, correlation_id: &str) -> HexagonalResult<()>;
}
