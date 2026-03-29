//! Mouse event handling for thegent TUI — WL-052.
//!
//! Provides:
//! - `MouseHandler` trait — unified interface for widgets that respond to mouse events
//! - `DragState` — tracks an active drag: origin, current position, and which border
//! - `PaneSplitter` — resizable split pane (horizontal or vertical) driven by mouse drag
//! - `ScrollState` — scroll offset management with mouse-wheel helpers
//! - `ContextMenuItem` / `ContextMenu` — right-click context menu popup

use crossterm::event::{MouseButton, MouseEvent, MouseEventKind};
use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Clear, Paragraph, Widget};

// ---------------------------------------------------------------------------
// MouseHandler trait
// ---------------------------------------------------------------------------

/// Implemented by any widget that reacts to ratatui/crossterm mouse events.
///
/// `area` is the `Rect` the widget occupies in the current frame.
///
/// Returns `true` when the event was consumed by this handler (preventing
/// further propagation to widgets underneath).
pub trait MouseHandler {
    fn handle_mouse(&mut self, event: MouseEvent, area: Rect) -> bool;
}

// ---------------------------------------------------------------------------
// Helper: point-in-rect
// ---------------------------------------------------------------------------

fn point_in_rect(col: u16, row: u16, rect: Rect) -> bool {
    col >= rect.x && col < rect.x + rect.width && row >= rect.y && row < rect.y + rect.height
}

// ---------------------------------------------------------------------------
// BorderSide — which border of the pane is being dragged
// ---------------------------------------------------------------------------

/// Which split-border is currently being dragged.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BorderSide {
    /// The vertical border between left and right panes.
    Vertical,
    /// The horizontal border between top and bottom panes.
    Horizontal,
}

// ---------------------------------------------------------------------------
// DragState
// ---------------------------------------------------------------------------

/// Tracks an active drag operation: starting cell, current cell, and which
/// border of the split is being moved.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DragState {
    /// Terminal column where the drag started.
    pub origin_col: u16,
    /// Terminal row where the drag started.
    pub origin_row: u16,
    /// Current drag column.
    pub current_col: u16,
    /// Current drag row.
    pub current_row: u16,
    /// Which border is being dragged.
    pub border: BorderSide,
}

impl DragState {
    /// Create a new `DragState` anchored at (`col`, `row`).
    pub fn new(col: u16, row: u16, border: BorderSide) -> Self {
        Self {
            origin_col: col,
            origin_row: row,
            current_col: col,
            current_row: row,
            border,
        }
    }

    /// Update the current drag position.
    pub fn update(&mut self, col: u16, row: u16) {
        self.current_col = col;
        self.current_row = row;
    }

    /// Column delta since drag start.
    pub fn delta_col(&self) -> i32 {
        self.current_col as i32 - self.origin_col as i32
    }

    /// Row delta since drag start.
    pub fn delta_row(&self) -> i32 {
        self.current_row as i32 - self.origin_row as i32
    }
}

// ---------------------------------------------------------------------------
// Orientation
// ---------------------------------------------------------------------------

/// Whether the `PaneSplitter` divides the area left/right or top/bottom.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Orientation {
    /// Vertical split: left pane | right pane.
    Horizontal,
    /// Horizontal split: top pane / bottom pane.
    Vertical,
}

// ---------------------------------------------------------------------------
// PaneSplitter
// ---------------------------------------------------------------------------

/// A resizable two-pane divider.
///
/// `ratio` (0.0 – 1.0) controls how much of the parent `Rect` the first pane
/// occupies.  Dragging the separator changes the ratio in real time.
pub struct PaneSplitter {
    /// Fraction of the total area allocated to the first (left/top) pane.
    pub ratio: f32,
    /// Split orientation.
    pub orientation: Orientation,
    /// Active drag, if any.
    drag: Option<DragState>,
    /// Width of the separator bar in terminal cells (always 1 in practice).
    pub separator_width: u16,
    /// Colour of the separator line.
    pub separator_color: Color,
    /// Colour of the separator while being dragged.
    pub separator_drag_color: Color,
}

