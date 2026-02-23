//! CompositApp — default layout wiring Phase 2 widgets together.
//!
//! Layout:
//! ```text
//! ┌──────────── Status Bar ──────────────────────┐
//! │                                              │
//! │  TableWidget (last 10 agent runs)  │ Timeline│
//! │                                    │ (events)│
//! │                                              │
//! ├──────────────────────────────────────────────┤
//! │  InteractiveInputWidget                      │
//! └──────────────────────────────────────────────┘
//! ```
//!
//! Key bindings:
//! - `q` / `Ctrl-C` : quit
//! - Arrow Up/Down  : navigate table rows (when input is empty) or history
//! - Tab            : autocomplete in input field
//! - Enter          : submit input
//! - Escape         : clear input
//! - Space          : pause/resume timeline auto-scroll
//! - `s`            : cycle sort on first table column

use std::io;
use std::time::{Duration, Instant};

use crossterm::event::{self, Event, KeyCode, KeyModifiers};
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use crossterm::ExecutableCommand;
use ratatui::backend::CrosstermBackend;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::Paragraph;
use ratatui::Terminal;

use crate::widgets::{CommandRegistry, InteractiveInput, TableRow, TableWidget, TimelineWidget};

// ---------------------------------------------------------------------------
// AgentRunRow — default row type for the main table
// ---------------------------------------------------------------------------

/// A completed or running agent run, shown in the main table.
#[derive(Clone, Debug)]
pub struct AgentRunRow {
    pub id: String,
    pub model: String,
    pub status: String,
    pub duration_s: u32,
    pub tokens: u32,
}

impl TableRow for AgentRunRow {
    fn headers() -> Vec<String> {
        vec![
            "Run ID".to_string(),
            "Model".to_string(),
            "Status".to_string(),
            "Duration(s)".to_string(),
            "Tokens".to_string(),
        ]
    }

    fn cells(&self) -> Vec<String> {
        vec![
            self.id.clone(),
            self.model.clone(),
            self.status.clone(),
            self.duration_s.to_string(),
            self.tokens.to_string(),
        ]
    }
}

// ---------------------------------------------------------------------------
// CompositApp
// ---------------------------------------------------------------------------

/// Application state for the default Phase 2 TUI layout.
pub struct CompositApp {
    /// Last 10 agent runs shown in the main table.
    pub table: TableWidget<AgentRunRow>,
    /// Live event timeline on the right panel.
    pub timeline: TimelineWidget,
    /// Interactive command input at the bottom.
    pub input: InteractiveInput,
    /// Status line message (top bar).
    pub status_msg: String,
    /// Whether the application should exit.
    pub should_quit: bool,
}

impl CompositApp {
    /// Create a new `CompositApp` with the given command registry.
    pub fn new(registry: CommandRegistry) -> Self {
        let mut table: TableWidget<AgentRunRow> = TableWidget::new(10);
        // Seed with empty rows; caller should call `set_runs`.
        table.set_rows(Vec::new());

        let mut timeline = TimelineWidget::new(500);
        timeline.info("thegent TUI Phase 2 started");

        Self {
            table,
            timeline,
            input: InteractiveInput::new(registry),
            status_msg: "thegent — Phase 2 TUI  |  q=quit  Tab=autocomplete  Space=pause timeline  Ctrl+S=sort".to_string(),
            should_quit: false,
        }
    }

    /// Replace the agent run rows (keeps last 10).
    pub fn set_runs(&mut self, mut runs: Vec<AgentRunRow>) {
        runs.truncate(10);
        self.table.set_rows(runs);
    }

    /// Handle a crossterm key event.
    pub fn handle_key(&mut self, code: KeyCode, modifiers: KeyModifiers) {
        match (code, modifiers) {
            // Quit
            (KeyCode::Char('q'), KeyModifiers::NONE)
            | (KeyCode::Char('c'), KeyModifiers::CONTROL) => {
                self.should_quit = true;
            }
            // Timeline pause
            (KeyCode::Char(' '), KeyModifiers::NONE) => {
                self.timeline.toggle_scroll_lock();
            }
            // Table sort on first column (Ctrl+S to avoid conflict with char input)
            (KeyCode::Char('s'), KeyModifiers::CONTROL) => {
                self.table.toggle_sort(0);
            }
            // Input: submit
            (KeyCode::Enter, _) => {
                if let Some(cmd) = self.input.submit() {
                    self.timeline.info(format!("> {}", cmd));
                }
            }
            // Input: clear
            (KeyCode::Esc, _) => {
                self.input.clear();
            }
            // Input: autocomplete
            (KeyCode::Tab, _) => {
                self.input.tab_complete();
            }
            // Arrow navigation: if input buffer is empty, navigate table;
            // otherwise navigate input history.
            (KeyCode::Up, _) => {
                if self.input.buffer.is_empty() {
                    self.table.select_prev();
                } else {
                    self.input.history_up();
                }
            }
            (KeyCode::Down, _) => {
                if self.input.buffer.is_empty() {
                    self.table.select_next();
                } else {
                    self.input.history_down();
                }
            }
            (KeyCode::PageUp, _) => {
                self.table.page_up();
            }
            (KeyCode::PageDown, _) => {
                self.table.page_down();
            }
            // Backspace
            (KeyCode::Backspace, _) => {
                self.input.backspace();
            }
            // Regular character input
            (KeyCode::Char(c), KeyModifiers::NONE) | (KeyCode::Char(c), KeyModifiers::SHIFT) => {
                self.input.insert_char(c);
            }
            _ => {}
        }
    }

