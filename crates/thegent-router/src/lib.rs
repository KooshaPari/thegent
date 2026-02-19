//! Pareto routing engine with hysteresis for task distribution.
//!
//! This crate provides a risk-aware routing system that distributes tasks
//! between two execution modes (Lifecycle and TheGent) based on complexity,
//! cost, and dependencies. Hysteresis prevents oscillation.

pub mod risk;
pub mod router;
pub mod hysteresis;

#[cfg(feature = "python")]
pub mod python;

pub use risk::{RiskCalculator, ComplexityLevel, RiskFactors};
pub use router::{ParetoRouter, RoutingMode, RoutingDecision, RouterMetrics};
pub use hysteresis::HysteresisManager;

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
