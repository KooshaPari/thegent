//! Policy Compiler - Compiles policy definitions from various formats.

use serde::{Deserialize, Serialize};

use crate::domain::{Effect, Policy, PolicyError, PolicyResult, Rule};

/// Policy compiler - Compiles policy definitions.
pub struct PolicyCompiler;

impl PolicyCompiler {
    /// Compile a policy from JSON.
    pub fn from_json(json: &str) -> PolicyResult<Policy> {
        let def: PolicyDefinition = serde_json::from_str(json)
            .map_err(|e| PolicyError::ParseError { message: e.to_string() })?;

        Self::compile(def)
    }

    /// Compile a policy from YAML.
    #[cfg(feature = "yaml")]
    pub fn from_yaml(yaml: &str) -> PolicyResult<Policy> {
        let def: PolicyDefinition = serde_yaml::from_str(yaml)
            .map_err(|e| PolicyError::ParseError { message: e.to_string() })?;

        Self::compile(def)
    }

    /// Compile a policy definition.
    fn compile(def: PolicyDefinition) -> PolicyResult<Policy> {
        let mut policy = match def.effect.as_str() {
            "allow" | "permit" | "Allow" | "Permit" => Policy::allow(&def.name),
            "deny" | "forbid" | "Deny" | "Forbid" => Policy::deny(&def.name),
            _ => return Err(PolicyError::InvalidPolicy { 
                message: format!("Invalid effect: {}", def.effect) 
            }),
        };

        if let Some(desc) = def.description {
            policy = policy.with_description(desc);
        }

        if let Some(version) = def.version {
            policy = policy.with_version(version);
        }

        for rule_def in def.rules.into_iter() {
            let rule = Rule::new(&rule_def.name, Self::parse_effect(&rule_def.effect)?);
            
            // Note: In a real implementation, you'd parse conditions here
            // For now, we use simple condition syntax
            
            policy = policy.with_rule(rule);
        }

        Ok(policy)
    }

    fn parse_effect(effect: &str) -> PolicyResult<Effect> {
        match effect.to_lowercase().as_str() {
            "allow" | "permit" | "true" => Ok(Effect::Allow),
            "deny" | "forbid" | "false" => Ok(Effect::Deny),
            _ => Err(PolicyError::InvalidRule { 
                message: format!("Invalid effect: {}", effect) 
            }),
        }
    }
}

/// Policy definition for serialization/deserialization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyDefinition {
    /// Policy name
    pub name: String,
    /// Policy description
    pub description: Option<String>,
    /// Policy version
    pub version: Option<String>,
    /// Policy effect
    pub effect: String,
    /// Rules
    pub rules: Vec<RuleDefinition>,
}

/// Rule definition for serialization/deserialization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuleDefinition {
    /// Rule name
    pub name: String,
    /// Rule effect
    pub effect: String,
    /// Condition (simplified - in production, use proper condition DSL)
    pub condition: Option<String>,
}

/// Compile multiple policies from JSON array.
pub fn compile_policies_from_json(json: &str) -> PolicyResult<Vec<Policy>> {
    let defs: Vec<PolicyDefinition> = serde_json::from_str(json)
        .map_err(|e| PolicyError::ParseError { message: e.to_string() })?;

    defs.into_iter()
        .map(PolicyCompiler::compile)
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compile_simple_policy() {
        let json = r#"{
            "name": "test-policy",
            "effect": "allow",
            "rules": [
                {"name": "rule1", "effect": "allow"}
            ]
        }"#;

        let policy = PolicyCompiler::from_json(json).unwrap();
        assert_eq!(policy.name(), "test-policy");
    }

    #[test]
    fn test_compile_multiple() {
        let json = r#"[
            {"name": "policy1", "effect": "allow", "rules": []},
            {"name": "policy2", "effect": "deny", "rules": []}
        ]"#;

        let policies = compile_policies_from_json(json).unwrap();
        assert_eq!(policies.len(), 2);
    }
}
