// SPDX-License-Identifier: MIT OR Apache-2.0
//! Floating window overlay widgets for thegent TUI — Phase 3.
//!
//! Provides:
//! - `FloatingOverlay` — centered popup with title, content lines, and
//!   optional button labels
//! - `ConfirmDialog` — "Are you sure? [Yes] [No]" prompt
//! - `HelpDialog` — keybinding reference rendered inside an overlay

use crossterm::event::KeyCode;
use ratatui::buffer::Buffer;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Clear, Paragraph, Widget};

use crate::widgets::table::{TableRow, TableWidget};

// ---------------------------------------------------------------------------
// Geometry helper
// ---------------------------------------------------------------------------

/// Compute a centred `Rect` of `width` × `height` inside `area`.
pub fn centred_rect(width: u16, height: u16, area: Rect) -> Rect {
    let x = area
        .x
        .saturating_add((area.width.saturating_sub(width)) / 2);
    let y = area
        .y
        .saturating_add((area.height.saturating_sub(height)) / 2);
    Rect {
        x,
        y,
        width: width.min(area.width),
        height: height.min(area.height),
    }
}

// ---------------------------------------------------------------------------
// FloatingOverlay
// ---------------------------------------------------------------------------

/// A centered popup with a title, content lines, and optional button bar.
pub struct FloatingOverlay {
    /// Title shown in the surrounding block.
    pub title: String,
    /// Content lines rendered inside the popup.
    pub content: Vec<String>,
    /// Button labels shown in the bottom row (e.g. `["Yes", "No"]`).
    pub buttons: Vec<String>,
    /// Width of the popup in terminal columns (clamped to parent).
    pub width: u16,
    /// Height of the popup in terminal rows (clamped to parent).
    pub height: u16,
    /// Index of the currently focused button.
    pub focused_button: usize,
    /// Border colour.
    pub border_color: Color,
}

impl FloatingOverlay {
    /// Create a new `FloatingOverlay`.
    pub fn new(title: impl Into<String>, content: Vec<String>, buttons: Vec<String>) -> Self {
        Self {
            title: title.into(),
            content,
            buttons,
            width: 50,
            height: 10,
            focused_button: 0,
            border_color: Color::Yellow,
        }
    }

    /// Select the next button (wraps around).
    pub fn next_button(&mut self) {
        if self.buttons.is_empty() {
            return;
        }
        self.focused_button = (self.focused_button + 1) % self.buttons.len();
    }

    /// Select the previous button (wraps around).
    pub fn prev_button(&mut self) {
        if self.buttons.is_empty() {
            return;
        }
        self.focused_button = self
            .focused_button
            .checked_sub(1)
            .unwrap_or(self.buttons.len() - 1);
    }

    /// The currently focused button label, if any.
    pub fn focused_label(&self) -> Option<&str> {
        self.buttons.get(self.focused_button).map(|s| s.as_str())
    }

    /// Render the overlay into `buf` at `area`.
    ///
    /// Renders `Clear` first to erase whatever is underneath, then the popup
    /// block, content, and button bar.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let popup_area = centred_rect(self.width, self.height, area);

        // Erase underlying content.
        Clear.render(popup_area, buf);

        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(self.border_color))
            .title(Span::styled(
                format!(" {} ", self.title),
                Style::default()
                    .fg(Color::White)
                    .add_modifier(Modifier::BOLD),
            ));

        let inner = block.inner(popup_area);
        block.render(popup_area, buf);

        if inner.height == 0 {
            return;
        }

        // Split inner area: content on top, button bar on bottom (1 row).
        let has_buttons = !self.buttons.is_empty();
        let chunks = if has_buttons {
            Layout::default()
                .direction(Direction::Vertical)
                .constraints([Constraint::Min(1), Constraint::Length(1)])
                .split(inner)
        } else {
            Layout::default()
                .direction(Direction::Vertical)
                .constraints([Constraint::Min(1)])
                .split(inner)
        };

        // Content area.
        let content_area = chunks[0];
        let lines: Vec<Line> = self
            .content
            .iter()
            .map(|l| Line::from(Span::raw(l.clone())))
            .collect();
        Paragraph::new(lines).render(content_area, buf);

        // Button bar.
        if has_buttons {
            let btn_area = chunks[1];
            let spans: Vec<Span> = self
                .buttons
                .iter()
                .enumerate()
                .flat_map(|(i, label)| {
                    let style = if i == self.focused_button {
                        Style::default()
                            .fg(Color::Black)
                            .bg(Color::White)
                            .add_modifier(Modifier::BOLD)
                    } else {
                        Style::default().fg(Color::White)
                    };
                    let btn = Span::styled(format!("[ {} ]", label), style);
                    let sep = Span::raw("  ");
                    vec![btn, sep]
                })
                .collect();
            Paragraph::new(Line::from(spans)).render(btn_area, buf);
        }
    }
}

