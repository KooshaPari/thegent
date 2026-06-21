// SPDX-License-Identifier: MIT OR Apache-2.0
//! TUI panels — WL-031 and beyond.
//!
//! Panels are full-region composites that combine multiple widgets into a
//! coherent view.  They manage their own state structs and translate raw
//! key events into domain actions.
//!
//! Current panels:
//! - `ParetoFrontierPanel` — Pareto Frontier Visualization (WL-031)

pub mod pareto;

pub use pareto::{AuditRecord, ParetoAction, ParetoFrontierPanel, ParetoFrontierState};