impl PaneSplitter {
    /// Construct a `PaneSplitter` with the given `ratio` and `orientation`.
    pub fn new(ratio: f32, orientation: Orientation) -> Self {
        Self {
            ratio: ratio.clamp(0.05, 0.95),
            orientation,
            drag: None,
            separator_width: 1,
            separator_color: Color::DarkGray,
            separator_drag_color: Color::Yellow,
        }
    }

    /// Whether a drag is currently in progress.
    pub fn is_dragging(&self) -> bool {
        self.drag.is_some()
    }

    /// Compute the two child `Rect`s for the given parent `area`.
    ///
    /// Returns `(first_pane, second_pane)` where the separator row/column is
    /// consumed by the splitter itself.
    pub fn split(&self, area: Rect) -> (Rect, Rect) {
        match self.orientation {
            Orientation::Horizontal => {
                let split_col = (area.x as f32
                    + (area.width.saturating_sub(self.separator_width)) as f32 * self.ratio)
                    as u16;
                let left_width = split_col.saturating_sub(area.x);
                let right_x = (split_col + self.separator_width).min(area.x + area.width);
                let right_width = (area.x + area.width).saturating_sub(right_x);
                (
                    Rect {
                        x: area.x,
                        y: area.y,
                        width: left_width,
                        height: area.height,
                    },
                    Rect {
                        x: right_x,
                        y: area.y,
                        width: right_width,
                        height: area.height,
                    },
                )
            }
            Orientation::Vertical => {
                let split_row = (area.y as f32
                    + (area.height.saturating_sub(self.separator_width)) as f32 * self.ratio)
                    as u16;
                let top_height = split_row.saturating_sub(area.y);
                let bottom_y = (split_row + self.separator_width).min(area.y + area.height);
                let bottom_height = (area.y + area.height).saturating_sub(bottom_y);
                (
                    Rect {
                        x: area.x,
                        y: area.y,
                        width: area.width,
                        height: top_height,
                    },
                    Rect {
                        x: area.x,
                        y: bottom_y,
                        width: area.width,
                        height: bottom_height,
                    },
                )
            }
        }
    }

    /// Render the separator into `buf` at `area`.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let color = if self.is_dragging() {
            self.separator_drag_color
        } else {
            self.separator_color
        };
        let style = Style::default().fg(color);

        match self.orientation {
            Orientation::Horizontal => {
                let (left, _) = self.split(area);
                let sep_col = left.x + left.width;
                if sep_col >= area.x + area.width {
                    return;
                }
                for row in area.y..area.y + area.height {
                    if let Some(cell) = buf.cell_mut((sep_col, row)) {
                        cell.set_char('│');
                        cell.set_style(style);
                    }
                }
            }
            Orientation::Vertical => {
                let (top, _) = self.split(area);
                let sep_row = top.y + top.height;
                if sep_row >= area.y + area.height {
                    return;
                }
                for col in area.x..area.x + area.width {
                    if let Some(cell) = buf.cell_mut((col, sep_row)) {
                        cell.set_char('─');
                        cell.set_style(style);
                    }
                }
            }
        }
    }

    /// Determine the separator position (column for Horizontal, row for Vertical).
    fn separator_pos(&self, area: Rect) -> u16 {
        match self.orientation {
            Orientation::Horizontal => {
                let (left, _) = self.split(area);
                left.x + left.width
            }
            Orientation::Vertical => {
                let (top, _) = self.split(area);
                top.y + top.height
            }
        }
    }

    /// Return `true` if the given coordinate is over the separator (within 1 cell tolerance).
    pub fn is_near_separator(&self, col: u16, row: u16, area: Rect) -> bool {
        let pos = self.separator_pos(area);
        match self.orientation {
            Orientation::Horizontal => point_in_rect(col, row, area) && col.abs_diff(pos) <= 1,
            Orientation::Vertical => point_in_rect(col, row, area) && row.abs_diff(pos) <= 1,
        }
    }

    /// Update `ratio` from the current drag position relative to `area`.
    fn apply_drag(&mut self, area: Rect) {
        if let Some(ref drag) = self.drag {
            let new_ratio = match self.orientation {
                Orientation::Horizontal => {
                    let available = area.width.saturating_sub(self.separator_width) as f32;
                    if available == 0.0 {
                        return;
                    }
                    (drag.current_col.saturating_sub(area.x)) as f32 / available
                }
                Orientation::Vertical => {
                    let available = area.height.saturating_sub(self.separator_width) as f32;
                    if available == 0.0 {
                        return;
                    }
                    (drag.current_row.saturating_sub(area.y)) as f32 / available
                }
            };
            self.ratio = new_ratio.clamp(0.05, 0.95);
        }
    }
}

