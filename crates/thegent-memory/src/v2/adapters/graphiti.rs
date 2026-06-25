// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`GraphitiAdapter`] — temporal knowledge-graph memory.
//!
//! Talks to the Graphiti server (`getzep/graphiti`, Apache-2.0) over its
//! REST API (default `http://127.0.0.1:8001`, surfaced by the
//! `pheno-graphiti` sidecar). Graphiti is the OSS core of the Zep Cloud
//! product; it maintains a **bitemporal** knowledge graph (event time +
//! ingestion time) and is one of the SOTA backbones on LoCoMo and
//! LongMemEval.
//!
//! Scope mapping: Graphiti is used for `ProjectKnowledge` (the same
//! niche as Cognee) but with a different ontology model — temporal
//! edges instead of static triples. ADR-098 treats Cognee as the
//! primary KG and Graphiti as an alternative projection that better
//! fits code-evolution history (commit → file → symbol graphs).

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct GraphitiAdapter {
    base_url: String,
    group_id: String,
    client: Client,
}

impl GraphitiAdapter {
    pub fn default_endpoint() -> Self {
        Self::new(
            default_base_url(MemoryProvider::Graphiti).to_string(),
            "_default".to_string(),
        )
    }

    pub fn new(base_url: String, group_id: String) -> Self {
        Self {
            base_url,
            group_id,
            client: Client::new(),
        }
    }
}

#[derive(Debug, Serialize)]
struct GraphitiAddRequest<'a> {
    group_id: &'a str,
    name: &'a str,
    episode_body: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    source_description: Option<&'a str>,
}

#[derive(Debug, Deserialize)]
struct GraphitiAddResponse {
    message: String,
    #[serde(default)]
    uuid: Option<String>,
}

#[derive(Debug, Serialize)]
struct GraphitiSearchRequest<'a> {
    group_ids: Vec<&'a str>,
    query: &'a str,
    #[serde(default)]
    max_facts: usize,
}

#[derive(Debug, Deserialize)]
struct GraphitiSearchResponse {
    facts: Vec<GraphitiFact>,
}

#[derive(Debug, Deserialize)]
struct GraphitiFact {
    #[serde(default)]
    uuid: Option<String>,
    fact: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for GraphitiAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        let body = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by GraphitiAdapter; pre-encode".into(),
                ))
            }
        };
        let req = GraphitiAddRequest {
            group_id: &self.group_id,
            name: key,
            episode_body: body,
            source_description: Some("thegent-memory v2 GraphitiAdapter"),
        };
        let _ = scope;
        let resp = self
            .client
            .post(format!("{}/add_episode", self.base_url))
            .json(&req)
            .send()
            .await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: GraphitiAddResponse = resp.json().await?;
        Ok(parsed.uuid.unwrap_or(parsed.message))
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        let _ = scope;
        let req = GraphitiSearchRequest {
            group_ids: vec![&self.group_id],
            query: &query.text,
            max_facts: query.limit,
        };
        let resp = self
            .client
            .post(format!("{}/search", self.base_url))
            .json(&req)
            .send()
            .await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: GraphitiSearchResponse = resp.json().await?;
        Ok(parsed
            .facts
            .into_iter()
            .map(|f| MemoryRecord {
                id: f.uuid.clone().unwrap_or_default(),
                scope,
                key: f.uuid.unwrap_or_default(),
                value: MemoryValue::Text(f.fact),
                score: f.score,
            })
            .collect())
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        let _ = scope;
        let url = format!("{}/entity/{}/{}", self.base_url, self.group_id, key);
        let resp = self.client.delete(url).send().await?;
        let status = resp.status();
        if status.is_success() || status.as_u16() == 404 {
            return Ok(());
        }
        let body = resp.text().await.unwrap_or_default();
        Err(MemoryError::Backend {
            status: status.as_u16(),
            body,
        })
    }

    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError> {
        Ok(vec![MemoryScope::ProjectKnowledge])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Graphiti
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn graphiti_adapter_constructs_with_default_endpoint() {
        let a = GraphitiAdapter::default_endpoint();
        assert_eq!(a.provider(), MemoryProvider::Graphiti);
    }

    #[test]
    fn graphiti_adapter_constructs_with_custom_url() {
        let a = GraphitiAdapter::new("http://example:9000".into(), "g1".into());
        assert_eq!(a.base_url, "http://example:9000");
        assert_eq!(a.group_id, "g1");
    }

    #[tokio::test]
    async fn graphiti_lists_project_knowledge_scope() {
        let a = GraphitiAdapter::default_endpoint();
        let scopes = a.list_scopes().await.unwrap();
        assert_eq!(scopes, vec![MemoryScope::ProjectKnowledge]);
    }

    #[tokio::test]
    async fn graphiti_rejects_binary_payloads() {
        let a = GraphitiAdapter::default_endpoint();
        let err = a
            .store(MemoryScope::ProjectKnowledge, "k", MemoryValue::Binary(vec![1, 2, 3]))
            .await
            .unwrap_err();
        assert!(matches!(err, MemoryError::Invalid(_)));
    }
}
