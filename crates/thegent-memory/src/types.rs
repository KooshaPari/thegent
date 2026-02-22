//! Type definitions for Supermemory integration
//!
//! Provides request/response types, memory operations, and queries
//! that are serializable to/from JSON for the Supermemory.ai API.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

// ============================================================================
// Memory Identifiers
// ============================================================================

/// Unique identifier for a memory entry.
pub type MemoryId = String;

/// Unique identifier for a session context.
pub type SessionId = String;

// ============================================================================
// Memory Operations
// ============================================================================

/// Represents a memory operation (store, update, or delete action).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryOperation {
    /// Unique ID for this operation.
    pub id: MemoryId,

    /// Session this operation belongs to.
    pub session_id: SessionId,

    /// Type of operation: "store", "update", "delete", etc.
    pub operation_type: OperationType,

    /// Timestamp when the operation was created.
    pub created_at: DateTime<Utc>,

    /// Timestamp when the operation was last updated.
    pub updated_at: DateTime<Utc>,

    /// The actual memory data (embedding, metadata, context, etc.).
    pub data: MemoryData,

    /// Optional tags for categorization and filtering.
    #[serde(default)]
    pub tags: Vec<String>,

    /// Optional metadata about the memory.
    #[serde(default)]
    pub metadata: serde_json::Value,
}

impl MemoryOperation {
    /// Create a new memory operation for storing data.
    pub fn new_store(session_id: SessionId, data: MemoryData) -> Self {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        Self {
            id,
            session_id,
            operation_type: OperationType::Store,
            created_at: now,
            updated_at: now,
            data,
            tags: Vec::new(),
            metadata: serde_json::json!({}),
        }
    }

    /// Create a new memory operation for retrieving data.
    pub fn new_retrieve(session_id: SessionId, data: MemoryData) -> Self {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        Self {
            id,
            session_id,
            operation_type: OperationType::Retrieve,
            created_at: now,
            updated_at: now,
            data,
            tags: Vec::new(),
            metadata: serde_json::json!({}),
        }
    }
}

/// Type of operation to perform on memory.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum OperationType {
    /// Store new memory.
    Store,
    /// Update existing memory.
    Update,
    /// Retrieve memory.
    Retrieve,
    /// Delete memory.
    Delete,
    /// Search for memory.
    Search,
}

impl std::fmt::Display for OperationType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Store => write!(f, "store"),
            Self::Update => write!(f, "update"),
            Self::Retrieve => write!(f, "retrieve"),
            Self::Delete => write!(f, "delete"),
            Self::Search => write!(f, "search"),
        }
    }
}

// ============================================================================
// Memory Data
// ============================================================================

/// The actual memory data being stored or retrieved.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryData {
    /// Raw text content of the memory.
    pub content: String,

    /// Vector embedding of the content (for semantic search).
    #[serde(default)]
    pub embedding: Option<Vec<f32>>,

    /// Source of the memory (e.g., "user_input", "document", "conversation").
    #[serde(default)]
    pub source: Option<String>,

    /// Additional context relevant to the memory.
    #[serde(default)]
    pub context: Option<String>,
}

impl MemoryData {
    /// Create new memory data with just content.
    pub fn new(content: impl Into<String>) -> Self {
        Self {
            content: content.into(),
            embedding: None,
            source: None,
            context: None,
        }
    }

    /// Set the embedding vector.
    pub fn with_embedding(mut self, embedding: Vec<f32>) -> Self {
        self.embedding = Some(embedding);
        self
    }

    /// Set the source.
    pub fn with_source(mut self, source: impl Into<String>) -> Self {
        self.source = Some(source.into());
        self
    }

    /// Set the context.
    pub fn with_context(mut self, context: impl Into<String>) -> Self {
        self.context = Some(context.into());
        self
    }
}

// ============================================================================
// Query Types
// ============================================================================

/// A query for searching memories.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryQuery {
    /// Session ID to search within.
    pub session_id: SessionId,

    /// Search query text.
    pub query: String,

    /// Optional embedding vector for semantic search.
    #[serde(default)]
    pub embedding: Option<Vec<f32>>,

    /// Maximum number of results to return.
    #[serde(default = "default_limit")]
    pub limit: usize,

    /// Optional filters (e.g., by tags or metadata).
    #[serde(default)]
    pub filters: serde_json::Value,

    /// Optional threshold for similarity matching.
    #[serde(default)]
    pub threshold: Option<f32>,
}

fn default_limit() -> usize {
    10
}

impl MemoryQuery {
    /// Create a new query.
    pub fn new(session_id: SessionId, query: impl Into<String>) -> Self {
        Self {
            session_id,
            query: query.into(),
            embedding: None,
            limit: 10,
            filters: serde_json::json!({}),
            threshold: None,
        }
    }

    /// Set the limit on results.
    pub fn with_limit(mut self, limit: usize) -> Self {
        self.limit = limit;
        self
    }