impl MouseHandler for PaneSplitter {
    fn handle_mouse(&mut self, event: MouseEvent, area: Rect) -> bool {
        let col = event.column;
        let row = event.row;

        match event.kind {
            MouseEventKind::Down(MouseButton::Left) => {
                if self.is_near_separator(col, row, area) {
                    let border = match self.orientation {
                        Orientation::Horizontal => BorderSide::Vertical,
                        Orientation::Vertical => BorderSide::Horizontal,
                    };
                    self.drag = Some(DragState::new(col, row, border));
                    return true;
                }
                false
            }
            MouseEventKind::Drag(MouseButton::Left) => {
                if let Some(ref mut drag) = self.drag {
                    drag.update(col, row);
                    self.apply_drag(area);
                    true
                } else {
                    false
                }
            }
            MouseEventKind::Up(MouseButton::Left) => {
                if self.drag.is_some() {
                    if let Some(ref mut drag) = self.drag {
                        drag.update(col, row);
                    }
                    self.apply_drag(area);
                    self.drag = None;
                    true
                } else {
                    false
                }
            }
            _ => false,
        }
    }
}

// ---------------------------------------------------------------------------
// ScrollState
// ---------------------------------------------------------------------------

/// Manages a scroll offset for a widget.
///
/// `offset` is the number of items (rows/lines) scrolled from the top.
/// `total` tracks the total number of scrollable items for clamping.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ScrollState {
    offset: usize,
    total: usize,
    page_size: usize,
}

impl ScrollState {
    /// Create a `ScrollState` with the given page size (visible rows).
    pub fn new(page_size: usize) -> Self {
        Self {
            offset: 0,
            total: 0,
            page_size,
        }
    }

    /// Current scroll offset (number of rows from the top).
    pub fn offset(&self) -> usize {
        self.offset
    }

    /// Update the total number of scrollable items (triggers clamp).
    pub fn set_total(&mut self, total: usize) {
        self.total = total;
        self.clamp();
    }

    /// Update the visible page size.
    pub fn set_page_size(&mut self, page_size: usize) {
        self.page_size = page_size;
        self.clamp();
    }

    /// Scroll up by `delta` rows (toward the top).
    pub fn scroll_up(&mut self) {
        self.offset = self.offset.saturating_sub(1);
    }

    /// Scroll down by `delta` rows (toward the bottom).
    pub fn scroll_down(&mut self) {
        self.offset = (self.offset + 1).min(self.max_offset());
    }

    /// Apply a signed scroll delta: positive = down, negative = up.
    pub fn handle_scroll(&mut self, delta: i32) {
        if delta > 0 {
            for _ in 0..delta {
                self.scroll_down();
            }
        } else {
            for _ in 0..(-delta) {
                self.scroll_up();
            }
        }
    }

    /// Jump to the top.
    pub fn reset(&mut self) {
        self.offset = 0;
    }

