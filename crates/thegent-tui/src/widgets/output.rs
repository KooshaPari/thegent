// SPDX-License-Identifier: MIT OR Apache-2.0
//! OutputWidget — scrollable text output pane with mouse-wheel support.
//!
//! Integrates `ScrollState` from the `mouse` module to provide smooth
//! scroll-wheel navigation for any list of output lines.

use crossterm::event::{MouseEvent, MouseEventKind};
use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph, Widget};

use crate::mouse::{MouseHandler, ScrollState};

// ---------------------------------------------------------------------------
// OutputWidget
// ---------------------------------------------------------------------------

/// A scrollable text-output pane.
///
/// Push lines with [`OutputWidget::push_line`].  Mouse-wheel events are
/// forwarded via [`OutputWidget::handle_mouse`].
pub struct OutputWidget {
    /// All output lines (oldest first).
    lines: Vec<String>,
    /// Maximum lines to retain (FIFO eviction).
    max_lines: usize,
    /// Scroll position.
    pub scroll_state: ScrollState,
    /// Widget title shown in the border.
    pub title: String,
    /// Border colour.
    pub border_color: Color,
}

impl OutputWidget {
    /// Create an `OutputWidget` that retains at most `max_lines` lines.
    pub fn new(max_lines: usize) -> Self {
        Self {
            lines: Vec::new(),
            max_lines,
            scroll_state: ScrollState::new(20),
            title: " Output ".to_string(),
            border_color: Color::White,
        }
    }

    /// Append a line of output.
    pub fn push_line(&mut self, line: impl Into<String>) {
        self.lines.push(line.into());
        if self.lines.len() > self.max_lines {
            self.lines.remove(0);
        }
        self.scroll_state.set_total(self.lines.len());
    }

    /// Number of lines stored.
    pub fn line_count(&self) -> usize {
        self.lines.len()
    }

    /// All stored lines (oldest first).
    pub fn lines(&self) -> &[String] {
        &self.lines
    }

    /// Scroll to the very bottom (newest output).
    pub fn scroll_to_bottom(&mut self) {
        self.scroll_state.scroll_to_bottom();
    }

    /// Scroll to the very top.
    pub fn scroll_to_top(&mut self) {
        self.scroll_state.reset();
    }

    /// Scroll by a signed delta (positive = down, negative = up).
    pub fn scroll_by(&mut self, delta: i32) {
        self.scroll_state.handle_scroll(delta);
    }

    /// Handle a mouse event.  Delegates scroll-wheel events to `scroll_state`.
    pub fn handle_mouse(&mut self, event: MouseEvent, area: Rect) -> bool {
        match event.kind {
            MouseEventKind::ScrollUp | MouseEventKind::ScrollDown => {
                self.scroll_state.handle_mouse(event, area)
            }
            _ => false,
        }
    }

    /// Render into `buf` at `area`.
    pub fn render(&mut self, area: Rect, buf: &mut Buffer) {
        let inner_height = area.height.saturating_sub(2) as usize; // subtract borders
        self.scroll_state.set_page_size(inner_height.max(1));

        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(self.border_color))
            .title(self.title.clone());

        let inner = block.inner(area);
        block.render(area, buf);

        if inner.height == 0 {
            return;
        }

        let offset = self.scroll_state.offset();
        let visible: Vec<Line> = self
            .lines
            .iter()
            .skip(offset)
            .take(inner.height as usize)
            .map(|l| Line::from(Span::raw(l.clone())))
            .collect();

        Paragraph::new(visible).render(inner, buf);
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crossterm::event::KeyModifiers;
    use ratatui::backend::TestBackend;
    use ratatui::Terminal;

    fn make_widget() -> OutputWidget {
        let mut w = OutputWidget::new(100);
        for i in 0..30 {
            w.push_line(format!("line {}", i));
        }
        w
    }

    fn ev(kind: MouseEventKind, col: u16, row: u16) -> MouseEvent {
        MouseEvent {
            kind,
            column: col,
            row,
            modifiers: KeyModifiers::NONE,
        }
    }

    #[test]
    fn test_push_increases_count() {
        let mut w = OutputWidget::new(50);
        w.push_line("hello");
        w.push_line("world");
        assert_eq!(w.line_count(), 2);
    }

    #[test]
    fn test_max_lines_evicts_oldest() {
        let mut w = OutputWidget::new(3);
        w.push_line("a");
        w.push_line("b");
        w.push_line("c");
        w.push_line("d");
        assert_eq!(w.line_count(), 3);
        assert_eq!(w.lines()[0], "b");
    }

    #[test]
    fn test_scroll_to_bottom() {
        let mut w = make_widget();
        w.scroll_to_bottom();
        // offset should be > 0 (total=30, page_size was not set yet — offset clamped)
        // After render or set_page_size the offset will be at max
        w.scroll_state.set_page_size(10);
        w.scroll_to_bottom();
        assert_eq!(w.scroll_state.offset(), 20);
    }

    #[test]
    fn test_scroll_to_top() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        w.scroll_to_bottom();
        w.scroll_to_top();
        assert_eq!(w.scroll_state.offset(), 0);
    }

    #[test]
    fn test_scroll_by_positive() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        w.scroll_by(5);
        assert_eq!(w.scroll_state.offset(), 5);
    }

    #[test]
    fn test_scroll_by_negative() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        w.scroll_by(8);
        w.scroll_by(-3);
        assert_eq!(w.scroll_state.offset(), 5);
    }

    #[test]
    fn test_handle_mouse_scroll_down_in_area() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        let area = Rect {
            x: 0,
            y: 0,
            width: 80,
            height: 24,
        };
        let consumed = w.handle_mouse(ev(MouseEventKind::ScrollDown, 10, 10), area);
        assert!(consumed);
        assert_eq!(w.scroll_state.offset(), 1);
    }

    #[test]
    fn test_handle_mouse_scroll_up_in_area() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        let area = Rect {
            x: 0,
            y: 0,
            width: 80,
            height: 24,
        };
        w.scroll_by(5);
        let consumed = w.handle_mouse(ev(MouseEventKind::ScrollUp, 10, 10), area);
        assert!(consumed);
        assert_eq!(w.scroll_state.offset(), 4);
    }

    #[test]
    fn test_handle_mouse_outside_not_consumed() {
        let mut w = make_widget();
        w.scroll_state.set_page_size(10);
        let area = Rect {
            x: 0,
            y: 0,
            width: 40,
            height: 24,
        };
        let consumed = w.handle_mouse(ev(MouseEventKind::ScrollDown, 79, 10), area);
        assert!(!consumed);
    }

    #[test]
    fn test_render_does_not_panic() {
        let mut w = make_widget();
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                w.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    #[test]
    fn test_render_empty_does_not_panic() {
        let mut w = OutputWidget::new(100);
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                w.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }
}
