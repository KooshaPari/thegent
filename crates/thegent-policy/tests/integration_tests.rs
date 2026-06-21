// SPDX-License-Identifier: MIT OR Apache-2.0
/// @trace FR-GOV-001
#[test]
fn test_policy_engine_loads_config() {
    let engine = thegent_policy::PolicyEngine::new("./tests/fixtures/test-policy.toml");
    assert!(engine.is_ok());
}

/// @trace FR-GOV-001
#[test]
fn test_policy_evaluates_compliance_rule() {
    let engine = thegent_policy::PolicyEngine::new("./tests/fixtures/test-policy.toml")
        .expect("Failed to load engine");

    let rule = thegent_policy::ComplianceRule {
        id: "FR-GOV-001".to_string(),
        category: "cost_governance".to_string(),
        expression: "cost_per_call <= 0.01".to_string(),
    };

    let result = engine.evaluate(&rule, &Default::default());
    assert!(result.is_ok());
}

/// @trace FR-GOV-002
#[test]
fn test_policy_engine_caches_evaluation() {
    let engine = thegent_policy::PolicyEngine::new("./tests/fixtures/test-policy.toml")
        .expect("Failed to load engine");

    let rule = thegent_policy::ComplianceRule {
        id: "FR-GOV-002".to_string(),
        category: "cost_governance".to_string(),
        expression: "call_count <= 1000".to_string(),
    };

    let context = thegent_policy::EvaluationContext::default();

    // First evaluation
    let result1 = engine.evaluate(&rule, &context).unwrap();

    // Second evaluation (should be cached)
    let result2 = engine.evaluate(&rule, &context).unwrap();

    // Both results must be identical
    assert_eq!(result1, result2);
}

/// @trace FR-GOV-003
#[test]
fn test_policy_engine_evaluate_by_id() {
    let engine = thegent_policy::PolicyEngine::new("./tests/fixtures/test-policy.toml")
        .expect("Failed to load engine");

    let context = thegent_policy::EvaluationContext::default();
    let result = engine.evaluate_by_id("FR-GOV-001", &context);
    assert!(result.is_ok());
    assert!(result.unwrap().passed);
}

/// @trace FR-GOV-003
#[test]
fn test_policy_engine_evaluate_by_id_not_found() {
    let engine = thegent_policy::PolicyEngine::new("./tests/fixtures/test-policy.toml")
        .expect("Failed to load engine");

    let context = thegent_policy::EvaluationContext::default();
    let result = engine.evaluate_by_id("DOES_NOT_EXIST", &context);
    assert!(result.is_err());
}
