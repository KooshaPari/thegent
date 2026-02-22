//! Integration tests for hysteresis manager.

use thegent_router::HysteresisManager;
use thegent_router::RoutingMode;
use std::time::{Duration, Instant};

#[test]
fn test_hysteresis_band_prevents_oscillation() {
    let hyst = HysteresisManager::new();
    let now = Instant::now();
    let threshold = 0.5;

    // Simulate task near threshold oscillating within dwell period
    // First call: small movement within band from previous 0.5
    let can_switch_1 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.51,     // Slight movement (within band [0.35, 0.65])
        threshold,
        now,
        0.50,     // Small change from previous
    );
    assert!(!can_switch_1); // In band + dwell active prevents switch

    // After some time in dwell (but not small movement), still prevented
    let can_switch_2 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.49,     // Back within band
        threshold,
        now,      // Still in dwell (same time)
        0.51,     // Small oscillation
    );
    assert!(!can_switch_2); // In band + dwell prevents oscillation
}

#[test]
fn test_hysteresis_max_dwell_forces_reevaluation() {
    let hyst = HysteresisManager::new();
    let past = Instant::now() - Duration::from_secs(2000); // > max_dwell (1800s)

    // In hysteresis band but max dwell expired
    let can_switch = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.50,     // Inside band
        0.5,
        past,
        0.505,
    );
    assert!(can_switch); // Force re-evaluation
}

#[test]
fn test_hysteresis_large_risk_change_overrides_dwell() {
    let hyst = HysteresisManager::new();
    let now = Instant::now();

    // In band, dwell active, but large risk change
    let can_switch = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.50,     // Inside band
        0.5,
        now,      // Just switched, dwell active
        0.25,     // Large change of 0.25 > override_threshold
    );
    assert!(can_switch); // Override dwell
}

#[test]
fn test_hysteresis_steady_state_no_switches() {
    let hyst = HysteresisManager::new();
    let mut last_time = Instant::now();
    let threshold = 0.5;
    let mut switch_count = 0;

    // Simulate steady state with small oscillations in band
    let risk_scores = vec![0.495, 0.505, 0.498, 0.502, 0.499];

    for risk in risk_scores {
        if hyst.should_switch(
            RoutingMode::Lifecycle,
            risk,
            threshold,
            last_time,
            0.5,
        ) {
            switch_count += 1;
            last_time = Instant::now();
        }
    }

    assert_eq!(switch_count, 0); // No switches in steady state
}

#[test]
fn test_hysteresis_dwell_time_enforcement() {
    let hyst = HysteresisManager::new();
    let now = Instant::now();

    // Just switched, dwell active
    let can_switch_1 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.70,     // Outside band (should be able to switch)
        0.5,
        now,
        0.3,
    );
    assert!(can_switch_1); // Outside band always switches

    // But if in band right after switch, don't allow it
    let can_switch_2 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.50,     // Inside band
        0.5,
        now,      // Dwell active
        0.505,
    );
    assert!(!can_switch_2);
}

#[test]
fn test_hysteresis_band_boundary_precision() {
    let hyst = HysteresisManager::new();
    let threshold = 0.5;

    // Test exact band boundaries
    let lower = threshold - hyst.band_width;
    let upper = threshold + hyst.band_width;

    assert!(hyst.in_hysteresis_band(lower, threshold));
    assert!(hyst.in_hysteresis_band(upper, threshold));
    assert!(!hyst.in_hysteresis_band(lower - 0.001, threshold));
    assert!(!hyst.in_hysteresis_band(upper + 0.001, threshold));
}

#[test]
fn test_hysteresis_custom_parameters() {
    let narrow_band = HysteresisManager::with_config(
        0.05,
        Duration::from_secs(60),
        Duration::from_secs(600),
        0.10,
    );

    let threshold = 0.5;

    // Narrower band means less tolerance
    assert!(narrow_band.in_hysteresis_band(0.47, threshold));
    assert!(!narrow_band.in_hysteresis_band(0.44, threshold)); // Outside narrow band
}

#[test]
fn test_hysteresis_multiple_switches() {
    let hyst = HysteresisManager::new();
    let mut last_time = Instant::now();
    let threshold = 0.5;

    // Switch 1: far below threshold
    let can_switch_1 = hyst.should_switch(
        RoutingMode::Lifecycle,
        0.1,
        threshold,
        last_time,
        0.5,
    );
    assert!(can_switch_1);
    last_time = Instant::now();

    // Switch 2: in dwell, don't switch back yet
    let can_switch_2 = hyst.should_switch(
        RoutingMode::TheGent,
        0.9,      // Back to high risk
        threshold,
        last_time,  // Dwell active
        0.1,
    );
    assert!(can_switch_2); // Outside band, always switch
}
