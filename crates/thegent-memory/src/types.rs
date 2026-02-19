//! Type definitions for Supermemory integration

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Knowledge graph node
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeNode {
    /// Unique identifier
    pub id: String,

    /// Entity name
    pub entity: String,

    /// Node description
    pub description: Option<String>,

    /// Associated relationships
    pub relationships: Vec<Relationship>,

    /// Node metadata
    pub metadata: HashMap<String, serde_json::Value>,

    /// Creation timestamp (Unix seconds)
    pub created_at: u64,

    /// Last updated timestamp (Unix seconds)
    pub updated_at: u64,
}

impl KnowledgeNode {
    /// Create a new knowledge node
    pub fn new(id: String, entity: String) -> Self {
        let now = chrono::Utc::now().timestamp() as u64;
        Self {
            id,
            entity,
            description: None,
            relationships: Vec::new(),
            metadata: HashMap::new(),
            created_at: now,
            updated_at: now,
        }
    }
}

/// Relationship between entities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Relationship {
    /// Relationship type (e.g., "depends_on", "references")
    pub relationship_type: String,

    /// Target entity ID
    pub target: String,

    /// Relationship metadata
    pub metadata: HashMap<String, serde_json::Value>,
}

impl Relationship {
    /// Create a new relationship
    pub fn new(relationship_type: String, target: String) -> Self {
        Self {
            relationship_type,
            target,
            metadata: HashMap::new(),
        }
    }
}

/// Authentication method for Supermemory API
#[derive(Debug, Clone)]
pub enum AuthMethod {
    /// API key authentication
    ApiKey(String),

    /// OAuth2 token
    OAuth2(String),
}

impl AuthMethod {
    /// Extract header value for authentication
    pub fn to_header_value(&self) -> String {
        match self {
            AuthMethod::ApiKey(key) => format!("Bearer {}", key),
            AuthMethod::OAuth2(token) => format!("Bearer {}", token),
        }
    }
}

/// Query result from Supermemory
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryResult {
    /// Matched knowledge nodes
    pub nodes: Vec<KnowledgeNode>,

    /// Total number of results (for pagination)
    pub total: usize,

    /// Current page offset
    pub offset: usize,

    /// Current page size
    pub limit: usize,
}

impl QueryResult {
    /// Check if there are more results
    pub fn has_more(&self) -> bool {
        self.offset + self.limit < self.total
    }

    /// Get next page offset
    pub fn next_offset(&self) -> usize {
        self.offset + self.limit
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_knowledge_node_creation() {
        let node = KnowledgeNode::new("n1".to_string(), "Agent".to_string());
        assert_eq!(node.id, "n1");
        assert_eq!(node.entity, "Agent");
        assert_eq!(node.relationships.len(), 0);
    }

    #[test]
    fn test_relationship_creation() {
        let rel = Relationship::new("depends_on".to_string(), "n2".to_string());
        assert_eq!(rel.relationship_type, "depends_on");
        assert_eq!(rel.target, "n2");
    }

    #[test]
    fn test_auth_method_header() {
        let auth = AuthMethod::ApiKey("test_key".to_string());
        assert_eq!(auth.to_header_value(), "Bearer test_key");
    }

    #[test]
    fn test_query_result_pagination() {
        let result = QueryResult {
            nodes: vec![],
            total: 100,
            offset: 0,
            limit: 10,
        };
        assert!(result.has_more());
        assert_eq!(result.next_offset(), 10);
    }
}
