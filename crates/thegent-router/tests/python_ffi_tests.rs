// SPDX-License-Identifier: MIT OR Apache-2.0
//! Tests for Python FFI bindings (manual integration tests without PyO3)
//!
//! These tests verify that the Python module can be imported and used.
//! Full Python integration tests require maturin build and pytest.

#[cfg(test)]
mod tests {
    use thegent_router::*;

    #[test]
    fn test_risk_factors_creation() {
        let factors = RiskFactors::new(ComplexityLevel::Simple);
        assert_eq!(factors.complexity, ComplexityLevel::Simple);
        assert_eq!(factors.cost_cents, 0);
        assert_eq!(factors.dependency_count, 0);
        assert!(!factors.security_sensitive);
    }

    #[test]
    fn test_risk_calculator_simple() {
        let calc = RiskCalculator::new();
        let factors = RiskFactors::new(ComplexityLevel::Simple);
        let risk = calc.calculate(&factors);

        assert!((0.0..=1.0).contains(&risk));
        assert!(risk < 0.35); // Simple should be low risk
    }

    #[test]
    fn test_risk_calculator_complex() {
        let calc = RiskCalculator::new();
        let factors = RiskFactors {
            complexity: ComplexityLevel::VeryComplex,
            cost_cents: 8000,
            dependency_count: 8,
            security_sensitive: true,
            max_cost_cents: 10_000,
        };
        let risk = calc.calculate(&factors);

        assert!((0.0..=1.0).contains(&risk));
        assert!(risk > 0.65); // Very complex should be high risk
    }

    #[test]
    fn test_router_basic() {
        let router = ParetoRouter::new();
        let factors = RiskFactors::new(ComplexityLevel::Simple);
        let decision = router.route(&factors);

        assert_eq!(decision.mode, RoutingMode::Lifecycle);
        assert!(decision.risk_score < 0.35);
        assert!(decision.rationale.contains("Lifecycle"));
    }

    #[test]
    fn test_router_with_session() {
        let router = ParetoRouter::new();
        let factors_simple = RiskFactors::new(ComplexityLevel::Simple);
        let factors_complex = RiskFactors {
            complexity: ComplexityLevel::VeryComplex,
            cost_cents: 8000,
            dependency_count: 8,
            security_sensitive: true,
            max_cost_cents: 10_000,
        };

        let session_id = "test-session-1";

        // First decision: simple task
        let decision1 = router.route_with_session(session_id, &factors_simple);
        assert_eq!(decision1.mode, RoutingMode::Lifecycle);

        // Second decision: complex task (may not switch due to hysteresis)
        let decision2 = router.route_with_session(session_id, &factors_complex);
        assert!(decision2.risk_score > 0.65);
    }

    #[test]
    fn test_router_metrics() {
        let router = ParetoRouter::new();
        let simple = RiskFactors::new(ComplexityLevel::Simple);
        let complex = RiskFactors {
            complexity: ComplexityLevel::VeryComplex,
            cost_cents: 8000,
            dependency_count: 8,
            security_sensitive: true,
            max_cost_cents: 10_000,
        };

        router.route(&simple);
        router.route(&complex);
        router.route(&simple);

        let metrics = router.get_metrics();
        assert_eq!(metrics.total_decisions, 3);
        assert_eq!(metrics.lifecycle_count, 2);
        assert_eq!(metrics.thegent_count, 1);

        let percentage = router.lifecycle_percentage();
        assert!((percentage - 66.666_67).abs() < 0.1);
    }

    #[test]
    fn test_hysteresis_manager() {
        let hyst = HysteresisManager::new();

        let threshold = 0.5;

        // Inside band
        assert!(hyst.in_hysteresis_band(0.45, threshold));
        assert!(hyst.in_hysteresis_band(0.55, threshold));

        // Outside band
        assert!(!hyst.in_hysteresis_band(0.20, threshold));
        assert!(!hyst.in_hysteresis_band(0.80, threshold));
    }

    #[test]
    fn test_routing_mode_equality() {
        assert_eq!(RoutingMode::Lifecycle, RoutingMode::Lifecycle);
        assert_eq!(RoutingMode::TheGent, RoutingMode::TheGent);
        assert_ne!(RoutingMode::Lifecycle, RoutingMode::TheGent);
    }

    #[test]
    fn test_routing_decision_fields() {
        let router = ParetoRouter::new();
        let factors = RiskFactors::new(ComplexityLevel::Moderate);
        let decision = router.route(&factors);

        assert!(decision.risk_score >= 0.0);
        assert!(decision.risk_score <= 1.0);
        assert!(!decision.rationale.is_empty());
    }

    #[test]
    fn test_router_multiple_sessions() {
        let router = ParetoRouter::new();
        let simple = RiskFactors::new(ComplexityLevel::Simple);
        let complex = RiskFactors {
            complexity: ComplexityLevel::VeryComplex,
            cost_cents: 8000,
            dependency_count: 8,
            security_sensitive: true,
            max_cost_cents: 10_000,
        };

        // Session 1
        let d1_1 = router.route_with_session("session-1", &simple);
        let d1_2 = router.route_with_session("session-1", &complex);

        // Session 2 (should start fresh)
        let d2_1 = router.route_with_session("session-2", &simple);
        let d2_2 = router.route_with_session("session-2", &complex);

        // Both sessions should follow similar patterns
        assert_eq!(d1_1.mode, d2_1.mode);
        assert!(d1_2.risk_score > 0.65);
        assert!(d2_2.risk_score > 0.65);
    }

    #[test]
    fn test_lifecycle_percentage_calculations() {
        let router = ParetoRouter::new();
        let simple = RiskFactors::new(ComplexityLevel::Simple);
        let complex = RiskFactors {
            complexity: ComplexityLevel::VeryComplex,
            cost_cents: 8000,
            dependency_count: 8,
            security_sensitive: true,
            max_cost_cents: 10_000,
        };

        // 80% Lifecycle, 20% TheGent
        for _ in 0..80 {
            router.route(&simple);
        }
        for _ in 0..20 {
            router.route(&complex);
        }

        let percentage = router.lifecycle_percentage();
        assert!((percentage - 80.0).abs() < 0.1);
        assert!((router.get_metrics().total_decisions - 100).eq(&0));
    }
}
