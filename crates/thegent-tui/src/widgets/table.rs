// SPDX-License-Identifier: MIT OR Apache-2.0
//! TableWidget — sortable, selectable, paginated table for any `TableRow` type.
//!
//! Features:
//! - Sortable column headers (keyboard cycle: None → Asc → Desc)
//! - Row selection with highlight and arrow-key / Page-Up / Page-Down navigation
//! - Pagination with configurable `page_size` and a page indicator
//! - Mouse scroll-wheel navigation via integrated `ScrollState`
//! - Generic over row data: implement `TableRow` for your type

use crossterm::event::{MouseEvent, MouseEventKind};
use ratatui::buffer::Buffer;
use ratatui::layout::{Constraint, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::Span;
use ratatui::widgets::{Block, Borders, Cell, Row, Table, TableState};

use crate::mouse::{MouseHandler, ScrollState};

// ---------------------------------------------------------------------------
// Public trait
// ---------------------------------------------------------------------------

/// A type that can be displayed as a table row.
pub trait TableRow: Clone {
    /// Column headers.  Must have the same length as `cells()`.
    fn headers() -> Vec<String>;

    /// Cell values for this row (same order as `headers()`).
    fn cells(&self) -> Vec<String>;
}

// ---------------------------------------------------------------------------
// Sort direction
// ---------------------------------------------------------------------------

/// Sort direction for a column.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SortDir {
    None,
    Asc,
    Desc,
}

impl SortDir {
    /// Cycle: None → Asc → Desc → None.
    pub fn cycle(&self) -> Self {
        match self {
            SortDir::None => SortDir::Asc,
            SortDir::Asc => SortDir::Desc,
            SortDir::Desc => SortDir::None,
        }
    }

    /// Indicator glyph shown in the column header.
    pub fn indicator(&self) -> &'static str {
        match self {
            SortDir::None => "  ",
            SortDir::Asc => " ^",
            SortDir::Desc => " v",
        }
    }
}

// ---------------------------------------------------------------------------
// TableWidget state
// ---------------------------------------------------------------------------

/// Stateful table widget.
pub struct TableWidget<T: TableRow> {
    /// All rows (unsorted).
    rows: Vec<T>,
    /// Sorted/filtered view: indices into `rows`.
    view: Vec<usize>,
    /// Currently selected row in `view`.
    selected: Option<usize>,
    /// Sort column index (`None` = no sort).
    sort_col: Option<usize>,
    /// Sort direction.
    sort_dir: SortDir,
    /// Rows per page.
    pub page_size: usize,
    /// Zero-based current page.
    page: usize,
    /// Ratatui internal table state (for highlight rendering).
    table_state: TableState,
    /// Mouse-wheel scroll state (tracks page-level offset for large datasets).
    scroll_state: ScrollState,
}

impl<T: TableRow> TableWidget<T> {
    /// Create a new `TableWidget` with the given page size.
    pub fn new(page_size: usize) -> Self {
        Self {
            rows: Vec::new(),
            view: Vec::new(),
            selected: None,
            sort_col: None,
            sort_dir: SortDir::None,
            page_size,
            page: 0,
            table_state: TableState::default(),
            scroll_state: ScrollState::new(page_size),
        }
    }

    /// Replace all rows and rebuild the view.
    pub fn set_rows(&mut self, rows: Vec<T>) {
        self.rows = rows;
        self.rebuild_view();
        // Clamp selection.
        if let Some(sel) = self.selected {
            if self.view.is_empty() {
                self.selected = None;
            } else {
                self.selected = Some(sel.min(self.view.len() - 1));
            }
        }
        self.clamp_page();
        self.sync_table_state();
        self.scroll_state.set_total(self.total_pages());
    }

    /// Number of total rows.
    pub fn row_count(&self) -> usize {
        self.rows.len()
    }

    /// Currently selected row (if any).
    pub fn selected_row(&self) -> Option<&T> {
        self.selected
            .and_then(|i| self.view.get(i))
            .and_then(|&ri| self.rows.get(ri))
    }

    /// Zero-based index of the selected row in `view`.
    pub fn selected_index(&self) -> Option<usize> {
        self.selected
    }

    /// Current page (0-based).
    pub fn current_page(&self) -> usize {
        self.page
    }

    /// Total number of pages.
    pub fn total_pages(&self) -> usize {
        if self.view.is_empty() {
            1
        } else {
            self.view.len().div_ceil(self.page_size)
        }
    }

