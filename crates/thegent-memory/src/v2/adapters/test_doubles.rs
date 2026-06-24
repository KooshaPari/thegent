// SPDX-License-Identifier: MIT OR Apache-2.0
//! In-process test doubles — no network, no live sidecars required.
//!
//! The [`MockAdapter`] is the canonical implementation used by the
//! trait-conformance suite (`tests/trait_conformance.rs`). It accepts
//! any [`MemoryScope`] and stores records in a `Mutex<Vec<MemoryRecord>>`,
//! matching by `text` substring on recall.

use std::collections::HashMap;
use std::sync::Mutex;

use async_trait::async_trait;

use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

#[derive(Default)]
pub struct MockAdapter {
    inner: Mutex<HashMap<(MemoryScope, String), MemoryRecord>>,
}

impl MockAdapter {
    pub fn new() -> Self {
        Self::default()
    }
}

#[async_trait]
impl MemoryPort for MockAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        let id = uuid::Uuid::new_v4().to_string();
        let rec = MemoryRecord {
            id: id.clone(),
            scope,
            key: key.to_string(),
            value,
            score: Some(1.0),
        };
        let mut g = self.inner.lock().map_err(|e| MemoryError::Internal(e.to_string()))?;
        g.insert((scope, key.to_string()), rec);
        Ok(id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        let g = self.inner.lock().map_err(|e| MemoryError::Internal(e.to_string()))?;
        let needle = query.text.to_lowercase();
        let mut hits: Vec<MemoryRecord> = g
            .values()
            .filter(|r| r.scope == scope)
            .filter(|r| match &r.value {
                MemoryValue::Text(s) => s.to_lowercase().contains(&needle),
                _ => false,
            })
            .cloned()
            .collect();
        hits.truncate(query.limit);
        Ok(hits)
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        let mut g = self.inner.lock().map_err(|e| MemoryError::Internal(e.to_string()))?;
        g.remove(&(scope, key.to_string()));
        Ok(())
    }

    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError> {
        // Mock accepts any scope, so report all four.
        Ok(vec![
            MemoryScope::Episodic,
            MemoryScope::Identity,
            MemoryScope::ProjectKnowledge,
            MemoryScope::Fallback,
        ])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Composite // distinguishable from any single backend
    }
}