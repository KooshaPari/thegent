// SPDX-License-Identifier: MIT OR Apache-2.0
//! v2 of the memory substrate: a polyglot, hexagonal port over multiple
//! memory engines (Supermemory, Letta, Cognee, Mem0) and a `CompositeAdapter`
//! router that dispatches by `MemoryScope`.
//!
//! v1 (`SupermemoryClient` at `crate::client`) remains available via
//! `pub use` at the crate root and is unchanged in behavior; v2 is additive.
//!
//! Trait surface (per AGENTS.md ADR-014 hexagonal port pattern):
//! - [`MemoryPort`] — the abstract port
//! - [`MemoryScope`] — routes through the composite
//! - [`MemoryValue`] / [`MemoryQuery`] / [`MemoryRecord`] / [`MemoryError`]
//!   — value + error types
//! - [`MemoryProvider`] — labels which backend a port talks to
//!
//! Adapters (each implements [`MemoryPort`]):
//! - [`adapters::SupermemoryAdapter`] — primary episodic store (REST/MCP)
//! - [`adapters::LettaAdapter`] — subconscious blocks per-agent identity
//! - [`adapters::CogneeAdapter`] — project knowledge graph
//! - [`adapters::Mem0Adapter`] — fallback
//! - [`adapters::MockAdapter`] — in-process test double
//! - [`CompositeAdapter`] — router that dispatches by [`MemoryScope`]
//!
//! See `thegent/docs/specs/memory/v2.md` for the canonical spec and
//! `findings/2026-06-23-forgecode-improvement-plan.md` for context.

pub mod adapters;
pub mod composite;
pub mod port;
pub mod value;

pub use composite::CompositeAdapter;
pub use port::{MemoryPort, MemoryProvider};
pub use value::{MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue};

// Re-export the adapters at the v2 module root for ergonomics:
//   `use thegent_memory::v2::SupermemoryAdapter;`
pub use adapters::{CogneeAdapter, LettaAdapter, Mem0Adapter, SupermemoryAdapter};