    // ------------------------------------------------------------------
    // Navigation
    // ------------------------------------------------------------------

    /// Move selection down by one.
    pub fn select_next(&mut self) {
        if self.view.is_empty() {
            return;
        }
        let new_sel = match self.selected {
            None => 0,
            Some(i) => (i + 1).min(self.view.len() - 1),
        };
        self.selected = Some(new_sel);
        self.page = new_sel / self.page_size;
        self.sync_table_state();
    }

    /// Move selection up by one.
    pub fn select_prev(&mut self) {
        if self.view.is_empty() {
            return;
        }
        let new_sel = match self.selected {
            None => 0,
            Some(0) => 0,
            Some(i) => i - 1,
        };
        self.selected = Some(new_sel);
        self.page = new_sel / self.page_size;
        self.sync_table_state();
    }

    /// Page down.
    pub fn page_down(&mut self) {
        let total = self.total_pages();
        self.page = (self.page + 1).min(total.saturating_sub(1));
        // Move selection to first row of new page.
        let first = self.page * self.page_size;
        let last = (first + self.page_size - 1).min(self.view.len().saturating_sub(1));
        self.selected = if self.view.is_empty() {
            None
        } else {
            Some(first.min(last))
        };
        self.sync_table_state();
    }

    /// Page up.
    pub fn page_up(&mut self) {
        self.page = self.page.saturating_sub(1);
        let first = self.page * self.page_size;
        let last = (first + self.page_size - 1).min(self.view.len().saturating_sub(1));
        self.selected = if self.view.is_empty() {
            None
        } else {
            Some(first.min(last))
        };
        self.sync_table_state();
    }

    // ------------------------------------------------------------------
    // Sorting
    // ------------------------------------------------------------------

    /// Toggle sort on `col_idx`. Cycles None → Asc → Desc → None.
    pub fn toggle_sort(&mut self, col_idx: usize) {
        if self.sort_col == Some(col_idx) {
            self.sort_dir = self.sort_dir.cycle();
            if self.sort_dir == SortDir::None {
                self.sort_col = None;
            }
        } else {
            self.sort_col = Some(col_idx);
            self.sort_dir = SortDir::Asc;
        }
        self.rebuild_view();
        self.sync_table_state();
    }

    /// Current sort column index.
    pub fn sort_col(&self) -> Option<usize> {
        self.sort_col
    }

    /// Current sort direction.
    pub fn sort_dir(&self) -> &SortDir {
        &self.sort_dir
    }

    // ------------------------------------------------------------------
    // Mouse support
    // ------------------------------------------------------------------

    /// Handle a mouse event for this table.
    ///
    /// Scroll-wheel events navigate pages: `ScrollUp` → previous page,
    /// `ScrollDown` → next page.  Returns `true` when the event was consumed.
    pub fn handle_mouse(&mut self, event: MouseEvent, area: Rect) -> bool {
        match event.kind {
            MouseEventKind::ScrollUp => {
                self.page_up();
                true
            }
            MouseEventKind::ScrollDown => {
                self.page_down();
                true
            }
            _ => {
                // Delegate other events to the row-level scroll state.
                self.scroll_state.handle_mouse(event, area)
            }
        }
    }

    // ------------------------------------------------------------------
    // Internal helpers
    // ------------------------------------------------------------------

    fn rebuild_view(&mut self) {
        self.view = (0..self.rows.len()).collect();
        if let Some(col) = self.sort_col {
            let dir = self.sort_dir.clone();
            self.view.sort_by(|&a, &b| {
                let ca = self.rows[a].cells();
                let cb = self.rows[b].cells();
                let va = ca.get(col).map(|s| s.as_str()).unwrap_or("");
                let vb = cb.get(col).map(|s| s.as_str()).unwrap_or("");
                match dir {
                    SortDir::Asc => va.cmp(vb),
                    SortDir::Desc => vb.cmp(va),
                    SortDir::None => std::cmp::Ordering::Equal,
                }
            });
        }
    }

    fn clamp_page(&mut self) {
        let total = self.total_pages();
        if self.page >= total {
            self.page = total.saturating_sub(1);
        }
    }

    fn sync_table_state(&mut self) {
        let page_sel = self.selected.map(|s| s % self.page_size);
        self.table_state.select(page_sel);
    }

