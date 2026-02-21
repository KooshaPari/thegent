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

pub mod risk;
pub mod router;
pub mod hysteresis;
pub mod audit;
pub mod executor;
pub mod orchestrator;

#[cfg(feature = "python")]
pub mod python;

pub use risk::{RiskCalculator, ComplexityLevel, RiskFactors};
pub use router::{ParetoRouter, RoutingMode, RoutingDecision, RouterMetrics, RouterConfig};
pub use hysteresis::HysteresisManager;
pub use audit::{AuditLogger, AuditRecord};
pub use executor::{RouteExecutor, ExecutionOutcome, DispatchTarget, Dispatcher};
pub use orchestrator::{RoutingOrchestrator, RouterStatus, AgentRoutingState, ArbitrationPolicy};

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
