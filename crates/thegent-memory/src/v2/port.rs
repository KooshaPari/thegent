// SPDX-License-Identifier: MIT OR Apache-2.0
//! The abstract [`MemoryPort`] — every adapter in `v2::adapters::*` implements
//! this. Per AGENTS.md ADR-014 (hexagonal port-adapter L4 policy), the trait
//! is the only contract; nothing in v2 couples to a concrete backend.

use async_trait::async_trait;

use crate::v2::value::{MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue};

/// Identifies which backend a port talks to. The composite router uses
/// this to label itself and to surface the backing engine to callers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum MemoryProvider {
    Supermemory,
    Letta,
    Cognee,
    Mem0,
    /// Alternative: temporal KG (event time + ingestion time). Same
    /// scope niche as Cognee (`ProjectKnowledge`) but with a different
    /// ontology. See ADR-098.
    Graphiti,
    /// Alternative: per-user memory with explicit consent gating. Same
    /// scope niche as Letta (`Identity`) but multi-tenant-safe. See ADR-098.
    Hippo,
    /// Alternative: episodic memory with dialogue-act classification.
    /// Same scope niche as Supermemory (`Episodic`) but turn-type
    /// metadata in recall. See ADR-098.
    Zep,
    Composite,
}

impl MemoryProvider {
    /// Stable lowercase string label (useful for logging, telemetry, FFI).
    pub fn as_str(&self) -> &'static str {
        match self {
            MemoryProvider::Supermemory => "supermemory",
            MemoryProvider::Letta => "letta",
            MemoryProvider::Cognee => "cognee",
            MemoryProvider::Mem0 => "mem0",
            MemoryProvider::Graphiti => "graphiti",
            MemoryProvider::Hippo => "hippo",
            MemoryProvider::Zep => "zep",
            MemoryProvider::Composite => "composite",
        }
    }

    /// Returns `true` if this provider is a primary (in the default
    /// composite scope routing). Returns `false` for the 3 ADR-098
    /// alternatives and the `Composite` router itself.
    pub fn is_primary(&self) -> bool {
        matches!(
            self,
            MemoryProvider::Supermemory
                | MemoryProvider::Letta
                | MemoryProvider::Cognee
                | MemoryProvider::Mem0
        )
    }
}

/// The hexagonal port. Every adapter implements this exact surface; every
/// composite delegates to one.
///
/// `Send + Sync` so the port can be wrapped in `Arc<dyn MemoryPort>` and
/// shared across threads (the typical forge/agent topology).
#[async_trait]
pub trait MemoryPort: Send + Sync {
    /// Persist `value` under (`scope`, `key`). Returns the new memory's id.
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError>;

    /// Query the given `scope` for records matching `query`.
    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError>;

    /// Delete (`scope`, `key`). Idempotent: missing keys are not an error.
    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError>;

    /// Return the scopes this port owns. An adapter typically returns exactly
    /// one scope (its primary); the composite returns all four.
    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError>;

    /// Which backend this port talks to.
    fn provider(&self) -> MemoryProvider;
}