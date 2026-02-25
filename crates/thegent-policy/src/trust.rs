//! Trust boundary checks module

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Trust levels for agents and domains
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Serialize, Deserialize)]
pub enum TrustLevel {
    External = 0,
    Partner = 1,
    Internal = 2,
    Strict = 3,
}

impl TrustLevel {
    pub fn as_int(&self) -> i32 {
        match self {
            TrustLevel::External => 0,
            TrustLevel::Partner => 1,
            TrustLevel::Internal => 2,
            TrustLevel::Strict => 3,
        }
    }
}

/// Enforces trust boundaries between agents and tasks
#[derive(Debug, Clone)]
pub struct TrustBoundaryChecker {
    agent_trust_map: HashMap<String, TrustLevel>,
    cache: HashMap<String, CacheEntry>,
    cache_ttl: Duration,
}

#[derive(Debug, Clone)]
struct CacheEntry {
    result: EvaluationResult,
    cached_at: Instant,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationResult {
    pub allowed: bool,
    pub reason: Option<String>,
    pub agent_trust: String,
    pub risk_score: i32,
}

impl TrustBoundaryChecker {
    pub fn new(cache_ttl_sec: u64) -> Self {
        let mut agent_trust_map = HashMap::new();
        agent_trust_map.insert("interactive_agent".to_string(), TrustLevel::Internal);
        agent_trust_map.insert("headless_agent".to_string(), TrustLevel::Internal);
        agent_trust_map.insert("cursor".to_string(), TrustLevel::Internal);
        agent_trust_map.insert("copilot".to_string(), TrustLevel::External);
        agent_trust_map.insert("gemini".to_string(), TrustLevel::External);
        agent_trust_map.insert("quality_agent".to_string(), TrustLevel::Internal);

        Self {
            agent_trust_map,
            cache: HashMap::new(),
            cache_ttl: Duration::from_secs(cache_ttl_sec),
        }
    }

    pub fn get_agent_trust(&self, agent_name: &str) -> TrustLevel {
        self.agent_trust_map.get(agent_name).copied().unwrap_or(TrustLevel::External)
    }

    fn create_cache_key(&self, target_agent: &str, prompt: &str) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        prompt.hash(&mut hasher);
        let hash = hasher.finish();
        format!("{}:{:016x}", target_agent, hash)
    }

    fn is_cache_valid(&self, key: &str) -> bool {
        if let Some(entry) = self.cache.get(key) {
            return entry.cached_at.elapsed() < self.cache_ttl;
        }
        false
    }

    pub fn evaluate_routing(&mut self, task_prompt: &str, target_agent: &str) -> EvaluationResult {
        // Create cache key
        let cache_key = self.create_cache_key(target_agent, task_prompt);

        // Check cache first (OPT-008)
        if self.is_cache_valid(&cache_key) {
            return self.cache.get(&cache_key).unwrap().result.clone();
        }

        // Evaluate policy
        let agent_trust = self.get_agent_trust(target_agent);
        let mut result = EvaluationResult {
            allowed: true,
            reason: None,
            agent_trust: format!("{:?}", agent_trust),
            risk_score: 0,
        };

        // Sensitive keywords requiring INTERNAL+ trust
        let sensitive_keywords = [
            "password", "secret", "private_key", "token", "credential", "api_key"
        ];

        let prompt_lower = task_prompt.to_lowercase();
        let found_sensitive: Vec<&str> = sensitive_keywords
            .iter()
            .filter(|kw| prompt_lower.contains(**kw))
            .copied()
            .collect();

        if !found_sensitive.is_empty() && agent_trust < TrustLevel::Internal {
            result.allowed = false;
            result.reason = Some(format!(
                "Sensitive data ({}) cannot be sent to EXTERNAL agent {}",
                found_sensitive[0], target_agent
            ));
            result.risk_score = 10;
        }

        // Cache result
        self.cache.insert(cache_key, CacheEntry {
            result: result.clone(),
            cached_at: Instant::now(),
        });

        result
    }

    pub fn check_data_flow(&self, source_agent: &str, dest_agent: &str) -> bool {
        let source_level = self.get_agent_trust(source_agent);
        let dest_level = self.get_agent_trust(dest_agent);

        // Data can flow to same or higher trust
        // Flowing from higher to lower trust might need auditing
        if source_level > dest_level {
            // Log cross-boundary flow (in production would use logging)
        }

        true // Default allow
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_trust_boundary_checker_new() {
        let checker = TrustBoundaryChecker::new(300);
        assert_eq!(checker.get_agent_trust("cursor"), TrustLevel::Internal);
        assert_eq!(checker.get_agent_trust("copilot"), TrustLevel::External);
    }

    #[test]
    fn test_evaluate_routing_allowed() {
        let mut checker = TrustBoundaryChecker::new(300);
        let result = checker.evaluate_routing("Hello world", "cursor");
        assert!(result.allowed);
    }

    #[test]
    fn test_evaluate_routing_blocked() {
        let mut checker = TrustBoundaryChecker::new(0); // Disable cache
        // copilot is External, prompt contains sensitive keyword "api_key"
        let result = checker.evaluate_routing("Please send my secret API key now", "copilot");
        assert!(!result.allowed);
        assert!(result.reason.is_some());
        assert_eq!(result.risk_score, 10);
    }

    #[test]
    fn test_evaluate_routing_cache() {
        let mut checker = TrustBoundaryChecker::new(300);
        let result1 = checker.evaluate_routing("test prompt", "cursor");
        let result2 = checker.evaluate_routing("test prompt", "cursor");
        assert_eq!(result1.risk_score, result2.risk_score);
    }

    #[test]
    fn test_check_data_flow() {
        let checker = TrustBoundaryChecker::new(300);
        assert!(checker.check_data_flow("cursor", "cursor"));
    }
}
