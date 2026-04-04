//! Integration tests for hysteresis manager with FR traceability.
//!
//! Traces to:
//! - FR-THEGENT-001: Hysteresis band prevents oscillation
//! - FR-THEGENT-002: Max dwell forces reevaluation
//! - FR-THEGENT-003: Routing mode switching logic

use std::time::{Duration, Instant};
use thegent_router::HysteresisManager;
use thegent_router::RoutingMode;

/// Test hysteresis band prevents oscillation.
/// Traces to: FR-THEGENT-001
#[trace_to("FR-THEGENT-001")]
#[test]
fn test_hysteresis_band_prevents_oscillation() {
    let hyst = HysteresisManager::new();
    let now = Instant::now();
    let threshold = 0.5;

    // Simulate task near threshold oscillating within dwell period
    let can_switch_1 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.51,
        threshold,
        now,
        0.50,
    );
    assert!(!can_switch_1);

    let can_switch_2 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.49,
        threshold,
        now,
        0.51,
    );
    assert!(!can_switch_2);
}

/// Test max dwell forces reevaluation.
/// Traces to: FR-THEGENT-002
#[trace_to("FR-THEGENT-002")]
#[test]
fn test_hysteresis_max_dwell_forces_reevaluation() {
    let hyst = HysteresisManager::new();
    let past = Instant::now() - Duration::from_secs(2000);

    let can_switch = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.4,
        0.5,
        past,
        0.6,
    );
    assert!(can_switch);
}

/// Test routing mode switching with hysteresis.
/// Traces to: FR-THEGENT-003
#[trace_to("FR-THEGENT-003")]
#[test]
fn test_routing_mode_switching() {
    let hyst = HysteresisManager::new();
    let now = Instant::now();
    
    let should_switch = hyst.should_switch(
        RoutingMode::Immediate,
        0.8,
        0.5,
        now,
        0.3,
    );
    assert!(should_switch);
}
