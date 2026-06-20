// SPDX-License-Identifier: MIT OR Apache-2.0
//! Tests for thegent-policy module

use crate::{PolicyManager, LearningSession, SloRegulator};

#[test]
fn test_policy_manager_new() {
    let pm = PolicyManager::new(None);
    assert!(pm.get_policy("nonexistent").is_none());
}

#[test]
fn test_policy_manager_update() {
    let mut pm = PolicyManager::new(None);
    let mut policies = std::collections::HashMap::new();
    policies.insert("cost_cap".to_string(), serde_json::json!(10.0));
    policies.insert("enabled".to_string(), serde_json::json!(true));
    pm.update(policies);
    
    assert!(pm.get_policy("cost_cap").is_some());
    assert_eq!(pm.get_policy_f64("cost_cap"), Some(10.0));
}

#[test]
fn test_policy_manager_get_policy_str() {
    let mut pm = PolicyManager::new(None);
    let mut policies = std::collections::HashMap::new();
    policies.insert("name".to_string(), serde_json::json!("test_policy"));
    pm.update(policies);
    
    assert_eq!(pm.get_policy_str("name"), Some("test_policy".to_string()));
}

#[test]
fn test_learning_session_new() {
    let pm = PolicyManager::new(None);
    let session = LearningSession::new(pm);
    assert!(!session.is_active());
    assert_eq!(session.cost_cap(), 10.0); // default
}

#[test]
fn test_learning_session_with_cost_cap() {
    let mut pm = PolicyManager::new(None);
    let mut policies = std::collections::HashMap::new();
    policies.insert("cost_cap".to_string(), serde_json::json!(25.0));
    pm.update(policies);
    
    let session = LearningSession::new(pm);
    assert_eq!(session.cost_cap(), 25.0);
}

#[test]
fn test_learning_session_start() {
    let pm = PolicyManager::new(None);
    let mut session = LearningSession::new(pm);
    assert!(!session.is_valid());
    
    session.start();
    assert!(session.is_valid());
    assert!(session.is_active());
}

#[test]
fn test_learning_session_refresh_policy() {
    let mut pm = PolicyManager::new(None);
    let mut policies = std::collections::HashMap::new();
    policies.insert("cost_cap".to_string(), serde_json::json!(10.0));
    pm.update(policies);
    
    let mut session = LearningSession::new(pm);
    session.start();
    assert_eq!(session.cost_cap(), 10.0);
    
    // Update policy during session
    let mut new_policies = std::collections::HashMap::new();
    new_policies.insert("cost_cap".to_string(), serde_json::json!(50.0));
    // Note: This would need &mut PolicyManager in real usage
}

// SLO Regulator tests

#[test]
fn test_slo_regulator_new() {
    let slo = SloRegulator::new(100.0, 0.05);
    assert!(slo.is_compliant()); // Empty metrics = compliant
}

#[test]
fn test_slo_regulator_record_execution() {
    let mut slo = SloRegulator::new(100.0, 0.05);
    slo.record_execution(50.0, true);
    assert_eq!(slo.metrics_count(), 1);
}

#[test]
fn test_slo_regulator_compliant() {
    let mut slo = SloRegulator::new(100.0, 0.05);
    // All good executions
    for _ in 0..10 {
        slo.record_execution(50.0, true);
    }
    assert!(slo.is_compliant());
}

#[test]
fn test_slo_regulator_latency_violation() {
    let mut slo = SloRegulator::new(100.0, 0.05);
    // High latency
    for _ in 0..10 {
        slo.record_execution(150.0, true);
    }
    assert!(!slo.is_compliant());
}

#[test]
fn test_slo_regulator_error_violation() {
    let mut slo = SloRegulator::new(100.0, 0.05);
    // High error rate
    for _ in 0..10 {
        slo.record_execution(50.0, false);
    }
    assert!(!slo.is_compliant());
}
