/// @trace FR-GOV-004
#[test]
fn test_compliance_check_cost_exceeded() {
    let checker = thegent_policy::ComplianceChecker::new();

    let rule = thegent_policy::ComplianceRule {
        id: "cost-limit".to_string(),
        category: "cost".to_string(),
        expression: "cost <= 1.0".to_string(),
    };

    let mut context = thegent_policy::EvaluationContext::default();
    context.cost_per_call = 2.5;

    let result = checker.evaluate(&rule, &context).unwrap();
    assert!(!result.passed);
    assert!(result.reason.contains("cost"));
}

/// @trace FR-GOV-004
#[test]
fn test_compliance_check_cost_within_limit() {
    let checker = thegent_policy::ComplianceChecker::new();

    let rule = thegent_policy::ComplianceRule {
        id: "cost-limit".to_string(),
        category: "cost".to_string(),
        expression: "cost <= 1.0".to_string(),
    };

    let mut context = thegent_policy::EvaluationContext::default();
    context.cost_per_call = 0.5;

    let result = checker.evaluate(&rule, &context).unwrap();
    assert!(result.passed);
}

/// @trace FR-GOV-005
#[test]
fn test_compliance_check_multiple_rules() {
    let checker = thegent_policy::ComplianceChecker::new();

    let rules = vec![
        thegent_policy::ComplianceRule {
            id: "rule1".to_string(),
            category: "cost".to_string(),
            expression: "cost <= 1.0".to_string(),
        },
        thegent_policy::ComplianceRule {
            id: "rule2".to_string(),
            category: "calls".to_string(),
            expression: "calls <= 1000".to_string(),
        },
    ];

    let context = thegent_policy::EvaluationContext::default();
    let results = checker.evaluate_batch(&rules, &context).unwrap();

    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.passed));
}

/// @trace FR-GOV-006
#[test]
fn test_cost_enforcer_basic() {
    let enforcer = thegent_policy::CostEnforcer::new(1.0);

    let result1 = enforcer.check_budget_available(0.5).unwrap();
    assert!(result1);

    assert!(enforcer.can_spend(0.5));
    assert!(!enforcer.can_spend(0.6));
    assert!(enforcer.can_spend(0.5));
}

/// @trace FR-GOV-006
#[test]
fn test_cost_enforcer_remaining() {
    let enforcer = thegent_policy::CostEnforcer::new(1.0);
    assert!((enforcer.remaining() - 1.0).abs() < f64::EPSILON);

    enforcer.can_spend(0.3);
    assert!((enforcer.remaining() - 0.7).abs() < f64::EPSILON);
}

/// @trace FR-GOV-006
#[test]
fn test_cost_enforcer_reset() {
    let enforcer = thegent_policy::CostEnforcer::new(1.0);
    enforcer.can_spend(0.8);
    enforcer.reset();
    assert!((enforcer.remaining() - 1.0).abs() < f64::EPSILON);
    assert!(enforcer.can_spend(1.0));
}

/// @trace FR-GOV-006
#[test]
fn test_cost_enforcer_clone_shares_state() {
    let enforcer = thegent_policy::CostEnforcer::new(1.0);
    let clone = enforcer.clone();

    enforcer.can_spend(0.5);
    // Clone shares the same Arc<Mutex<f64>>
    assert!((clone.remaining() - 0.5).abs() < f64::EPSILON);
}
