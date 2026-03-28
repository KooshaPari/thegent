//! Application Handlers
//! 
//! Handlers implement inbound ports and orchestrate the domain.

/// Marker trait for command handlers
pub trait CommandHandler<C, R>: Send + Sync {
    /// Handle a command
    fn handle(&self, command: C) -> R;
}

/// Marker trait for query handlers
pub trait QueryHandler<Q, R>: Send + Sync {
    /// Handle a query
    fn handle(&self, query: Q) -> R;
}