    /// Set the embedding for semantic search.
    pub fn with_embedding(mut self, embedding: Vec<f32>) -> Self {
        self.embedding = Some(embedding);
        self
    }

    /// Set the threshold for similarity.
    pub fn with_threshold(mut self, threshold: f32) -> Self {
        self.threshold = Some(threshold);
        self
    }
}

// ============================================================================
// Response Types
// ============================================================================

/// Response from a memory operation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryResponse {
    /// ID of the operation.
    pub operation_id: MemoryId,

    /// Matched results (for search/retrieve operations).
    pub results: Vec<MemoryResult>,

    /// Metadata about the response.
    pub metadata: ResponseMetadata,

    /// Session context returned by the server.
    #[serde(default)]
    pub session_context: Option<SessionContext>,
}

impl MemoryResponse {
    /// Create a new response.
    pub fn new(operation_id: MemoryId) -> Self {
        Self {
            operation_id,
            results: Vec::new(),
            metadata: ResponseMetadata::default(),
            session_context: None,
        }
    }

    /// Add a result to the response.
    pub fn with_result(mut self, result: MemoryResult) -> Self {
        self.results.push(result);
        self
    }
}

/// A single result from a memory search or retrieval.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryResult {
    /// ID of the memory entry.
    pub id: MemoryId,

    /// Content of the memory.
    pub content: String,

    /// Relevance score (0.0 to 1.0).
    pub score: f32,

    /// Tags associated with this memory.
    #[serde(default)]
    pub tags: Vec<String>,

    /// Timestamp when this memory was created.
    pub created_at: DateTime<Utc>,

    /// Source of the memory.
    #[serde(default)]
    pub source: Option<String>,
}

/// Metadata about a response.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ResponseMetadata {
    /// Total number of results available.
    #[serde(default)]
    pub total_count: usize,

    /// Number of results returned.
    #[serde(default)]
    pub returned_count: usize,

    /// Whether there are more results available.
    #[serde(default)]
    pub has_more: bool,

    /// Server-provided request ID for tracking.
    #[serde(default)]
    pub request_id: Option<String>,

    /// Processing time in milliseconds.
    #[serde(default)]
    pub processing_time_ms: Option<u64>,
}

/// Session context provided by the server.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionContext {
    /// Session ID.
    pub session_id: SessionId,

    /// Session creation time.
    pub created_at: DateTime<Utc>,

    /// Number of memories in the session.
    pub memory_count: usize,

    /// Total size of session data.
    pub total_size_bytes: u64,

    /// Server-provided metadata.
    #[serde(default)]
    pub metadata: serde_json::Value,
}

// ============================================================================
// Knowledge Graph Types
// ============================================================================

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

    // Memory operation tests (from supermemory-rs)
    #[test]
    fn test_memory_operation_serialization() {
        let data = MemoryData::new("test content");
        let op = MemoryOperation::new_store("session-1".to_string(), data);

        let json = serde_json::to_string(&op).expect("serialize");
        let deserialized: MemoryOperation = serde_json::from_str(&json).expect("deserialize");

        assert_eq!(op.id, deserialized.id);
        assert_eq!(op.session_id, deserialized.session_id);
        assert_eq!(op.data.content, deserialized.data.content);
    }

    #[test]
    fn test_memory_data_builder() {
        let data = MemoryData::new("hello")
            .with_source("test")
            .with_context("context");

        assert_eq!(data.content, "hello");
        assert_eq!(data.source, Some("test".to_string()));
        assert_eq!(data.context, Some("context".to_string()));
    }

    #[test]
    fn test_memory_query_serialization() {
        let query = MemoryQuery::new("session-1".to_string(), "search term")
            .with_limit(20)
            .with_threshold(0.7);

        let json = serde_json::to_string(&query).expect("serialize");
        let deserialized: MemoryQuery = serde_json::from_str(&json).expect("deserialize");

        assert_eq!(query.query, deserialized.query);
        assert_eq!(query.limit, deserialized.limit);
        assert_eq!(query.threshold, deserialized.threshold);
    }

    #[test]
    fn test_memory_result_serialization() {
        let result = MemoryResult {
            id: "mem-1".to_string(),
            content: "test content".to_string(),
            score: 0.95,
            tags: vec!["important".to_string()],
            created_at: Utc::now(),
            source: Some("test".to_string()),
        };

        let json = serde_json::to_string(&result).expect("serialize");
        let deserialized: MemoryResult = serde_json::from_str(&json).expect("deserialize");

        assert_eq!(result.id, deserialized.id);
        assert_eq!(result.score, deserialized.score);
    }

    #[test]
    fn test_operation_type_display() {
        assert_eq!(OperationType::Store.to_string(), "store");
        assert_eq!(OperationType::Search.to_string(), "search");
    }

    // Knowledge graph tests (from thegent-memory)
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
