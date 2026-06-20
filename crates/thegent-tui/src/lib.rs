// SPDX-License-Identifier: MIT OR Apache-2.0
//! thegent-tui — Phase 2 + Phase 3 + WL-052 + WL-031 TUI crate.
//!
//! Phase 2 provides:
//! - `widgets::InteractiveInput`  — command input with history & autocomplete
//! - `widgets::TableWidget`       — sortable, selectable, paginated table
//! - `widgets::TimelineWidget`    — scrollable color-coded event stream
//! - `app::CompositApp`           — default wired layout
//! - `app::run()`                 — blocking event loop
//!
//! Phase 3 adds:
//! - `themes::ThemeRegistry`      — singleton named-theme registry
//! - `themes::Theme`              — full color palette
//! - `widgets::SparklineWidget`   — horizontal sparkline chart
//! - `widgets::BarChartWidget`    — vertical bar chart
//! - `widgets::FloatingOverlay`   — centered popup overlay
//! - `widgets::ConfirmDialog`     — Yes / No confirmation dialog
//! - `widgets::HelpDialog`        — keybinding reference dialog
//!
//! WL-052 adds:
//! - `mouse::MouseHandler`        — trait for mouse-aware widgets
//! - `mouse::DragState`           — drag origin/current/border tracking
//! - `mouse::PaneSplitter`        — draggable split-pane divider
//! - `mouse::ScrollState`         — scroll offset with wheel helpers
//! - `mouse::ContextMenu`         — right-click context menu popup
//! - `widgets::OutputWidget`      — scrollable output pane with mouse support
//!
//! WL-031 adds:
//! - `panels::ParetoFrontierPanel` — Pareto Frontier Visualization panel
//! - `panels::ParetoFrontierState` — mutable state for the Pareto panel
//! - `panels::ParetoAction`        — actions emitted by the Pareto panel
//! - `panels::AuditRecord`         — parsed routing audit record

pub mod app;
pub mod mouse;
pub mod panels;
pub mod themes;
pub mod widgets;

pub use app::{AgentRunRow, CompositApp};
pub use mouse::{
    BorderSide, ContextMenu, ContextMenuItem, DragState, MouseHandler, Orientation, PaneSplitter,
    ScrollState,
};
pub use panels::{AuditRecord, ParetoAction, ParetoFrontierPanel, ParetoFrontierState};
pub use themes::{Theme, ThemeRegistry};
pub use widgets::{
    BarChartWidget, CommandRegistry, ConfirmDialog, EventKind, FloatingOverlay, HelpBinding,
    HelpDialog, InteractiveInput, OutputWidget, SortDir, SparklineWidget, TableRow, TableWidget,
    TimelineEvent, TimelineWidget, ValidationState,
};