    /// Jump to the bottom.
    pub fn scroll_to_bottom(&mut self) {
        self.offset = self.max_offset();
    }

    fn max_offset(&self) -> usize {
        self.total.saturating_sub(self.page_size)
    }

    fn clamp(&mut self) {
        let max = self.max_offset();
        if self.offset > max {
            self.offset = max;
        }
    }
}

impl MouseHandler for ScrollState {
    fn handle_mouse(&mut self, event: MouseEvent, area: Rect) -> bool {
        if !point_in_rect(event.column, event.row, area) {
            return false;
        }
        match event.kind {
            MouseEventKind::ScrollUp => {
                self.scroll_up();
                true
            }
            MouseEventKind::ScrollDown => {
                self.scroll_down();
                true
            }
            _ => false,
        }
    }
}

// ---------------------------------------------------------------------------
// ContextMenuItem
// ---------------------------------------------------------------------------

/// A single item in a right-click context menu.
#[derive(Debug, Clone)]
pub struct ContextMenuItem {
    /// Display label.
    pub label: String,
    /// Keyboard shortcut character (shown beside the label).
    pub key: char,
}

impl ContextMenuItem {
    /// Create a `ContextMenuItem`.
    pub fn new(label: impl Into<String>, key: char) -> Self {
        Self {
            label: label.into(),
            key,
        }
    }
}

// ---------------------------------------------------------------------------
// ContextMenu
// ---------------------------------------------------------------------------

/// A floating right-click context menu popup.
///
/// Call [`ContextMenu::show`] to make it visible at a given position.
/// Call [`ContextMenu::handle_mouse`] / [`ContextMenu::handle_key_char`] to
/// interact with it.
/// After [`handle_mouse`] or [`handle_key_char`] returns, inspect
/// [`ContextMenu::selected`] for the chosen item index.
pub struct ContextMenu {
    /// Menu items.
    items: Vec<ContextMenuItem>,
    /// Index of the currently highlighted item.
    pub highlighted: usize,
    /// Column where the popup should appear.
    popup_col: u16,
    /// Row where the popup should appear.
    popup_row: u16,
    /// Whether the menu is currently visible.
    pub visible: bool,
    /// Index of the item that was activated, if any.
    pub selected: Option<usize>,
}

impl ContextMenu {
    /// Create a `ContextMenu` with the given items (initially hidden).
    pub fn new(items: Vec<ContextMenuItem>) -> Self {
        Self {
            items,
            highlighted: 0,
            popup_col: 0,
            popup_row: 0,
            visible: false,
            selected: None,
        }
    }

    /// Number of items in the menu.
    pub fn item_count(&self) -> usize {
        self.items.len()
    }

    /// Show the context menu at the given terminal position.
    pub fn show(&mut self, col: u16, row: u16) {
        self.popup_col = col;
        self.popup_row = row;
        self.highlighted = 0;
        self.selected = None;
        self.visible = true;
    }

    /// Hide the context menu and clear any pending selection.
    pub fn hide(&mut self) {
        self.visible = false;
        self.selected = None;
    }

    /// Move highlight up by one item (wrapping).
    pub fn highlight_prev(&mut self) {
        if self.items.is_empty() {
            return;
        }
        self.highlighted = self
            .highlighted
            .checked_sub(1)
            .unwrap_or(self.items.len() - 1);
    }

    /// Move highlight down by one item (wrapping).
    pub fn highlight_next(&mut self) {
        if self.items.is_empty() {
            return;
        }
        self.highlighted = (self.highlighted + 1) % self.items.len();
    }

    /// Activate the currently highlighted item.
    pub fn confirm(&mut self) {
        if !self.items.is_empty() {
            self.selected = Some(self.highlighted);
        }
        self.visible = false;
    }

    /// Handle a keyboard character shortcut. Returns `true` if the char
    /// matched an item's key.
    pub fn handle_key_char(&mut self, c: char) -> bool {
        for (i, item) in self.items.iter().enumerate() {
            if item.key == c {
                self.selected = Some(i);
                self.visible = false;
                return true;
            }
        }
        false
    }

