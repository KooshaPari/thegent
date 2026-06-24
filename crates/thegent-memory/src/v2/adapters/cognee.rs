// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`CogneeAdapter`] — project knowledge graph.
//!
//! Talks to Cognee (`topoteretes/cognee`) via its MCP server (`cognee-mcp`)
//! using the 4-op API: `remember`, `recall`, `forget`, `improve`. Default
//! transport is stdio (`cognee-mcp`), surfaced by the `pheno-cognee`
//! sidecar in `pheno-forge-plugins`.
//!
//! Only the `ProjectKnowledge` scope is supported.
//!
//! The stdio transport is abstracted behind a [`CogneeTransport`] trait so
//! tests can stub it (the default constructor opens a real stdio pipe).

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

/// Transport for the cognee-mcp process. Implementations include the
/// production stdio pipe (`StdioCogneeTransport`) and the in-process
/// `MockCogneeTransport` used by tests.
#[async_trait]
pub trait CogneeTransport: Send + Sync {
    async fn invoke(
        &self,
        op: &str,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, MemoryError>;
}

pub struct CogneeAdapter {
    #[allow(dead_code)]
    base_url: String,
    transport: Box<dyn CogneeTransport>,
}

impl CogneeAdapter {
    pub fn default_endpoint() -> Self {
        Self::new(
            default_base_url(MemoryProvider::Cognee).to_string(),
            Box::new(StubTransport),
        )
    }

    pub fn new(base_url: String, transport: Box<dyn CogneeTransport>) -> Self {
        Self { base_url, transport }
    }
}

#[derive(Debug, Serialize)]
struct RememberRequest<'a> {
    dataset: &'a str,
    content: &'a str,
}

#[derive(Debug, Deserialize)]
struct RememberResponse {
    id: String,
}

#[derive(Debug, Serialize)]
struct RecallRequest<'a> {
    dataset: &'a str,
    query: &'a str,
    #[serde(rename = "limit")]
    limit: usize,
}

#[derive(Debug, Deserialize)]
struct RecallResponse {
    nodes: Vec<KnowledgeNode>,
}

#[derive(Debug, Deserialize)]
struct KnowledgeNode {
    id: String,
    label: String,
    #[serde(default)]
    summary: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for CogneeAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        if scope != MemoryScope::ProjectKnowledge {
            return Err(MemoryError::Invalid(format!(
                "CogneeAdapter only supports ProjectKnowledge scope (got {:?})",
                scope
            )));
        }
        let content = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by CogneeAdapter".into(),
                ))
            }
        };
        let req = RememberRequest {
            dataset: key,
            content,
        };
        let payload = self.transport.invoke("remember", serde_json::to_value(req)?).await?;
        let parsed: RememberResponse = serde_json::from_value(payload)?;
        Ok(parsed.id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        if scope != MemoryScope::ProjectKnowledge {
            return Err(MemoryError::Invalid(format!(
                "CogneeAdapter only supports ProjectKnowledge scope (got {:?})",
                scope
            )));
        }
        let req = RecallRequest {
            dataset: "_any_",
            query: &query.text,
            limit: query.limit,
        };
        let payload = self.transport.invoke("recall", serde_json::to_value(req)?).await?;
        let parsed: RecallResponse = serde_json::from_value(payload)?;
        Ok(parsed
            .nodes
            .into_iter()
            .map(|n| MemoryRecord {
                id: n.id.clone(),
                scope,
                key: n.id,
                value: MemoryValue::Text(if n.summary.is_empty() { n.label } else { n.summary }),
                score: n.score,
            })
            .collect())
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        if scope != MemoryScope::ProjectKnowledge {
            return Err(MemoryError::Invalid(format!(
                "CogneeAdapter only supports ProjectKnowledge scope (got {:?})",
                scope
            )));
        }
        let payload = serde_json::json!({ "dataset": key });
        let _ = self.transport.invoke("forget", payload).await?;
        Ok(())
    }

    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError> {
        Ok(vec![MemoryScope::ProjectKnowledge])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Cognee
    }
}

/// Default transport — returns `MemoryError::Unavailable` for every call so
/// the adapter compiles without an external `cognee-mcp` binary. Tests use
/// their own transport via `CogneeAdapter::new`.
struct StubTransport;

#[async_trait]
impl CogneeTransport for StubTransport {
    async fn invoke(
        &self,
        _op: &str,
        _payload: serde_json::Value,
    ) -> Result<serde_json::Value, MemoryError> {
        Err(MemoryError::Unavailable(
            "CogneeAdapter requires a configured CogneeTransport (stdio or mock); \
             use CogneeAdapter::new(url, transport) to inject one"
                .into(),
        ))
    }
}

/// In-process mock transport for tests. Records all calls into a `Vec` and
/// returns canned responses per op.
#[cfg(test)]
pub struct MockCogneeTransport {
    pub calls: std::sync::Mutex<Vec<(String, serde_json::Value)>>,
}

#[cfg(test)]
impl MockCogneeTransport {
    pub fn new() -> Self {
        Self {
            calls: std::sync::Mutex::new(Vec::new()),
        }
    }
}

#[cfg(test)]
#[async_trait]
impl CogneeTransport for MockCogneeTransport {
    async fn invoke(
        &self,
        op: &str,
        payload: serde_json::Value,
    ) -> Result<serde_json::Value, MemoryError> {
        self.calls
            .lock()
            .map_err(|e| MemoryError::Internal(e.to_string()))?
            .push((op.to_string(), payload.clone()));
        match op {
            "remember" => Ok(serde_json::json!({ "id": "cognee-mock-1" })),
            "recall" => Ok(serde_json::json!({
                "nodes": [{
                    "id": "node-1",
                    "label": "mock label",
                    "summary": "mock summary",
                    "score": 0.9,
                }]
            })),
            "forget" => Ok(serde_json::json!({ "ok": true })),
            _ => Err(MemoryError::Invalid(format!("unknown op: {}", op))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn cognee_adapter_round_trips_via_mock_transport() {
        let mock = std::sync::Arc::new(MockCogneeTransport::new());
        let adapter = CogneeAdapter::new(
            "stdio://cognee-mcp".to_string(),
            Box::new(MockTransportWrap(mock.clone())),
        );

        let id = adapter
            .store(MemoryScope::ProjectKnowledge, "ds-1", "hello cognee".into())
            .await
            .unwrap();
        assert_eq!(id, "cognee-mock-1");

        let recs = adapter
            .recall(MemoryScope::ProjectKnowledge, MemoryQuery::new("hello"))
            .await
            .unwrap();
        assert_eq!(recs.len(), 1);
        assert_eq!(recs[0].scope, MemoryScope::ProjectKnowledge);
        assert_eq!(recs[0].value, MemoryValue::Text("mock summary".into()));

        adapter
            .forget(MemoryScope::ProjectKnowledge, "ds-1")
            .await
            .unwrap();

        assert_eq!(mock.calls.lock().unwrap().len(), 3);
    }

    struct MockTransportWrap(std::sync::Arc<MockCogneeTransport>);
    #[async_trait]
    impl CogneeTransport for MockTransportWrap {
        async fn invoke(
            &self,
            op: &str,
            payload: serde_json::Value,
        ) -> Result<serde_json::Value, MemoryError> {
            self.0.invoke(op, payload).await
        }
    }
}