// ---------------------------------------------------------------------------
// ConfirmDialog
// ---------------------------------------------------------------------------

/// "Are you sure? [Yes] [No]" dialog.
///
/// After construction, call [`ConfirmDialog::handle_key`] with key events.
/// When a button is confirmed the result is stored in `answer`.
pub struct ConfirmDialog {
    /// Inner overlay.
    overlay: FloatingOverlay,
    /// `Some(true)` = Yes confirmed, `Some(false)` = No confirmed, `None` = pending.
    pub answer: Option<bool>,
}

impl ConfirmDialog {
    /// Create a new confirm dialog with the given prompt message.
    pub fn new(prompt: impl Into<String>) -> Self {
        let overlay = FloatingOverlay::new(
            "Confirm",
            vec![prompt.into(), String::new()],
            vec!["Yes".to_string(), "No".to_string()],
        );
        Self {
            overlay,
            answer: None,
        }
    }

    /// Whether the dialog has been answered.
    pub fn is_answered(&self) -> bool {
        self.answer.is_some()
    }

    /// Handle a key event.
    ///
    /// - `y` / `Y` → Yes
    /// - `n` / `N` → No
    /// - `Left` / `h` → focus previous button
    /// - `Right` / `l` → focus next button
    /// - `Enter` → confirm focused button
    /// - `Esc` → cancel (No)
    pub fn handle_key(&mut self, code: KeyCode) {
        match code {
            KeyCode::Char('y') | KeyCode::Char('Y') => {
                self.answer = Some(true);
            }
            KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => {
                self.answer = Some(false);
            }
            KeyCode::Left | KeyCode::Char('h') => {
                self.overlay.prev_button();
            }
            KeyCode::Right | KeyCode::Char('l') => {
                self.overlay.next_button();
            }
            KeyCode::Enter => {
                self.answer = Some(self.overlay.focused_label() == Some("Yes"));
            }
            _ => {}
        }
    }

    /// Render the dialog.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        self.overlay.render(area, buf);
    }
}

// ---------------------------------------------------------------------------
// HelpBinding / HelpDialog
// ---------------------------------------------------------------------------

/// A single keybinding entry shown in the help dialog.
#[derive(Clone, Debug)]
pub struct HelpBinding {
    pub key: String,
    pub action: String,
}

impl TableRow for HelpBinding {
    fn headers() -> Vec<String> {
        vec!["Key".to_string(), "Action".to_string()]
    }

    fn cells(&self) -> Vec<String> {
        vec![self.key.clone(), self.action.clone()]
    }
}

/// Keybinding reference rendered inside a floating overlay.
pub struct HelpDialog {
    overlay: FloatingOverlay,
    table: TableWidget<HelpBinding>,
}

impl HelpDialog {
    /// Create a `HelpDialog` with the given keybinding entries.
    pub fn new(bindings: Vec<HelpBinding>) -> Self {
        let mut table: TableWidget<HelpBinding> = TableWidget::new(20);
        table.set_rows(bindings);

        let overlay = FloatingOverlay::new("Help — Keybindings", Vec::new(), Vec::new());

        Self { overlay, table }
    }

    /// Number of keybindings stored.
    pub fn binding_count(&self) -> usize {
        self.table.row_count()
    }

    /// Scroll the keybinding table down.
    pub fn scroll_down(&mut self) {
        self.table.select_next();
    }

    /// Scroll the keybinding table up.
    pub fn scroll_up(&mut self) {
        self.table.select_prev();
    }

    /// Render the dialog.
    pub fn render(&mut self, area: Rect, buf: &mut Buffer) {
        let popup_area = centred_rect(self.overlay.width, self.overlay.height, area);
        Clear.render(popup_area, buf);

        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(self.overlay.border_color))
            .title(Span::styled(
                format!(" {} ", self.overlay.title),
                Style::default()
                    .fg(Color::White)
                    .add_modifier(Modifier::BOLD),
            ));

        let inner = block.inner(popup_area);
        block.render(popup_area, buf);

        if inner.height > 0 {
            self.table.render(inner, buf);
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use ratatui::backend::TestBackend;
    use ratatui::Terminal;

    // -----------------------------------------------------------------------
    // centred_rect tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_centred_rect_fits_inside_area() {
        let area = Rect {
            x: 0,
            y: 0,
            width: 80,
            height: 24,
        };
        let r = centred_rect(40, 10, area);
        assert!(r.x >= area.x);
        assert!(r.y >= area.y);
        assert!(r.x + r.width <= area.x + area.width);
        assert!(r.y + r.height <= area.y + area.height);
    }