    /// Compute the bounding `Rect` of the popup given a maximum available area.
    fn popup_rect(&self, available: Rect) -> Rect {
        let width = self
            .items
            .iter()
            .map(|it| it.label.len() + 6) // "  x  label  "
            .max()
            .unwrap_or(10) as u16;
        let height = self.items.len() as u16 + 2; // border top + bottom

        let x = self
            .popup_col
            .min(available.x + available.width.saturating_sub(width));
        let y = self
            .popup_row
            .min(available.y + available.height.saturating_sub(height));

        Rect {
            x: x.max(available.x),
            y: y.max(available.y),
            width: width.min(available.width),
            height: height.min(available.height),
        }
    }

    /// Render the context menu popup into `buf`.  `available` is the total
    /// terminal area used for boundary clamping.
    pub fn render(&self, available: Rect, buf: &mut Buffer) {
        if !self.visible || self.items.is_empty() {
            return;
        }

        let popup = self.popup_rect(available);
        Clear.render(popup, buf);

        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(Color::White));
        let inner = block.inner(popup);
        block.render(popup, buf);

        for (i, item) in self.items.iter().enumerate() {
            let y = inner.y + i as u16;
            if y >= inner.y + inner.height {
                break;
            }
            let is_highlighted = i == self.highlighted;
            let style = if is_highlighted {
                Style::default()
                    .fg(Color::Black)
                    .bg(Color::White)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };

            let text = format!(" {} {}", item.key, item.label);
            let line = Line::from(Span::styled(text, style));
            let row_rect = Rect {
                x: inner.x,
                y,
                width: inner.width,
                height: 1,
            };
            Paragraph::new(line).render(row_rect, buf);
        }
    }
}

