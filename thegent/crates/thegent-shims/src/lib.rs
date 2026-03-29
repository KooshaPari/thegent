//! thegent-shims: High-performance Rust command shims for thegent
//!
//! Provides fast, reliable replacements for shell wrappers:
//! - `thegent-git`: Git operations with TTL caching and lock handling
//! - `thegent-grep`: Fast search with ripgrep integration
//! - `thegent-find`: Directory traversal with fd awareness
//! - `thegent-agent`: Agent invocation with fallback routing

pub mod agent;
pub mod cache;
pub mod find;
pub mod git;
pub mod grep;
pub mod lock;
pub mod utils;

pub use agent::AgentShim;
pub use find::FindShim;
pub use git::GitShim;
pub use grep::GrepShim;
