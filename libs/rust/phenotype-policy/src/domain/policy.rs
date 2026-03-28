//! Policy - Core domain concept for authorization policies.
//!
//! A Policy defines the rules for allowing or denying access to resources.

use std::collections::HashMap;
use std::fmt::Debug;

use super::{Condition, Effect, Rule};

/// Policy - A named set of rules for authorization decisions.
///
/// A policy consists of:
/// - A unique name
/// - A description
/// - An effect (ALLOW or DENY)
/// - A description of what the policy applies to (optional)
/// - A list of rules
#[derive(Debug, Clone)]
pub struct Policy {
    /// Unique identifier for the policy
    name: String,
    /// Human-readable description
    description: Option<String>,
    /// The effect of the policy
    effect: Effect,
    /// Policy version
    version: String,
    /// List of rules in this policy
    rules: Vec<Rule>,
    /// Target (what this policy applies to)
    target: Option<PolicyTarget>,
    /// Metadata
    metadata: HashMap<String, String>,
}

impl Policy {
    /// Create a new policy with the given name and effect.
    pub fn new(name: impl Into<String>, effect: Effect) -> Self {
        Self {
            name: name.into(),
            description: None,
            effect,
            version: "1.0".to_string(),
            rules: Vec::new(),
            target: None,
            metadata: HashMap::new(),
        }
    }

    /// Create an ALLOW policy.
    pub fn allow(name: impl Into<String>) -> Self {
        Self::new(name, Effect::Allow)
    }

    /// Create a DENY policy.
    pub fn deny(name: impl Into<String>) -> Self {
        Self::new(name, Effect::Deny)
    }

    /// Get the policy name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get the effect.
    pub fn effect(&self) -> Effect {
        self.effect
    }

    /// Get the description.
    pub fn description(&self) -> Option<&str> {
        self.description.as_deref()
    }

    /// Set the description.
    pub fn with_description(mut self, description: impl Into<String>) -> Self {
        self.description = Some(description.into());
        self
    }

    /// Get the version.
    pub fn version(&self) -> &str {
        &self.version
    }

    /// Set the version.
    pub fn with_version(mut self, version: impl Into<String>) -> Self {
        self.version = version.into();
        self
    }

    /// Add a rule to the policy.
    pub fn with_rule(mut self, rule: Rule) -> Self {
        self.rules.push(rule);
        self
    }

    /// Add multiple rules to the policy.
    pub fn with_rules(mut self, rules: impl IntoIterator<Item = Rule>) -> Self {
        self.rules.extend(rules);
        self
    }

    /// Get the rules.
    pub fn rules(&self) -> &[Rule] {
        &self.rules
    }

    /// Set the target.
    pub fn with_target(mut self, target: PolicyTarget) -> Self {
        self.target = Some(target);
        self
    }

    /// Get the target.
    pub fn target(&self) -> Option<&PolicyTarget> {
        self.target.as_ref()
    }

    /// Add metadata.
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    /// Get metadata.
    pub fn metadata(&self) -> &HashMap<String, String> {
        &self.metadata
    }

    /// Check if the policy is empty (no rules).
    pub fn is_empty(&self) -> bool {
        self.rules.is_empty()
    }

    /// Get the number of rules.
    pub fn len(&self) -> usize {
        self.rules.len()
    }
}

/// Target - Describes what resources a policy applies to.
#[derive(Debug, Clone, Default)]
pub struct PolicyTarget {
    /// Resource types this policy applies to
    resources: Vec<String>,
    /// Actions this policy applies to
    actions: Vec<String>,
    /// Subjects this policy applies to
    subjects: Vec<String>,
    /// Environments this policy applies to
    environments: Vec<Condition>,
}

impl PolicyTarget {
    /// Create a new empty target.
    pub fn new() -> Self {
        Self::default()
    }

    /// Add a resource pattern.
    pub fn with_resources(mut self, resources: impl IntoIterator<Item = String>) -> Self {
        self.resources.extend(resources);
        self
    }

    /// Add an action pattern.
    pub fn with_actions(mut self, actions: impl IntoIterator<Item = String>) -> Self {
        self.actions.extend(actions);
        self
    }

    /// Add a subject pattern.
    pub fn with_subjects(mut self, subjects: impl IntoIterator<Item = String>) -> Self {
        self.subjects.extend(subjects);
        self
    }

    /// Check if this target matches the given attributes.
    pub fn matches(
        &self,
        resource: &str,
        action: &str,
        subject: &str,
    ) -> bool {
        self.matches_resource(resource)
            && self.matches_action(action)
            && self.matches_subject(subject)
    }

    fn matches_resource(&self, resource: &str) -> bool {
        self.resources.is_empty()
            || self.resources.iter().any(|r| resource.starts_with(r))
    }

    fn matches_action(&self, action: &str) -> bool {
        self.actions.is_empty()
            || self.actions.iter().any(|a| action.starts_with(a))
    }

    fn matches_subject(&self, subject: &str) -> bool {
        self.subjects.is_empty()
            || self.subjects.iter().any(|s| subject.starts_with(s))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_allow_policy() {
        let policy = Policy::allow("read-todos")
            .with_description("Allow reading todos")
            .with_rule(Rule::new("read-rule", Effect::Allow)
                .with_condition(|_| true));

        assert_eq!(policy.name(), "read-todos");
        assert_eq!(policy.effect(), Effect::Allow);
        assert_eq!(policy.len(), 1);
    }

    #[test]
    fn test_deny_policy() {
        let policy = Policy::deny("delete-admin")
            .with_rule(Rule::new("deny-rule", Effect::Deny)
                .with_condition(|_| false));

        assert_eq!(policy.effect(), Effect::Deny);
    }

    #[test]
    fn test_target_matching() {
        let target = PolicyTarget::new()
            .with_resources(vec!["arn:aws:s3:::bucket/".to_string()])
            .with_actions(vec!["s3:GetObject".to_string()]);

        assert!(target.matches("arn:aws:s3:::bucket/file.txt", "s3:GetObject", "user:123"));
        assert!(!target.matches("arn:aws:s3:::other-bucket/", "s3:GetObject", "user:123"));
    }
}