impl MouseHandler for ContextMenu {
    /// Handle a mouse event against this context menu.
    ///
    /// - `Down(Right)` anywhere → if visible, hide; otherwise caller should
    ///   call [`show`] at the event coordinates.
    /// - `Down(Left)` on a menu item → activate it.
    /// - `Down(Left)` outside the popup → hide without selection.
    /// - `Move` within popup → update highlight.
    fn handle_mouse(&mut self, event: MouseEvent, available: Rect) -> bool {
        let col = event.column;
        let row = event.row;

        match event.kind {
            MouseEventKind::Down(MouseButton::Right) => {
                self.show(col, row);
                true
            }
            MouseEventKind::Down(MouseButton::Left) => {
                if !self.visible {
                    return false;
                }
                let popup = self.popup_rect(available);
                if !point_in_rect(col, row, popup) {
                    self.hide();
                    return true;
                }
                let inner = Block::default().borders(Borders::ALL).inner(popup);
                if row >= inner.y && row < inner.y + inner.height {
                    let idx = (row - inner.y) as usize;
                    if idx < self.items.len() {
                        self.highlighted = idx;
                        self.confirm();
                        return true;
                    }
                }
                false
            }
            MouseEventKind::Moved => {
                if !self.visible {
                    return false;
                }
                let popup = self.popup_rect(available);
                if !point_in_rect(col, row, popup) {
                    return false;
                }
                let inner = Block::default().borders(Borders::ALL).inner(popup);
                if row >= inner.y && row < inner.y + inner.height {
                    let idx = (row - inner.y) as usize;
                    if idx < self.items.len() {
                        self.highlighted = idx;
                        return true;
                    }
                }
                false
            }
            _ => false,
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crossterm::event::{KeyModifiers, MouseEvent, MouseEventKind};
    use ratatui::backend::TestBackend;
    use ratatui::Terminal;

    // Helper: build a MouseEvent at (col, row)
    fn mouse_event(kind: MouseEventKind, col: u16, row: u16) -> MouseEvent {
        MouseEvent {
            kind,
            column: col,
            row,
            modifiers: KeyModifiers::NONE,
        }
    }

    // -----------------------------------------------------------------------
    // DragState tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_drag_state_new_sets_origin() {
        let drag = DragState::new(10, 5, BorderSide::Vertical);
        assert_eq!(drag.origin_col, 10);
        assert_eq!(drag.current_col, 10);
        assert_eq!(drag.border, BorderSide::Vertical);
    }

    #[test]
    fn test_drag_state_update_changes_current() {
        let mut drag = DragState::new(10, 5, BorderSide::Horizontal);
        drag.update(20, 8);
        assert_eq!(drag.current_col, 20);
        assert_eq!(drag.current_row, 8);
    }

    #[test]
    fn test_drag_state_delta_col() {
        let mut drag = DragState::new(10, 5, BorderSide::Vertical);
        drag.update(15, 5);
        assert_eq!(drag.delta_col(), 5);
    }

    #[test]
    fn test_drag_state_delta_row() {
        let mut drag = DragState::new(10, 5, BorderSide::Horizontal);
        drag.update(10, 9);
        assert_eq!(drag.delta_row(), 4);
    }

    // -----------------------------------------------------------------------
    // PaneSplitter — split geometry
    // -----------------------------------------------------------------------

    fn area(w: u16, h: u16) -> Rect {
        Rect {
            x: 0,
            y: 0,
            width: w,
            height: h,
        }
    }

    #[test]
    fn test_splitter_horizontal_split_ratio_half() {
        let sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let (left, right) = sp.split(area(80, 24));
        // left + sep + right = 80
        assert_eq!(left.width + 1 + right.width, 80);
        // left should be ~40 columns (half of 79 rounded)
        assert!(left.width >= 38 && left.width <= 41);
    }

    #[test]
    fn test_splitter_vertical_split_ratio_third() {
        let sp = PaneSplitter::new(0.333, Orientation::Vertical);
        let (top, bottom) = sp.split(area(80, 30));
        assert_eq!(top.height + 1 + bottom.height, 30);
        assert!(top.height >= 8 && top.height <= 12);
    }

    #[test]
    fn test_splitter_horizontal_panes_same_height() {
        let sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let (left, right) = sp.split(area(80, 24));
        assert_eq!(left.height, 24);
        assert_eq!(right.height, 24);
    }

    #[test]
    fn test_splitter_vertical_panes_same_width() {
        let sp = PaneSplitter::new(0.5, Orientation::Vertical);
        let (top, bottom) = sp.split(area(80, 24));
        assert_eq!(top.width, 80);
        assert_eq!(bottom.width, 80);
    }

    #[test]
    fn test_splitter_ratio_clamped() {
        let sp = PaneSplitter::new(2.0, Orientation::Horizontal);
        assert!(sp.ratio <= 0.95);
        let sp2 = PaneSplitter::new(-1.0, Orientation::Horizontal);
        assert!(sp2.ratio >= 0.05);
    }

    // -----------------------------------------------------------------------
    // PaneSplitter — mouse interaction
    // -----------------------------------------------------------------------

    #[test]
    fn test_splitter_drag_start_on_separator() {
        let mut sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let a = area(80, 24);
        let (left, _) = sp.split(a);
        let sep_col = left.x + left.width;
        let ev = mouse_event(MouseEventKind::Down(MouseButton::Left), sep_col, 5);
        let consumed = sp.handle_mouse(ev, a);
        assert!(consumed);
        assert!(sp.is_dragging());
    }

    #[test]
    fn test_splitter_drag_away_from_separator_not_consumed() {
        let mut sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let a = area(80, 24);
        let ev = mouse_event(MouseEventKind::Down(MouseButton::Left), 5, 5);
        let consumed = sp.handle_mouse(ev, a);
        assert!(!consumed);
        assert!(!sp.is_dragging());
    }

    #[test]
    fn test_splitter_drag_changes_ratio() {
        let mut sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let a = area(80, 24);

        // Start drag on separator
        let (left, _) = sp.split(a);
        let sep_col = left.x + left.width;
        sp.handle_mouse(
            mouse_event(MouseEventKind::Down(MouseButton::Left), sep_col, 5),
            a,
        );

        // Drag to column 60 (ratio should increase toward ~60/79 ≈ 0.76)
        sp.handle_mouse(
            mouse_event(MouseEventKind::Drag(MouseButton::Left), 60, 5),
            a,
        );
        assert!(sp.ratio > 0.5, "ratio should increase when dragging right");
    }

    #[test]
    fn test_splitter_drag_release_ends_drag() {
        let mut sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let a = area(80, 24);

        let (left, _) = sp.split(a);
        let sep_col = left.x + left.width;
        sp.handle_mouse(
            mouse_event(MouseEventKind::Down(MouseButton::Left), sep_col, 5),
            a,
        );
        assert!(sp.is_dragging());

        sp.handle_mouse(
            mouse_event(MouseEventKind::Up(MouseButton::Left), sep_col, 5),
            a,
        );
        assert!(!sp.is_dragging());
    }

    #[test]
    fn test_splitter_render_does_not_panic() {
        let sp = PaneSplitter::new(0.5, Orientation::Horizontal);
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                sp.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    #[test]
    fn test_splitter_vertical_render_does_not_panic() {
        let sp = PaneSplitter::new(0.5, Orientation::Vertical);
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                sp.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    // -----------------------------------------------------------------------
    // ScrollState tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_scroll_state_initial_offset_zero() {
        let s = ScrollState::new(10);
        assert_eq!(s.offset(), 0);
    }

    #[test]
    fn test_scroll_state_scroll_down_increases_offset() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_down();
        assert_eq!(s.offset(), 1);
        s.scroll_down();
        assert_eq!(s.offset(), 2);
    }

    #[test]
    fn test_scroll_state_scroll_up_decreases_offset() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_down();
        s.scroll_down();
        s.scroll_up();
        assert_eq!(s.offset(), 1);
    }

