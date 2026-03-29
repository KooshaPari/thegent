//! Widget library for thegent TUI.
//!
//! Phase 2 modules:
//! - `interactive_input`: Command input with history, autocomplete, validation
//! - `table`: Sortable, selectable, paginated table
//! - `timeline`: Scrollable color-coded event stream
//!
//! Phase 3 modules:
//! - `chart`: SparklineWidget and BarChartWidget
//! - `overlay`: FloatingOverlay, ConfirmDialog, HelpDialog
//!
//! WL-052 (mouse support) modules:
//! - `output`: Scrollable text-output pane with mouse-wheel integration

pub mod chart;
pub mod interactive_input;
pub mod output;
pub mod overlay;
pub mod table;
pub mod timeline;

pub use chart::{BarChartWidget, SparklineWidget};
pub use interactive_input::{CommandRegistry, InteractiveInput, ValidationState};
pub use output::OutputWidget;
pub use overlay::{ConfirmDialog, FloatingOverlay, HelpBinding, HelpDialog};
pub use table::{SortDir, TableRow, TableWidget};
pub use timeline::{EventKind, TimelineEvent, TimelineWidget};
