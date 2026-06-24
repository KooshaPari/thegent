// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`SupermemoryAdapter`] — primary episodic store.
//!
//! Talks to the supermemory binary (`supermemoryai/supermemory`) over its
//! REST API (default `http://127.0.0.1:3030`, surfaced by the
//! `pheno-supermemory` sidecar in `pheno-forge-plugins`).
//!
//! Only the `Episodic` scope is supported. Other scopes return
//! [`MemoryError::Invalid`].
//!
//! Live integration with the supermemory binary is gated behind
//! `#[ignore]` tests in `tests/` (see `trait_conformance.rs`). The unit
//! tests here exercise only the request-shape logic via `mockito`.

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct SupermemoryAdapter {
    base_url: String,
    client: Client,
}

impl SupermemoryAdapter {
    /// Default endpoint constructor — `http://127.0.0.1:3030`.
    pub fn default_endpoint() -> Self {
        Self::new(default_base_url(MemoryProvider::Supermemory).to_string())
    }

    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }

    pub fn with_client(base_url: String, client: Client) -> Self {
        Self { base_url, client }
    }
}

#[derive(Debug, Serialize)]
struct StoreRequest<'a> {
    container_tag: &'a str,
    key: &'a str,
    content: &'a str,
}

#[derive(Debug, Deserialize)]
struct StoreResponse {
    id: String,
}

#[derive(Debug, Serialize)]
struct SearchRequest<'a> {
    q: &'a str,
    container_tag: &'a str,
    #[serde(rename = "limit")]
    limit: usize,
}

#[derive(Debug, Deserialize)]
struct SearchResponse {
    #[serde(default)]
    results: Vec<SearchHit>,
}

#[derive(Debug, Deserialize)]
struct SearchHit {
    id: String,
    #[serde(default)]
    content: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for SupermemoryAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        if scope != MemoryScope::Episodic {
            return Err(MemoryError::Invalid(format!(
                "SupermemoryAdapter only supports Episodic scope (got {:?})",
                scope
            )));
        }
        let content = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by SupermemoryAdapter; pre-encode"
                        .into(),
                ))
            }
        };
        let req = StoreRequest {
            container_tag: scope.as_str(),
            key,
            content,
        };
        let resp = self
            .client
            .post(format!("{}/v1/store", self.base_url))
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
        let parsed: StoreResponse = resp.json().await?;
        Ok(parsed.id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        if scope != MemoryScope::Episodic {
            return Err(MemoryError::Invalid(format!(
                "SupermemoryAdapter only supports Episodic scope (got {:?})",
                scope
            )));
        }
        let req = SearchRequest {
            q: &query.text,
            container_tag: scope.as_str(),
            limit: query.limit,
        };
        let resp = self
            .client
            .post(format!("{}/v1/search", self.base_url))
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
        let parsed: SearchResponse = resp.json().await?;
        let recs = parsed
            .results
            .into_iter()
            .map(|h| {
                let id = h.id.clone();
                MemoryRecord {
                    id: h.id,
                    scope,
                    key: id,
                    value: MemoryValue::Text(h.content),
                    score: h.score,
                }
            })
            .collect();
        Ok(recs)
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        if scope != MemoryScope::Episodic {
            return Err(MemoryError::Invalid(format!(
                "SupermemoryAdapter only supports Episodic scope (got {:?})",
                scope
            )));
        }
        let resp = self
            .client
            .delete(format!("{}/v1/store/{}/{}", self.base_url, scope.as_str(), key))
            .send()
            .await?;
        let status = resp.status();
        // 200/202/204 all count as success; 404 is idempotent.
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
        Ok(vec![MemoryScope::Episodic])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Supermemory
    }
}