    #[test]
    fn test_scroll_state_scroll_up_clamps_at_zero() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_up();
        s.scroll_up();
        assert_eq!(s.offset(), 0);
    }

    #[test]
    fn test_scroll_state_scroll_down_clamps_at_max() {
        let mut s = ScrollState::new(5);
        s.set_total(10);
        for _ in 0..20 {
            s.scroll_down();
        }
        // max_offset = 10 - 5 = 5
        assert_eq!(s.offset(), 5);
    }

    #[test]
    fn test_scroll_state_reset() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_down();
        s.scroll_down();
        s.reset();
        assert_eq!(s.offset(), 0);
    }

    #[test]
    fn test_scroll_state_scroll_to_bottom() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_to_bottom();
        assert_eq!(s.offset(), 15);
    }

    #[test]
    fn test_scroll_state_handle_scroll_positive() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.handle_scroll(3);
        assert_eq!(s.offset(), 3);
    }

    #[test]
    fn test_scroll_state_handle_scroll_negative() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.handle_scroll(5);
        s.handle_scroll(-2);
        assert_eq!(s.offset(), 3);
    }

    #[test]
    fn test_scroll_state_mouse_scroll_up_in_area() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        s.scroll_down();
        s.scroll_down();
        let ev = mouse_event(MouseEventKind::ScrollUp, 5, 5);
        let consumed = s.handle_mouse(
            ev,
            Rect {
                x: 0,
                y: 0,
                width: 80,
                height: 24,
            },
        );
        assert!(consumed);
        assert_eq!(s.offset(), 1);
    }

    #[test]
    fn test_scroll_state_mouse_scroll_down_in_area() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        let ev = mouse_event(MouseEventKind::ScrollDown, 5, 5);
        let consumed = s.handle_mouse(
            ev,
            Rect {
                x: 0,
                y: 0,
                width: 80,
                height: 24,
            },
        );
        assert!(consumed);
        assert_eq!(s.offset(), 1);
    }

    #[test]
    fn test_scroll_state_mouse_outside_area_not_consumed() {
        let mut s = ScrollState::new(5);
        s.set_total(20);
        let ev = mouse_event(MouseEventKind::ScrollDown, 100, 100);
        let consumed = s.handle_mouse(
            ev,
            Rect {
                x: 0,
                y: 0,
                width: 80,
                height: 24,
            },
        );
        assert!(!consumed);
        assert_eq!(s.offset(), 0);
    }

    // -----------------------------------------------------------------------
    // ContextMenu tests
    // -----------------------------------------------------------------------

    fn sample_menu() -> ContextMenu {
        ContextMenu::new(vec![
            ContextMenuItem::new("Run agent", 'r'),
            ContextMenuItem::new("Stop agent", 's'),
            ContextMenuItem::new("View logs", 'v'),
        ])
    }

    fn full_area() -> Rect {
        Rect {
            x: 0,
            y: 0,
            width: 80,
            height: 24,
        }
    }

    #[test]
    fn test_context_menu_initial_state() {
        let m = sample_menu();
        assert!(!m.visible);
        assert_eq!(m.item_count(), 3);
        assert_eq!(m.selected, None);
    }

    #[test]
    fn test_context_menu_show_hide() {
        let mut m = sample_menu();
        m.show(10, 5);
        assert!(m.visible);
        m.hide();
        assert!(!m.visible);
    }

    #[test]
    fn test_context_menu_right_click_shows_menu() {
        let mut m = sample_menu();
        let ev = mouse_event(MouseEventKind::Down(MouseButton::Right), 20, 10);
        let consumed = m.handle_mouse(ev, full_area());
        assert!(consumed);
        assert!(m.visible);
        assert_eq!(m.popup_col, 20);
        assert_eq!(m.popup_row, 10);
    }

    #[test]
    fn test_context_menu_highlight_next_prev() {
        let mut m = sample_menu();
        m.show(0, 0);
        assert_eq!(m.highlighted, 0);
        m.highlight_next();
        assert_eq!(m.highlighted, 1);
        m.highlight_next();
        assert_eq!(m.highlighted, 2);
        m.highlight_next(); // wraps
        assert_eq!(m.highlighted, 0);
        m.highlight_prev(); // wraps back
        assert_eq!(m.highlighted, 2);
    }

    #[test]
    fn test_context_menu_confirm_sets_selected() {
        let mut m = sample_menu();
        m.show(0, 0);
        m.highlighted = 1;
        m.confirm();
        assert_eq!(m.selected, Some(1));
        assert!(!m.visible);
    }

    #[test]
    fn test_context_menu_key_char_matches() {
        let mut m = sample_menu();
        m.show(0, 0);
        let matched = m.handle_key_char('s');
        assert!(matched);
        assert_eq!(m.selected, Some(1));
        assert!(!m.visible);
    }

    #[test]
    fn test_context_menu_key_char_no_match() {
        let mut m = sample_menu();
        m.show(0, 0);
        let matched = m.handle_key_char('z');
        assert!(!matched);
        assert_eq!(m.selected, None);
    }

    #[test]
    fn test_context_menu_render_does_not_panic_hidden() {
        let m = sample_menu();
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                m.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    #[test]
    fn test_context_menu_render_does_not_panic_visible() {
        let mut m = sample_menu();
        m.show(10, 5);
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                m.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    #[test]
    fn test_context_menu_click_outside_hides() {
        let mut m = sample_menu();
        m.show(10, 5);
        // Click far away from the menu popup
        let ev = mouse_event(MouseEventKind::Down(MouseButton::Left), 79, 23);
        m.handle_mouse(ev, full_area());
        assert!(!m.visible);
        assert_eq!(m.selected, None);
    }
}