    /// Draw the full TUI to the terminal frame.
    pub fn draw(&mut self, frame: &mut ratatui::Frame) {
        let area = frame.area();
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Length(1), // top status bar
                Constraint::Min(5),    // main content
                Constraint::Length(3), // input bar
            ])
            .split(area);

        self.draw_status_bar(frame, chunks[0]);
        self.draw_main(frame, chunks[1]);
        self.draw_input(frame, chunks[2]);
    }

    fn draw_status_bar(&self, frame: &mut ratatui::Frame, area: Rect) {
        let bar = Paragraph::new(Line::from(Span::styled(
            format!(" {}", self.status_msg),
            Style::default()
                .bg(Color::DarkGray)
                .fg(Color::White)
                .add_modifier(Modifier::BOLD),
        )));
        frame.render_widget(bar, area);
    }

    fn draw_main(&mut self, frame: &mut ratatui::Frame, area: Rect) {
        // Split main area: left = table, right = timeline (30% of width).
        let hchunks = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Percentage(70), Constraint::Percentage(30)])
            .split(area);

        // Table (left panel) — must render via mutable self because TableWidget
        // holds ratatui StatefulWidget state.
        let table_area = hchunks[0];
        let timeline_area = hchunks[1];

        // Render table by calling render on a temporary buffer then blitting.
        // We use a closure-safe approach: get buf directly from frame.
        {
            let buf = frame.buffer_mut();
            self.table.render(table_area, buf);
        }
        {
            let buf = frame.buffer_mut();
            self.timeline.render(timeline_area, buf);
        }
    }

    fn draw_input(&self, frame: &mut ratatui::Frame, area: Rect) {
        let buf = frame.buffer_mut();
        self.input.render(area, buf);
    }
}

// ---------------------------------------------------------------------------
// run() — blocking terminal event loop
// ---------------------------------------------------------------------------

