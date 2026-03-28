//! Policy Registry - Stores and retrieves policies.

use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use crate::domain::{Policy, PolicyError, PolicyResult};

/// Policy registry - Stores policies for retrieval.
pub struct PolicyRegistry {
    /// Storage for policies by name
    policies: RwLock<HashMap<String, Arc<Policy>>>,
    /// Storage for policy sets
    policy_sets: RwLock<HashMap<String, Vec<String>>>,
}

impl PolicyRegistry {
    /// Create a new empty registry.
    pub fn new() -> Self {
        Self {
            policies: RwLock::new(HashMap::new()),
            policy_sets: RwLock::new(HashMap::new()),
        }
    }

    /// Register a policy.
    pub fn register(&self, policy: Policy) -> PolicyResult<()> {
        let name = policy.name().to_string();
        let mut policies = self.policies.write()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire write lock".to_string() 
            })?;

        policies.insert(name, Arc::new(policy));
        Ok(())
    }

    /// Register multiple policies.
    pub fn register_all(&self, policies: impl IntoIterator<Item = Policy>) -> PolicyResult<()> {
        for policy in policies {
            self.register(policy)?;
        }
        Ok(())
    }

    /// Get a policy by name.
    pub fn get(&self, name: &str) -> PolicyResult<Arc<Policy>> {
        let policies = self.policies.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        policies.get(name)
            .cloned()
            .ok_or_else(|| PolicyError::policy_not_found(name))
    }

    /// Check if a policy exists.
    pub fn contains(&self, name: &str) -> bool {
        self.policies.read()
            .map(|p| p.contains_key(name))
            .unwrap_or(false)
    }

    /// List all policy names.
    pub fn list(&self) -> PolicyResult<Vec<String>> {
        let policies = self.policies.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        Ok(policies.keys().cloned().collect())
    }

    /// Get all policies.
    pub fn get_all(&self) -> PolicyResult<Vec<Arc<Policy>>> {
        let policies = self.policies.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        Ok(policies.values().cloned().collect())
    }

    /// Unregister a policy.
    pub fn unregister(&self, name: &str) -> PolicyResult<()> {
        let mut policies = self.policies.write()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire write lock".to_string() 
            })?;

        if policies.remove(name).is_none() {
            return Err(PolicyError::policy_not_found(name));
        }

        Ok(())
    }

    /// Clear all policies.
    pub fn clear(&self) -> PolicyResult<()> {
        let mut policies = self.policies.write()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire write lock".to_string() 
            })?;

        policies.clear();
        Ok(())
    }

    /// Register a policy set (collection of policies).
    pub fn register_policy_set(&self, name: &str, policy_names: Vec<String>) -> PolicyResult<()> {
        let mut sets = self.policy_sets.write()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire write lock".to_string() 
            })?;

        // Verify all policies exist
        let policies = self.policies.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        for policy_name in &policy_names {
            if !policies.contains_key(policy_name) {
                return Err(PolicyError::policy_not_found(policy_name));
            }
        }

        sets.insert(name.to_string(), policy_names);
        Ok(())
    }

    /// Get a policy set.
    pub fn get_policy_set(&self, name: &str) -> PolicyResult<Vec<Arc<Policy>>> {
        let sets = self.policy_sets.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        let policy_names = sets.get(name)
            .ok_or_else(|| PolicyError::policy_not_found(name))?;

        let policies = self.policies.read()
            .map_err(|_| PolicyError::RegistryError { 
                message: "Failed to acquire read lock".to_string() 
            })?;

        policy_names.iter()
            .map(|n| {
                policies.get(n)
                    .cloned()
                    .ok_or_else(|| PolicyError::policy_not_found(n))
            })
            .collect()
    }
}

impl Default for PolicyRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::{Effect, Rule};

    fn create_test_policy() -> Policy {
        Policy::new("test-policy", Effect::Allow)
            .with_rule(Rule::new("test-rule", Effect::Allow))
    }

    #[test]
    fn test_register_and_get() {
        let registry = PolicyRegistry::new();
        let policy = create_test_policy();

        registry.register(policy.clone()).unwrap();
        let retrieved = registry.get("test-policy").unwrap();

        assert_eq!(retrieved.name(), "test-policy");
    }

    #[test]
    fn test_not_found() {
        let registry = PolicyRegistry::new();
        let result = registry.get("non-existent");

        assert!(result.is_err());
    }

    #[test]
    fn test_unregister() {
        let registry = PolicyRegistry::new();
        let policy = create_test_policy();

        registry.register(policy).unwrap();
        registry.unregister("test-policy").unwrap();

        assert!(!registry.contains("test-policy"));
    }

    #[test]
    fn test_policy_set() {
        let registry = PolicyRegistry::new();

        registry.register(Policy::allow("policy1")).unwrap();
        registry.register(Policy::allow("policy2")).unwrap();

        registry.register_policy_set("my-set", vec!["policy1".to_string(), "policy2".to_string()]).unwrap();

        let policies = registry.get_policy_set("my-set").unwrap();
        assert_eq!(policies.len(), 2);
    }
}
