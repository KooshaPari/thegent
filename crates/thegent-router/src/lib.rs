//! Pareto routing engine with hysteresis for task distribution.
//!
//! This crate provides a risk-aware routing system that distributes tasks
//! between two execution modes (Lifecycle and TheGent) based on complexity,
//! cost, and dependencies. Hysteresis prevents oscillation.
//!
//! Phase 3 adds:
//! - `audit`: SHA-256 hash-chained audit log (ADR-015 pattern)
//! - `executor`: RouteExecutor dispatches RoutingDecisions to providers
//! - `orchestrator`: RoutingOrchestrator coordinates N concurrent agents

pub mod audit;
pub mod executor;
pub mod hysteresis;
pub mod orchestrator;
pub mod risk;
pub mod router;

#[cfg(feature = "python")]
pub mod python;

pub use audit::{AuditLogger, AuditRecord};
pub use executor::{DispatchTarget, Dispatcher, ExecutionOutcome, RouteExecutor};
pub use hysteresis::HysteresisManager;
pub use orchestrator::{AgentRoutingState, ArbitrationPolicy, RouterStatus, RoutingOrchestrator};
pub use risk::{ComplexityLevel, RiskCalculator, RiskFactors};
pub use router::{ParetoRouter, RouterConfig, RouterMetrics, RoutingDecision, RoutingMode};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_routing_mode_lifecycle() {
        assert_eq!(RoutingMode::Lifecycle, RoutingMode::Lifecycle);
    }

    #[test]
    fn test_routing_mode_thegent() {
        assert_eq!(RoutingMode::TheGent, RoutingMode::TheGent);
    }
}