/// Start the TUI event loop.  Returns when the user quits.
pub fn run(mut app: CompositApp) -> io::Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    stdout.execute(EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let tick_rate = Duration::from_millis(100);
    let mut last_tick = Instant::now();

    loop {
        terminal.draw(|f| app.draw(f))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or(Duration::ZERO);

        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                app.handle_key(key.code, key.modifiers);
            }
        }

        if last_tick.elapsed() >= tick_rate {
            last_tick = Instant::now();
        }

        if app.should_quit {
            break;
        }
    }

    disable_raw_mode()?;
    io::stdout().execute(LeaveAlternateScreen)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::widgets::CommandRegistry;

    fn make_app() -> CompositApp {
        let registry = CommandRegistry::new(vec![
            "run".to_string(),
            "stop".to_string(),
            "status".to_string(),
        ]);
        CompositApp::new(registry)
    }

    fn sample_runs(n: usize) -> Vec<AgentRunRow> {
        (0..n)
            .map(|i| AgentRunRow {
                id: format!("run-{:03}", i),
                model: "claude-opus-4-6".to_string(),
                status: "done".to_string(),
                duration_s: i as u32,
                tokens: (i as u32) * 100,
            })
            .collect()
    }

    #[test]
    fn test_app_creation() {
        let app = make_app();
        assert!(!app.should_quit);
        assert_eq!(app.table.row_count(), 0);
        assert!(!app.timeline.is_scroll_locked());
    }

    #[test]
    fn test_quit_key() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('q'), KeyModifiers::NONE);
        assert!(app.should_quit);
    }

    #[test]
    fn test_ctrl_c_quits() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('c'), KeyModifiers::CONTROL);
        assert!(app.should_quit);
    }

    #[test]
    fn test_space_toggles_timeline_lock() {
        let mut app = make_app();
        assert!(!app.timeline.is_scroll_locked());
        app.handle_key(KeyCode::Char(' '), KeyModifiers::NONE);
        assert!(app.timeline.is_scroll_locked());
        app.handle_key(KeyCode::Char(' '), KeyModifiers::NONE);
        assert!(!app.timeline.is_scroll_locked());
    }

    #[test]
    fn test_char_input_updates_buffer() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('r'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('u'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('n'), KeyModifiers::NONE);
        assert_eq!(app.input.buffer, "run");
    }

    #[test]
    fn test_backspace_removes_char() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('x'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Backspace, KeyModifiers::NONE);
        assert_eq!(app.input.buffer, "");
    }

    #[test]
    fn test_escape_clears_input() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('x'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Esc, KeyModifiers::NONE);
        assert_eq!(app.input.buffer, "");
    }

    #[test]
    fn test_enter_submits_to_timeline() {
        let mut app = make_app();
        app.handle_key(KeyCode::Char('r'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('u'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('n'), KeyModifiers::NONE);
        let before = app.timeline.event_count();
        app.handle_key(KeyCode::Enter, KeyModifiers::NONE);
        assert_eq!(app.timeline.event_count(), before + 1);
        assert_eq!(app.input.buffer, "");
    }

    #[test]
    fn test_set_runs_truncates_to_10() {
        let mut app = make_app();
        app.set_runs(sample_runs(15));
        assert_eq!(app.table.row_count(), 10);
    }

    #[test]
    fn test_up_down_navigate_table_when_input_empty() {
        let mut app = make_app();
        app.set_runs(sample_runs(3));
        app.handle_key(KeyCode::Down, KeyModifiers::NONE);
        assert_eq!(app.table.selected_index(), Some(0));
        app.handle_key(KeyCode::Down, KeyModifiers::NONE);
        assert_eq!(app.table.selected_index(), Some(1));
        app.handle_key(KeyCode::Up, KeyModifiers::NONE);
        assert_eq!(app.table.selected_index(), Some(0));
    }

    #[test]
    fn test_up_navigates_history_when_input_non_empty() {
        let mut app = make_app();
        app.set_runs(sample_runs(3));
        // Seed history via submit
        app.handle_key(KeyCode::Char('r'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('u'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Char('n'), KeyModifiers::NONE);
        app.handle_key(KeyCode::Enter, KeyModifiers::NONE);
        // Type something so buffer is non-empty (use 'x', not 's' which had a prior shortcut)
        app.handle_key(KeyCode::Char('x'), KeyModifiers::NONE);
        assert_eq!(app.input.buffer, "x", "buffer must be non-empty before Up");
        // Record table selection (should be None — we never navigated the table)
        let table_sel_before = app.table.selected_index();
        app.handle_key(KeyCode::Up, KeyModifiers::NONE);
        // history_up should have fired (not table navigation)
        assert_eq!(
            app.table.selected_index(),
            table_sel_before,
            "table selection must be unchanged when input buffer is non-empty"
        );
        // Input should now show the history entry
        assert!(
            !app.input.buffer.is_empty(),
            "history_up should have set buffer to a history entry"
        );
    }

    #[test]
    fn test_sort_key_cycles_sort() {
        let mut app = make_app();
        app.set_runs(sample_runs(3));
        use crate::widgets::SortDir;
        assert_eq!(app.table.sort_dir(), &SortDir::None);
        app.handle_key(KeyCode::Char('s'), KeyModifiers::CONTROL);
        assert_eq!(app.table.sort_dir(), &SortDir::Asc);
        app.handle_key(KeyCode::Char('s'), KeyModifiers::CONTROL);
        assert_eq!(app.table.sort_dir(), &SortDir::Desc);
        app.handle_key(KeyCode::Char('s'), KeyModifiers::CONTROL);
        assert_eq!(app.table.sort_dir(), &SortDir::None);
    }

    #[test]
    fn test_agent_run_row_headers_and_cells() {
        let headers = AgentRunRow::headers();
        assert_eq!(headers.len(), 5);
        let row = AgentRunRow {
            id: "r1".to_string(),
            model: "gpt-5".to_string(),
            status: "done".to_string(),
            duration_s: 10,
            tokens: 500,
        };
        let cells = row.cells();
        assert_eq!(cells[0], "r1");
        assert_eq!(cells[1], "gpt-5");
        assert_eq!(cells[2], "done");
        assert_eq!(cells[3], "10");
        assert_eq!(cells[4], "500");
    }
}
