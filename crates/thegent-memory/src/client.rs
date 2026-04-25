//! Supermemory client implementation with MCP protocol support

use crate::error::{Error, Result};
use crate::types::{AuthMethod, KnowledgeNode, QueryResult, Relationship};
use reqwest::Client as HttpClient;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Circuit breaker states
#[derive(Debug, Clone, Copy, PartialEq)]
enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

/// Circuit breaker for Supermemory API
#[derive(Debug)]
struct CircuitBreaker {
    state: Arc<Mutex<CircuitState>>,
    failure_count: Arc<Mutex<usize>>,
    last_failure_time: Arc<Mutex<Option<Instant>>>,
    failure_threshold: usize,
    reset_timeout: Duration,
}

impl CircuitBreaker {
    fn new(failure_threshold: usize, reset_timeout: Duration) -> Self {
        Self {
            state: Arc::new(Mutex::new(CircuitState::Closed)),
            failure_count: Arc::new(Mutex::new(0)),
            last_failure_time: Arc::new(Mutex::new(None)),
            failure_threshold,
            reset_timeout,
        }
    }

    fn record_success(&self) {
        let mut state = self.state.lock().unwrap();
        *self.failure_count.lock().unwrap() = 0;
        if *state == CircuitState::HalfOpen {
            *state = CircuitState::Closed;
        }
    }

    fn record_failure(&self) -> Result<()> {
        let mut count = self.failure_count.lock().unwrap();
        *count += 1;
        *self.last_failure_time.lock().unwrap() = Some(Instant::now());

        let mut state = self.state.lock().unwrap();
        if *count >= self.failure_threshold {
            *state = CircuitState::Open;
        }

        Ok(())
    }

    fn is_open(&self) -> bool {
        let state = self.state.lock().unwrap();
        match *state {
            CircuitState::Open => {
                if let Some(last_failure) = *self.last_failure_time.lock().unwrap() {
                    if last_failure.elapsed() > self.reset_timeout {
                        drop(state);
                        let mut s = self.state.lock().unwrap();
                        *s = CircuitState::HalfOpen;
                        false
                    } else {
                        true
                    }
                } else {
                    true
                }
            }
            _ => false,
        }
    }
}

/// Supermemory client with multi-tenant support
pub struct SupermemoryClient {
    http_client: HttpClient,
    base_url: String,
    auth: AuthMethod,
    project_id: String,
    circuit_breaker: CircuitBreaker,
    request_timeout: Duration,
}

impl SupermemoryClient {
    /// Create a new Supermemory client from environment variables.
    ///
    /// Reads `SM_API_KEY`, optionally `SM_PROJECT` and `SM_BASE_URL` environment variables.
    ///
    /// # Errors
    ///
    /// Returns an error if `SM_API_KEY` is not set or invalid.
    pub fn from_env() -> Result<Self> {
        use std::env;

        let api_key = env::var("SM_API_KEY")
            .map_err(|_| Error::Authentication("SM_API_KEY not set".into()))?;

        if api_key.is_empty() {
            return Err(Error::Authentication("SM_API_KEY is empty".into()));
        }

        let project = env::var("SM_PROJECT").ok();
        let base_url =
            env::var("SM_BASE_URL").unwrap_or_else(|_| "https://api.supermemory.ai/v1".to_string());

        let project_id = project.unwrap_or_else(|| "default".to_string());
        let auth = AuthMethod::ApiKey(api_key);

        // Use a blocking runtime for from_env since it's typically called at startup
        let runtime = tokio::runtime::Runtime::new()
            .map_err(|e| Error::Internal(format!("Failed to create runtime: {}", e)))?;

        runtime.block_on(Self::new(base_url, project_id, auth))
    }

    /// Create a new Supermemory client
    ///
    /// # Arguments
    /// * `base_url` - Supermemory API base URL
    /// * `project_id` - Project identifier for multi-tenant isolation
    /// * `auth` - Authentication method
    ///
    /// # Example
    /// ```ignore
    /// let auth = AuthMethod::ApiKey("key".to_string());
    /// let client = SupermemoryClient::new(
    ///     "https://api.supermemory.ai".to_string(),
    ///     "project-1".to_string(),
    ///     auth,
    /// ).await?;
    /// ```
    pub async fn new(base_url: String, project_id: String, auth: AuthMethod) -> Result<Self> {
        if project_id.is_empty() {
            return Err(Error::InvalidProject(
                "Project ID cannot be empty".to_string(),
            ));
        }

        let http_client = HttpClient::builder()
            .timeout(Duration::from_secs(30))
            .build()?;

        Ok(Self {
            http_client,
            base_url: base_url.trim_end_matches('/').to_string(),
            auth,
            project_id,
            circuit_breaker: CircuitBreaker::new(5, Duration::from_secs(60)),
            request_timeout: Duration::from_secs(30),
        })
    }

    /// Query knowledge graph
    ///
    /// # Arguments
    /// * `query` - Search query
    /// * `limit` - Maximum number of results
    ///
    /// # Returns
    /// Vector of matching knowledge nodes
    pub async fn query_knowledge(&self, query: &str, limit: usize) -> Result<Vec<KnowledgeNode>> {
        if self.circuit_breaker.is_open() {
            return Err(Error::CircuitBreakerOpen);
        }

        let url = format!("{}/knowledge/query", self.base_url);
        let body = serde_json::json!({
            "query": query,
            "limit": limit,
            "project_id": self.project_id,
        });

        let response = self
            .http_client
            .post(&url)
            .header("Authorization", self.auth.to_header_value())
            .header("x-sm-project", &self.project_id)
            .header("Content-Type", "application/json")
            .timeout(self.request_timeout)
            .json(&body)
            .send()
            .await;

        match response {
            Ok(resp) => {
                let result: QueryResult = resp.json().await?;
                self.circuit_breaker.record_success();
                Ok(result.nodes)
            }
            Err(e) => {
                let _ = self.circuit_breaker.record_failure();
                Err(Error::Query(format!("Query failed: {}", e)))
            }
        }
    }

