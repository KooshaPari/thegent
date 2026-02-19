//! Integration tests for router with hysteresis.

use thegent_router::{ParetoRouter, RiskFactors, ComplexityLevel, RoutingMode};

#[test]
fn test_router_with_hysteresis_single_session() {
    let router = ParetoRouter::new();
    let session_id = "test-session-1";
    
    // Route simple task
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let decision1 = router.route_with_session(session_id, &simple);
    assert_eq!(decision1.mode, RoutingMode::Lifecycle);
    
    // Route another simple task - should stay in Lifecycle
    let decision2 = router.route_with_session(session_id, &simple);
    assert_eq!(decision2.mode, RoutingMode::Lifecycle);
    
    let metrics = router.get_metrics();
    assert_eq!(metrics.hysteresis_activations, 0); // No switches
}

#[test]
fn test_router_with_hysteresis_mode_switch() {
    let router = ParetoRouter::new();
    let session_id = "test-session-2";
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let very_complex = RiskFactors {
        complexity: ComplexityLevel::VeryComplex,
        cost_cents: 8_000,
        dependency_count: 8,
        security_sensitive: true,
        max_cost_cents: 10_000,
    };
    
    // Route simple task
    let decision1 = router.route_with_session(session_id, &simple);
    assert_eq!(decision1.mode, RoutingMode::Lifecycle);
    
    // Route very complex task - should switch
    let decision2 = router.route_with_session(session_id, &very_complex);
    assert_eq!(decision2.mode, RoutingMode::TheGent);
    
    // Track hysteresis activation
    let metrics = router.get_metrics();
    assert!(metrics.hysteresis_activations > 0);
}

#[test]
fn test_router_multi_session_isolation() {
    let router = ParetoRouter::new();
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let moderate = RiskFactors {
        complexity: ComplexityLevel::Moderate,
        cost_cents: 5_000,
        dependency_count: 5,
        security_sensitive: false,
        max_cost_cents: 10_000,
    };
    
    // Session 1: route simple
    let decision1 = router.route_with_session("session-1", &simple);
    assert_eq!(decision1.mode, RoutingMode::Lifecycle);
    
    // Session 2: route moderate (may switch or stay depending on thresholds)
    let _decision2 = router.route_with_session("session-2", &moderate);
    
    // Session 1: route moderate again - should maintain session state
    let _decision3 = router.route_with_session("session-1", &moderate);
    
    // Both sessions should have independent state
    let metrics = router.get_metrics();
    assert_eq!(metrics.total_decisions, 3);
}

#[test]
fn test_router_hysteresis_prevents_rapid_switching() {
    let router = ParetoRouter::new();
    let session_id = "test-session-3";
    
    // Create tasks that oscillate around threshold
    let mut tasks = Vec::new();
    for i in 0..10 {
        let cost = 3000 + (i % 2) * 2000; // Oscillate: 3000, 5000, 3000, 5000...
        tasks.push(RiskFactors {
            complexity: ComplexityLevel::Moderate,
            cost_cents: cost,
            dependency_count: (3 + (i % 3)) as usize,
            security_sensitive: i % 2 == 0,
            max_cost_cents: 10_000,
        });
    }
    
    let mut switch_count = 0;
    let mut last_mode = None;
    
    for task in &tasks {
        let decision = router.route_with_session(session_id, task);
        if let Some(prev_mode) = last_mode {
            if prev_mode != decision.mode {
                switch_count += 1;
            }
        }
        last_mode = Some(decision.mode);
    }
    
    // Should have limited switches due to hysteresis
    assert!(switch_count < 5); // Expect fewer than 5 switches
}

#[test]
fn test_router_lifecycle_percentage_with_hysteresis() {
    let router = ParetoRouter::new();
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    
    // Route 100 simple tasks
    for i in 0..100 {
        router.route_with_session(&format!("session-{}", i), &simple);
    }
    
    let percentage = router.lifecycle_percentage();
    // Should be 100% for all simple tasks
    assert!(percentage > 99.0 && percentage <= 100.0);
}

#[test]
fn test_router_metrics_tracking_with_hysteresis() {
    let router = ParetoRouter::new();
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let very_complex = RiskFactors {
        complexity: ComplexityLevel::VeryComplex,
        cost_cents: 8_000,
        dependency_count: 8,
        security_sensitive: true,
        max_cost_cents: 10_000,
    };
    
    // Route some tasks
    router.route_with_session("s1", &simple);
    router.route_with_session("s2", &very_complex);
    router.route_with_session("s3", &simple);
    
    let metrics = router.get_metrics();
    assert_eq!(metrics.total_decisions, 3);
    assert_eq!(metrics.lifecycle_count, 2);
    assert_eq!(metrics.thegent_count, 1);
}

#[test]
fn test_router_hysteresis_band_prevents_middle_oscillation() {
    let router = ParetoRouter::new();
    let session_id = "test-session-band";
    
    // Create a task with risk right in the middle (between thresholds)
    let middle = RiskFactors {
        complexity: ComplexityLevel::Moderate,
        cost_cents: 5_000,
        dependency_count: 5,
        security_sensitive: false,
        max_cost_cents: 10_000,
    };
    
    // Route multiple times - should not oscillate
    let mut modes = Vec::new();
    for _ in 0..5 {
        let decision = router.route_with_session(session_id, &middle);
        modes.push(decision.mode);
    }
    
    // All modes should be the same (no oscillation in middle band)
    let first_mode = modes[0];
    for mode in modes {
        assert_eq!(mode, first_mode);
    }
}

#[test]
fn test_router_independent_session_metrics() {
    let router = ParetoRouter::new();
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    
    // Route through different sessions
    for i in 0..10 {
        let session_id = format!("isolated-session-{}", i);
        router.route_with_session(&session_id, &simple);
    }
    
    let metrics = router.get_metrics();
    assert_eq!(metrics.total_decisions, 10);
    assert_eq!(metrics.lifecycle_count, 10);
    assert_eq!(metrics.route_changes, 0); // All decisions independent
}

#[test]
fn test_router_rationale_includes_hysteresis_info() {
    let router = ParetoRouter::new();
    let session_id = "test-rationale";
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let decision = router.route_with_session(session_id, &simple);
    
    // Rationale should include hysteresis information
    assert!(
        decision.rationale.contains("Lifecycle") 
        || decision.rationale.contains("hysteresis")
    );
}

#[test]
fn test_router_80_20_split_target_with_hysteresis() {
    let router = ParetoRouter::new();
    
    let simple = RiskFactors::new(ComplexityLevel::Simple);
    let complex = RiskFactors {
        complexity: ComplexityLevel::VeryComplex,
        cost_cents: 8_000,
        dependency_count: 8,
        security_sensitive: true,
        max_cost_cents: 10_000,
    };
    
    // Route 1000 tasks: 800 simple (Lifecycle), 200 complex (TheGent)
    for i in 0..1000 {
        let session_id = format!("session-{}", i);
        if i < 800 {
            router.route_with_session(&session_id, &simple);
        } else {
            router.route_with_session(&session_id, &complex);
        }
    }
    
    let metrics = router.get_metrics();
    let lifecycle_pct = (metrics.lifecycle_count as f64 / metrics.total_decisions as f64) * 100.0;
    
    // Should be close to 80%
    assert!(lifecycle_pct > 75.0 && lifecycle_pct < 85.0);
}