    /// Rows on the current page (as view indices).
    fn page_view_indices(&self) -> &[usize] {
        let start = self.page * self.page_size;
        let end = (start + self.page_size).min(self.view.len());
        &self.view[start..end]
    }

    /// Render into `buf` at `area`.
    pub fn render(&mut self, area: Rect, buf: &mut Buffer) {
        let headers = T::headers();
        let n_cols = headers.len();

        // Build header cells with sort indicators.
        let header_cells: Vec<Cell> = headers
            .iter()
            .enumerate()
            .map(|(i, h)| {
                let indicator = if self.sort_col == Some(i) {
                    self.sort_dir.indicator()
                } else {
                    "  "
                };
                Cell::from(Span::styled(
                    format!("{}{}", h, indicator),
                    Style::default()
                        .fg(Color::Yellow)
                        .add_modifier(Modifier::BOLD),
                ))
            })
            .collect();
        let header_row = Row::new(header_cells).height(1);

        // Build page rows.
        let page_indices = self.page_view_indices().to_vec();
        let data_rows: Vec<Row> = page_indices
            .iter()
            .enumerate()
            .map(|(page_pos, &row_idx)| {
                let row = &self.rows[row_idx];
                let cells: Vec<Cell> = row.cells().into_iter().map(Cell::from).collect();
                let is_selected = self.selected.map(|s| s % self.page_size) == Some(page_pos);
                let style = if is_selected {
                    Style::default()
                        .bg(Color::Blue)
                        .fg(Color::White)
                        .add_modifier(Modifier::BOLD)
                } else {
                    Style::default()
                };
                Row::new(cells).style(style).height(1)
            })
            .collect();

        // Equal-width columns.
        let col_width = if n_cols == 0 {
            Constraint::Percentage(100)
        } else {
            Constraint::Percentage(100 / n_cols as u16)
        };
        let widths: Vec<Constraint> = (0..n_cols).map(|_| col_width).collect();

        // Page indicator in title.
        let title = format!(
            " Table  Page {}/{}  ({} rows) ",
            self.page + 1,
            self.total_pages(),
            self.view.len()
        );

        let block = Block::default().borders(Borders::ALL).title(title);

        let table = Table::new(data_rows, widths)
            .header(header_row)
            .block(block)
            .row_highlight_style(
                Style::default()
                    .bg(Color::Blue)
                    .fg(Color::White)
                    .add_modifier(Modifier::BOLD),
            );

        ratatui::widgets::StatefulWidget::render(table, area, buf, &mut self.table_state);
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Clone, Debug)]
    struct AgentRun {
        id: String,
        status: String,
        duration_s: u32,
    }

    impl TableRow for AgentRun {
        fn headers() -> Vec<String> {
            vec![
                "ID".to_string(),
                "Status".to_string(),
                "Duration(s)".to_string(),
            ]
        }

        fn cells(&self) -> Vec<String> {
            vec![
                self.id.clone(),
                self.status.clone(),
                self.duration_s.to_string(),
            ]
        }
    }

    fn sample_rows(n: usize) -> Vec<AgentRun> {
        (0..n)
            .map(|i| AgentRun {
                id: format!("run-{:03}", i),
                status: if i % 2 == 0 {
                    "done".to_string()
                } else {
                    "error".to_string()
                },
                duration_s: (i as u32 * 3 + 1),
            })
            .collect()
    }

    #[test]
    fn test_set_rows_populates_view() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(10));
        assert_eq!(t.row_count(), 10);
    }

    #[test]
    fn test_select_next_advances() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(3));
        t.select_next();
        assert_eq!(t.selected_index(), Some(0));
        t.select_next();
        assert_eq!(t.selected_index(), Some(1));
    }

    #[test]
    fn test_select_prev_clamps_at_zero() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(3));
        t.select_next();
        t.select_prev();
        assert_eq!(t.selected_index(), Some(0));
        t.select_prev();
        assert_eq!(t.selected_index(), Some(0));
    }

    #[test]
    fn test_select_next_clamps_at_end() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(3));
        t.select_next();
        t.select_next();
        t.select_next();
        t.select_next();
        assert_eq!(t.selected_index(), Some(2));
    }

    #[test]
    fn test_selected_row_returns_correct_row() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(3));
        t.select_next(); // index 0
        let row = t.selected_row().unwrap();
        assert_eq!(row.id, "run-000");
    }

    #[test]
    fn test_page_down_up() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(3);
        t.set_rows(sample_rows(9));
        assert_eq!(t.current_page(), 0);
        assert_eq!(t.total_pages(), 3);
        t.page_down();
        assert_eq!(t.current_page(), 1);
        t.page_down();
        assert_eq!(t.current_page(), 2);
        t.page_down(); // clamp
        assert_eq!(t.current_page(), 2);
        t.page_up();
        assert_eq!(t.current_page(), 1);
        t.page_up();
        assert_eq!(t.current_page(), 0);
        t.page_up(); // clamp
        assert_eq!(t.current_page(), 0);
    }

    #[test]
    fn test_total_pages_empty() {
        let t: TableWidget<AgentRun> = TableWidget::new(5);
        assert_eq!(t.total_pages(), 1);
    }

    #[test]
    fn test_total_pages_exact_multiple() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(3);
        t.set_rows(sample_rows(9));
        assert_eq!(t.total_pages(), 3);
    }

    #[test]
    fn test_total_pages_partial() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(3);
        t.set_rows(sample_rows(7));
        assert_eq!(t.total_pages(), 3);
    }

    #[test]
    fn test_sort_asc() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(10);
        t.set_rows(vec![
            AgentRun {
                id: "c".to_string(),
                status: "done".to_string(),
                duration_s: 3,
            },
            AgentRun {
                id: "a".to_string(),
                status: "done".to_string(),
                duration_s: 1,
            },
            AgentRun {
                id: "b".to_string(),
                status: "done".to_string(),
                duration_s: 2,
            },
        ]);
        t.toggle_sort(0); // sort by ID asc
        assert_eq!(t.sort_dir(), &SortDir::Asc);
        let ids: Vec<String> = t.view.iter().map(|&i| t.rows[i].id.clone()).collect();
        assert_eq!(ids, vec!["a", "b", "c"]);
    }

    #[test]
    fn test_sort_desc() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(10);
        t.set_rows(vec![
            AgentRun {
                id: "c".to_string(),
                status: "done".to_string(),
                duration_s: 3,
            },
            AgentRun {
                id: "a".to_string(),
                status: "done".to_string(),
                duration_s: 1,
            },
            AgentRun {
                id: "b".to_string(),
                status: "done".to_string(),
                duration_s: 2,
            },
        ]);
        t.toggle_sort(0); // Asc
        t.toggle_sort(0); // Desc
        assert_eq!(t.sort_dir(), &SortDir::Desc);
        let ids: Vec<String> = t.view.iter().map(|&i| t.rows[i].id.clone()).collect();
        assert_eq!(ids, vec!["c", "b", "a"]);
    }

    #[test]
    fn test_sort_cycle_resets() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(10);
        t.set_rows(sample_rows(3));
        t.toggle_sort(0); // Asc
        t.toggle_sort(0); // Desc
        t.toggle_sort(0); // None
        assert_eq!(t.sort_dir(), &SortDir::None);
        assert_eq!(t.sort_col(), None);
    }

    #[test]
    fn test_sort_dir_cycle() {
        assert_eq!(SortDir::None.cycle(), SortDir::Asc);
        assert_eq!(SortDir::Asc.cycle(), SortDir::Desc);
        assert_eq!(SortDir::Desc.cycle(), SortDir::None);
    }

    #[test]
    fn test_headers_and_cells() {
        let headers = AgentRun::headers();
        assert_eq!(headers.len(), 3);
        let row = AgentRun {
            id: "r1".to_string(),
            status: "ok".to_string(),
            duration_s: 42,
        };
        let cells = row.cells();
        assert_eq!(cells[0], "r1");
        assert_eq!(cells[1], "ok");
        assert_eq!(cells[2], "42");
    }

    #[test]
    fn test_set_rows_clamps_selection() {
        let mut t: TableWidget<AgentRun> = TableWidget::new(5);
        t.set_rows(sample_rows(5));
        // Select last row: need 5 calls from None to reach index 4 (None→0→1→2→3→4)
        for _ in 0..5 {
            t.select_next();
        }
        assert_eq!(t.selected_index(), Some(4));
        // Reduce rows to 2
        t.set_rows(sample_rows(2));
        // Selection must be clamped: 4.min(2-1) = 4.min(1) = 1
        assert_eq!(t.selected_index(), Some(1));
    }
}
