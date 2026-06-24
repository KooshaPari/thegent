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
            MemoryProvider::Composite => "composite",
        }
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