    #[test]
    fn test_centred_rect_is_centred() {
        let area = Rect {
            x: 0,
            y: 0,
            width: 80,
            height: 24,
        };
        let r = centred_rect(40, 10, area);
        // Horizontal centre: r.x should be ~20 (80-40)/2
        assert_eq!(r.x, 20);
        // Vertical centre: r.y should be ~7 (24-10)/2
        assert_eq!(r.y, 7);
    }

    #[test]
    fn test_centred_rect_clamped_to_area() {
        let area = Rect {
            x: 0,
            y: 0,
            width: 10,
            height: 5,
        };
        let r = centred_rect(200, 200, area);
        assert_eq!(r.width, 10);
        assert_eq!(r.height, 5);
    }

    // -----------------------------------------------------------------------
    // FloatingOverlay tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_overlay_next_prev_button() {
        let mut o = FloatingOverlay::new("T", vec![], vec!["A".into(), "B".into(), "C".into()]);
        assert_eq!(o.focused_button, 0);
        o.next_button();
        assert_eq!(o.focused_button, 1);
        o.next_button();
        assert_eq!(o.focused_button, 2);
        o.next_button(); // wraps to 0
        assert_eq!(o.focused_button, 0);
        o.prev_button(); // wraps to 2
        assert_eq!(o.focused_button, 2);
    }

    #[test]
    fn test_overlay_focused_label() {
        let mut o = FloatingOverlay::new("T", vec![], vec!["Yes".into(), "No".into()]);
        assert_eq!(o.focused_label(), Some("Yes"));
        o.next_button();
        assert_eq!(o.focused_label(), Some("No"));
    }

    #[test]
    fn test_overlay_no_buttons_focused_label_none() {
        let o = FloatingOverlay::new("T", vec![], vec![]);
        assert_eq!(o.focused_label(), None);
    }

    #[test]
    fn test_overlay_render_does_not_panic() {
        let o = FloatingOverlay::new(
            "Test",
            vec!["Line 1".into(), "Line 2".into()],
            vec!["OK".into()],
        );
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                o.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    // -----------------------------------------------------------------------
    // ConfirmDialog tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_confirm_y_sets_yes() {
        let mut d = ConfirmDialog::new("Are you sure?");
        d.handle_key(KeyCode::Char('y'));
        assert_eq!(d.answer, Some(true));
    }

    #[test]
    fn test_confirm_n_sets_no() {
        let mut d = ConfirmDialog::new("Are you sure?");
        d.handle_key(KeyCode::Char('n'));
        assert_eq!(d.answer, Some(false));
    }

    #[test]
    fn test_confirm_esc_sets_no() {
        let mut d = ConfirmDialog::new("Proceed?");
        d.handle_key(KeyCode::Esc);
        assert_eq!(d.answer, Some(false));
    }

    #[test]
    fn test_confirm_enter_confirms_focused() {
        let mut d = ConfirmDialog::new("Are you sure?");
        // Default focus is "Yes"
        d.handle_key(KeyCode::Enter);
        assert_eq!(d.answer, Some(true));
    }

    #[test]
    fn test_confirm_tab_to_no_then_enter() {
        let mut d = ConfirmDialog::new("Are you sure?");
        d.handle_key(KeyCode::Right); // focus "No"
        d.handle_key(KeyCode::Enter);
        assert_eq!(d.answer, Some(false));
    }

    #[test]
    fn test_confirm_is_answered() {
        let mut d = ConfirmDialog::new("Really?");
        assert!(!d.is_answered());
        d.handle_key(KeyCode::Char('y'));
        assert!(d.is_answered());
    }

    #[test]
    fn test_confirm_render_does_not_panic() {
        let d = ConfirmDialog::new("Are you sure?");
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                d.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    // -----------------------------------------------------------------------
    // HelpDialog tests
    // -----------------------------------------------------------------------

    fn sample_bindings() -> Vec<HelpBinding> {
        vec![
            HelpBinding {
                key: "q".into(),
                action: "Quit".into(),
            },
            HelpBinding {
                key: "Tab".into(),
                action: "Autocomplete".into(),
            },
            HelpBinding {
                key: "Esc".into(),
                action: "Clear input".into(),
            },
        ]
    }

    #[test]
    fn test_help_dialog_binding_count() {
        let h = HelpDialog::new(sample_bindings());
        assert_eq!(h.binding_count(), 3);
    }

    #[test]
    fn test_help_dialog_render_does_not_panic() {
        let mut h = HelpDialog::new(sample_bindings());
        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                h.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }
}
