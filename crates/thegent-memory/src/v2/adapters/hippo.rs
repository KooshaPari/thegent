// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`HippoAdapter`] — episodic + KG memory with consent gating.
//!
//! Talks to the Hippo (`hippo-rs/hippo`, Apache-2.0) REST API. Hippo is
//! a Rust-native memory engine built around "consented memory" — each
//! record carries an explicit consent scope (user/public/anonymous)
//! that gates recall. It is the smallest dep tree of the four SOTA
//! memory engines, with a single static binary deployment.
//!
//! Scope mapping: Hippo is used for `Identity` (per-user persistent
//! memory). It overlaps with Letta's `core_memory` blocks but adds a
//! consent layer that makes it a better fit for multi-tenant
//! deployments. ADR-098 treats Letta as the primary identity substrate
//! and Hippo as the alternative for fleets that need explicit consent
//! boundaries between agents.

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct HippoAdapter {
    base_url: String,
    agent_id: String,
    client: Client,
}

impl HippoAdapter {
    pub fn default_endpoint() -> Self {
        Self::new(
            default_base_url(MemoryProvider::Hippo).to_string(),
            "_default".to_string(),
        )
    }

    pub fn new(base_url: String, agent_id: String) -> Self {
        Self {
            base_url,
            agent_id,
            client: Client::new(),
        }
    }
}

#[derive(Debug, Serialize)]
struct HippoRememberRequest<'a> {
    agent_id: &'a str,
    key: &'a str,
    content: &'a str,
    consent: &'a str,
}

#[derive(Debug, Deserialize)]
struct HippoRememberResponse {
    id: String,
}

#[derive(Debug, Serialize)]
struct HippoRecallRequest<'a> {
    agent_id: &'a str,
    query: &'a str,
    #[serde(default)]
    limit: usize,
    #[serde(default)]
    consent: Option<&'a str>,
}

#[derive(Debug, Deserialize)]
struct HippoRecallResponse {
    memories: Vec<HippoMemory>,
}

#[derive(Debug, Deserialize)]
struct HippoMemory {
    id: String,
    key: String,
    content: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for HippoAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        let content = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by HippoAdapter; pre-encode".into(),
                ))
            }
        };
        let req = HippoRememberRequest {
            agent_id: &self.agent_id,
            key,
            content,
            consent: "self", // identity scope defaults to self-consent
        };
        let _ = scope;
        let resp = self
            .client
            .post(format!("{}/api/remember", self.base_url))
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
        let parsed: HippoRememberResponse = resp.json().await?;
        Ok(parsed.id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        let _ = scope;
        let req = HippoRecallRequest {
            agent_id: &self.agent_id,
            query: &query.text,
            limit: query.limit,
            consent: Some("self"),
        };
        let resp = self
            .client
            .post(format!("{}/api/recall", self.base_url))
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
        let parsed: HippoRecallResponse = resp.json().await?;
        Ok(parsed
            .memories
            .into_iter()
            .map(|m| MemoryRecord {
                id: m.id.clone(),
                scope,
                key: m.key,
                value: MemoryValue::Text(m.content),
                score: m.score,
            })
            .collect())
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        let _ = scope;
        let resp = self
            .client
            .delete(format!("{}/api/memories/{}/{}", self.base_url, self.agent_id, key))
            .send()
            .await?;
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
        Ok(vec![MemoryScope::Identity])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Hippo
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hippo_adapter_constructs_with_default_endpoint() {
        let a = HippoAdapter::default_endpoint();
        assert_eq!(a.provider(), MemoryProvider::Hippo);
    }

    #[test]
    fn hippo_adapter_constructs_with_custom_url() {
        let a = HippoAdapter::new("http://example:9000".into(), "agent-1".into());
        assert_eq!(a.base_url, "http://example:9000");
        assert_eq!(a.agent_id, "agent-1");
    }

    #[tokio::test]
    async fn hippo_lists_identity_scope() {
        let a = HippoAdapter::default_endpoint();
        let scopes = a.list_scopes().await.unwrap();
        assert_eq!(scopes, vec![MemoryScope::Identity]);
    }

    #[tokio::test]
    async fn hippo_rejects_binary_payloads() {
        let a = HippoAdapter::default_endpoint();
        let err = a
            .store(MemoryScope::Identity, "k", MemoryValue::Binary(vec![1, 2, 3]))
            .await
            .unwrap_err();
        assert!(matches!(err, MemoryError::Invalid(_)));
    }
}
