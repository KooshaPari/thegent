//! # Queries (CQRS)
//!
//! Operations that read state without side effects.

/// Query to get a specific lock
#[derive(Debug, Clone)]
pub struct GetLockQuery {
    pub cmd_hash: String,
}

/// Query to list all locks
#[derive(Debug, Clone)]
pub struct ListLocksQuery {}

/// Query to get circuit breaker state
#[derive(Debug, Clone)]
pub struct GetBreakerQuery {
    pub target: String,
}

/// Query to list all circuit breakers
#[derive(Debug, Clone)]
pub struct ListBreakersQuery {}

/// Query to get health score
#[derive(Debug, Clone)]
pub struct GetHealthQuery {}

/// Query to get provider metrics
#[derive(Debug, Clone)]
pub struct GetProviderMetricsQuery {
    pub provider: String,
}

/// Query to list all providers
#[derive(Debug, Clone)]
pub struct ListProvidersQuery {}