    /// Store knowledge in the graph
    ///
    /// # Arguments
    /// * `entity` - Entity name
    /// * `relationships` - Related entities
    ///
    /// # Returns
    /// Document ID of stored knowledge
    pub async fn store_knowledge(
        &self,
        entity: &str,
        relationships: Vec<Relationship>,
    ) -> Result<String> {
        if self.circuit_breaker.is_open() {
            return Err(Error::CircuitBreakerOpen);
        }

        if entity.is_empty() {
            return Err(Error::InvalidArgument("Entity cannot be empty".to_string()));
        }

        let url = format!("{}/knowledge/store", self.base_url);
        let node = KnowledgeNode::new(uuid::Uuid::new_v4().to_string(), entity.to_string());

        let body = serde_json::json!({
            "node": node,
            "relationships": relationships,
            "project_id": self.project_id,
        });

        let response = self
            .http_client
            .post(&url)
            .header("Authorization", self.auth.to_header_value())
            .header("x-sm-project", &self.project_id)
            .header("Content-Type", "application/json")
            .timeout(self.request_timeout)
            .json(&body)
            .send()
            .await;

        match response {
            Ok(resp) => {
                let result: serde_json::Value = resp.json().await?;
                if let Some(doc_id) = result.get("doc_id").and_then(|v| v.as_str()) {
                    self.circuit_breaker.record_success();
                    Ok(doc_id.to_string())
                } else {
                    Err(Error::Storage("No doc_id in response".to_string()))
                }
            }
            Err(e) => {
                let _ = self.circuit_breaker.record_failure();
                Err(Error::Storage(format!("Storage failed: {}", e)))
            }
        }
    }

    /// Store document to L4 storage
    ///
    /// # Arguments
    /// * `doc_id` - Document identifier
    /// * `content` - Document content
    ///
    /// # Returns
    /// Storage confirmation
    pub async fn store_document(&self, doc_id: &str, content: serde_json::Value) -> Result<()> {
        if self.circuit_breaker.is_open() {
            return Err(Error::CircuitBreakerOpen);
        }

        let url = format!("{}/documents/store", self.base_url);
        let body = serde_json::json!({
            "doc_id": doc_id,
            "content": content,
            "project_id": self.project_id,
        });

        let response = self
            .http_client
            .put(&url)
            .header("Authorization", self.auth.to_header_value())
            .header("x-sm-project", &self.project_id)
            .header("Content-Type", "application/json")
            .timeout(self.request_timeout)
            .json(&body)
            .send()
            .await;

        match response {
            Ok(_) => {
                self.circuit_breaker.record_success();
                Ok(())
            }
            Err(e) => {
                let _ = self.circuit_breaker.record_failure();
                Err(Error::Storage(format!("Document storage failed: {}", e)))
            }
        }
    }

    /// Get project ID
    pub fn project_id(&self) -> &str {
        &self.project_id
    }

    /// Get base URL
    pub fn base_url(&self) -> &str {
        &self.base_url
    }

    /// List all conversations.
    pub async fn list_conversations(&self) -> Result<Vec<String>> {
        // Placeholder implementation - would use reqwest in production
        Ok(vec![])
    }

    /// Store a memory.
    pub async fn store(&self, _data: &crate::types::MemoryData) -> Result<String> {
        // Placeholder - would POST to /memories
        Ok(uuid::Uuid::new_v4().to_string())
    }

    /// Query memories.
    pub async fn query(
        &self,
        _query: &crate::types::MemoryQuery,
    ) -> Result<Vec<crate::types::MemoryResponse>> {
        // Placeholder - would POST to /query
        Ok(vec![])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_client_creation() {
        let auth = AuthMethod::ApiKey("test_key".to_string());
        let client = SupermemoryClient::new(
            "https://api.example.com".to_string(),
            "proj-1".to_string(),
            auth,
        )
        .await
        .unwrap();

        assert_eq!(client.project_id(), "proj-1");
        assert_eq!(client.base_url(), "https://api.example.com");
    }

    #[tokio::test]
    async fn test_empty_project_id() {
        let auth = AuthMethod::ApiKey("test_key".to_string());
        let result =
            SupermemoryClient::new("https://api.example.com".to_string(), "".to_string(), auth)
                .await;

        assert!(result.is_err());
    }

    #[test]
    fn test_circuit_breaker_state_transitions() {
        let cb = CircuitBreaker::new(2, Duration::from_secs(10));

        // Initial state: Closed
        assert!(!cb.is_open());

        // Record failures
        let _ = cb.record_failure();
        assert!(!cb.is_open());

        let _ = cb.record_failure();
        assert!(cb.is_open());

        // After calling is_open() with an open breaker, if reset_timeout hasn't elapsed,
        // it should still be open and transition to HalfOpen if enough time has passed
        // For this test, we'll just verify the state is tracked
        let is_open = cb.is_open();
        assert!(is_open);
    }

    // Tests from supermemory-rs - Note: from_env tests are integration tests in tests/
    // because they require proper environment isolation and tokio runtime.
}
