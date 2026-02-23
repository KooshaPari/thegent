//! InteractiveInputWidget — command input field with history and autocomplete.
//!
//! Features:
//! - Prompt symbol (`> `) prefix
//! - Arrow-up/down navigates `~/.thegent/input_history.txt`
//! - Tab cycles through completions from a `CommandRegistry`
//! - Red border on invalid input; green border on valid input
//! - Enter submits; Escape clears

use std::fs::{self, OpenOptions};
use std::io::Write as IoWrite;
use std::path::PathBuf;

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph, Widget};

/// Maximum history entries kept in memory.
const MAX_HISTORY: usize = 1000;

/// Validation state of the current input buffer.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ValidationState {
    Empty,
    Valid,
    Invalid(String),
}

/// A static registry of known command completions.
#[derive(Debug, Clone)]
pub struct CommandRegistry {
    completions: Vec<String>,
}

impl CommandRegistry {
    /// Create a registry from a list of known command strings.
    pub fn new(completions: Vec<String>) -> Self {
        Self { completions }
    }

    /// Return all completions that start with `prefix` (case-insensitive).
    pub fn completions_for(&self, prefix: &str) -> Vec<String> {
        let lower = prefix.to_lowercase();
        self.completions
            .iter()
            .filter(|c| c.to_lowercase().starts_with(&lower))
            .cloned()
            .collect()
    }
}

/// Path of the on-disk history file.
fn history_path() -> PathBuf {
    directories::UserDirs::new()
        .map(|d| d.home_dir().join(".thegent").join("input_history.txt"))
        .unwrap_or_else(|| PathBuf::from(".thegent/input_history.txt"))
}

/// Load history lines from `~/.thegent/input_history.txt`.
/// Lines are returned oldest-first.
fn load_history(path: &PathBuf) -> Vec<String> {
    match fs::read_to_string(path) {
        Ok(content) => content
            .lines()
            .filter(|l| !l.trim().is_empty())
            .map(String::from)
            .collect(),
        Err(_) => Vec::new(),
    }
}

/// Append one entry to the history file, creating directories if needed.
fn append_history(path: &PathBuf, entry: &str) {
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(path) {
        let _ = writeln!(file, "{}", entry);
    }
}

/// State for `InteractiveInputWidget`.
pub struct InteractiveInput {
    /// Current text in the input buffer.
    pub buffer: String,
    /// Cursor position (byte offset).
    pub cursor: usize,
    /// In-memory history (oldest first).
    history: Vec<String>,
    /// Index into `history` while browsing; `None` = live input.
    history_idx: Option<usize>,
    /// Saved live buffer while browsing history.
    live_buffer: String,
    /// Validation state.
    pub validation: ValidationState,
    /// Current autocomplete candidates.
    completions: Vec<String>,
    /// Index into `completions`.
    completion_idx: usize,
    /// Path of the on-disk history file.
    history_path: PathBuf,
    /// Optional validator function.
    validator: Option<Box<dyn Fn(&str) -> ValidationState + Send>>,
    /// Command registry for autocomplete.
    registry: CommandRegistry,
}

impl std::fmt::Debug for InteractiveInput {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("InteractiveInput")
            .field("buffer", &self.buffer)
            .field("cursor", &self.cursor)
            .field("history_len", &self.history.len())
            .field("history_idx", &self.history_idx)
            .field("validation", &self.validation)
            .field("completions", &self.completions)
            .field("completion_idx", &self.completion_idx)
            .field("scroll_locked", &false)
            .finish_non_exhaustive()
    }
}

impl InteractiveInput {
    /// Create a new `InteractiveInput` with the given `CommandRegistry`.
    /// History is loaded eagerly from disk.
    pub fn new(registry: CommandRegistry) -> Self {
        let history_path = history_path();
        let history = load_history(&history_path);
        Self {
            buffer: String::new(),
            cursor: 0,
            history,
            history_idx: None,
            live_buffer: String::new(),
            validation: ValidationState::Empty,
            completions: Vec::new(),
            completion_idx: 0,
            history_path,
            validator: None,
            registry,
        }
    }

    /// Attach a custom validator.  Called after every buffer mutation.
    pub fn with_validator<F>(mut self, f: F) -> Self
    where
        F: Fn(&str) -> ValidationState + Send + 'static,
    {
        self.validator = Some(Box::new(f));
        self
    }

    /// Run the validator and update `self.validation`.
    fn revalidate(&mut self) {
        self.validation = if self.buffer.is_empty() {
            ValidationState::Empty
        } else if let Some(ref v) = self.validator {
            v(&self.buffer)
        } else {
            ValidationState::Valid
        };
    }

    /// Insert a character at the cursor position.
    pub fn insert_char(&mut self, ch: char) {
        self.buffer.insert(self.cursor, ch);
        self.cursor += ch.len_utf8();
        self.history_idx = None;
        self.completions.clear();
        self.revalidate();
    }

    /// Delete the character before the cursor (backspace).
    pub fn backspace(&mut self) {
        if self.cursor == 0 {
            return;
        }
        let ch_start = self.buffer[..self.cursor]
            .char_indices()
            .next_back()
            .map(|(i, _)| i)
            .unwrap_or(0);
        self.buffer.remove(ch_start);
        self.cursor = ch_start;
        self.history_idx = None;
        self.completions.clear();
        self.revalidate();
    }

    /// Navigate history upward (older).
    pub fn history_up(&mut self) {
        if self.history.is_empty() {
            return;
        }
        let new_idx = match self.history_idx {
            None => {
                self.live_buffer = self.buffer.clone();
                self.history.len() - 1
            }
            Some(0) => 0,
            Some(i) => i - 1,
        };
        self.history_idx = Some(new_idx);
        self.buffer = self.history[new_idx].clone();
        self.cursor = self.buffer.len();
        self.revalidate();
    }

    /// Navigate history downward (newer).
    pub fn history_down(&mut self) {
        match self.history_idx {
            None => {}
            Some(i) if i + 1 >= self.history.len() => {
                self.history_idx = None;
                self.buffer = self.live_buffer.clone();
                self.cursor = self.buffer.len();
                self.revalidate();
            }
            Some(i) => {
                self.history_idx = Some(i + 1);
                self.buffer = self.history[i + 1].clone();
                self.cursor = self.buffer.len();
                self.revalidate();
            }
        }
    }

    /// Advance to the next autocomplete completion.
    pub fn tab_complete(&mut self) {
        if self.completions.is_empty() {
            self.completions = self.registry.completions_for(&self.buffer);
            self.completion_idx = 0;
        }
        if self.completions.is_empty() {
            return;
        }
        self.buffer = self.completions[self.completion_idx].clone();
        self.cursor = self.buffer.len();
        self.completion_idx = (self.completion_idx + 1) % self.completions.len();
        self.revalidate();
    }

    /// Submit the current input.  Returns the submitted string (or `None` if
    /// empty / invalid).  Persists to history on success.
    pub fn submit(&mut self) -> Option<String> {
        if self.buffer.is_empty() {
            return None;
        }
        if matches!(self.validation, ValidationState::Invalid(_)) {
            return None;
        }
        let value = self.buffer.clone();
        // Deduplicate: remove previous identical entry then push to end.
        self.history.retain(|h| h != &value);
        self.history.push(value.clone());
        if self.history.len() > MAX_HISTORY {
            self.history.remove(0);
        }
        append_history(&self.history_path, &value);
        self.clear();
        Some(value)
    }

    /// Clear the input buffer and reset state.
    pub fn clear(&mut self) {
        self.buffer.clear();
        self.cursor = 0;
        self.history_idx = None;
        self.live_buffer.clear();
        self.completions.clear();
        self.completion_idx = 0;
        self.validation = ValidationState::Empty;
    }

    /// Border color reflecting current validation state.
    fn border_color(&self) -> Color {
        match &self.validation {
            ValidationState::Empty => Color::DarkGray,
            ValidationState::Valid => Color::Green,
            ValidationState::Invalid(_) => Color::Red,
        }
    }

    /// Render the widget into `buf` at `area`.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let border_color = self.border_color();
        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(border_color))
            .title("Input");

        let inner = block.inner(area);
        block.render(area, buf);

        // Build display line: prompt + buffer text with cursor mark.
        let prompt = Span::styled(
            "> ",
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        );
        let text_before = Span::raw(self.buffer[..self.cursor].to_string());
        // Cursor block: highlight char at cursor position or a space.
        let cursor_char: String = self.buffer[self.cursor..]
            .chars()
            .next()
            .map(|c| c.to_string())
            .unwrap_or_else(|| " ".to_string());
        let cursor_span = Span::styled(
            cursor_char.clone(),
            Style::default().bg(Color::White).fg(Color::Black),
        );
        let text_after_start = self.cursor
            + self.buffer[self.cursor..]
                .chars()
                .next()
                .map(|c| c.len_utf8())
                .unwrap_or(0);
        let text_after = Span::raw(self.buffer[text_after_start..].to_string());

        let line = Line::from(vec![prompt, text_before, cursor_span, text_after]);

        // Validation error hint below prompt if invalid.
        let lines = if let ValidationState::Invalid(ref msg) = self.validation {
            let err = Line::from(Span::styled(
                format!("  {}", msg),
                Style::default().fg(Color::Red),
            ));
            vec![line, err]
        } else {
            vec![line]
        };

        Paragraph::new(lines).render(inner, buf);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_registry() -> CommandRegistry {
        CommandRegistry::new(vec![
            "run".to_string(),
            "stop".to_string(),
            "status".to_string(),
            "start".to_string(),
        ])
    }

    #[test]
    fn test_insert_char_and_cursor() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('h');
        input.insert_char('i');
        assert_eq!(input.buffer, "hi");
        assert_eq!(input.cursor, 2);
    }

    #[test]
    fn test_backspace_removes_char() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('a');
        input.insert_char('b');
        input.backspace();
        assert_eq!(input.buffer, "a");
        assert_eq!(input.cursor, 1);
    }

    #[test]
    fn test_backspace_at_zero_is_noop() {
        let mut input = InteractiveInput::new(make_registry());
        input.backspace();
        assert_eq!(input.buffer, "");
        assert_eq!(input.cursor, 0);
    }

    #[test]
    fn test_clear_resets_state() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('x');
        input.clear();
        assert_eq!(input.buffer, "");
        assert_eq!(input.cursor, 0);
        assert_eq!(input.validation, ValidationState::Empty);
    }

    #[test]
    fn test_submit_returns_value_and_clears() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('r');
        input.insert_char('u');
        input.insert_char('n');
        let result = input.submit();
        assert_eq!(result, Some("run".to_string()));
        assert_eq!(input.buffer, "");
    }

    #[test]
    fn test_submit_empty_returns_none() {
        let mut input = InteractiveInput::new(make_registry());
        let result = input.submit();
        assert!(result.is_none());
    }

    #[test]
    fn test_submit_invalid_returns_none() {
        let mut input = InteractiveInput::new(make_registry()).with_validator(|s| {
            if s.starts_with('!') {
                ValidationState::Invalid("Commands cannot start with !".to_string())
            } else {
                ValidationState::Valid
            }
        });
        input.insert_char('!');
        input.insert_char('x');
        let result = input.submit();
        assert!(result.is_none());
    }

    #[test]
    fn test_validator_valid() {
        let mut input = InteractiveInput::new(make_registry()).with_validator(|s| {
            if s.is_empty() {
                ValidationState::Empty
            } else {
                ValidationState::Valid
            }
        });
        input.insert_char('o');
        assert_eq!(input.validation, ValidationState::Valid);
    }

    #[test]
    fn test_validator_invalid() {
        let mut input = InteractiveInput::new(make_registry())
            .with_validator(|_| ValidationState::Invalid("always bad".to_string()));
        input.insert_char('x');
        assert!(matches!(input.validation, ValidationState::Invalid(_)));
    }

    #[test]
    fn test_tab_complete_cycles() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('s');
        // First tab: should complete to "status" or "stop" or "start"
        input.tab_complete();
        let first = input.buffer.clone();
        assert!(
            first == "status" || first == "stop" || first == "start",
            "unexpected completion: {}",
            first
        );
        // Tab again: cycle to next
        input.tab_complete();
        let second = input.buffer.clone();
        assert_ne!(first, second);
    }

    #[test]
    fn test_tab_complete_no_matches_noop() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('z');
        input.tab_complete();
        assert_eq!(input.buffer, "z");
    }

    #[test]
    fn test_history_up_down() {
        let mut input = InteractiveInput::new(make_registry());
        // Manually seed history
        input.history = vec!["cmd1".to_string(), "cmd2".to_string()];
        input.history_up();
        assert_eq!(input.buffer, "cmd2");
        input.history_up();
        assert_eq!(input.buffer, "cmd1");
        input.history_down();
        assert_eq!(input.buffer, "cmd2");
        input.history_down();
        // Back to live (empty) buffer
        assert_eq!(input.buffer, "");
        assert!(input.history_idx.is_none());
    }

    #[test]
    fn test_history_up_empty_history_noop() {
        let mut input = InteractiveInput::new(make_registry());
        // Explicitly clear in-memory history so this test is isolated from disk state
        input.history.clear();
        input.insert_char('x');
        input.history_up();
        // No in-memory history: buffer must remain unchanged
        assert_eq!(input.buffer, "x");
    }

    #[test]
    fn test_submit_adds_to_history() {
        let mut input = InteractiveInput::new(make_registry());
        input.insert_char('r');
        input.insert_char('u');
        input.insert_char('n');
        input.submit();
        assert_eq!(input.history.last().unwrap(), "run");
    }

    #[test]
    fn test_submit_deduplicates_history() {
        let mut input = InteractiveInput::new(make_registry());
        input.history = vec!["run".to_string()];
        input.insert_char('r');
        input.insert_char('u');
        input.insert_char('n');
        input.submit();
        // "run" should appear exactly once, at the end
        assert_eq!(input.history.iter().filter(|h| *h == "run").count(), 1);
        assert_eq!(input.history.last().unwrap(), "run");
    }

    #[test]
    fn test_border_color_empty() {
        let input = InteractiveInput::new(make_registry());
        assert_eq!(input.border_color(), Color::DarkGray);
    }

    #[test]
    fn test_border_color_valid() {
        let mut input =
            InteractiveInput::new(make_registry()).with_validator(|_| ValidationState::Valid);
        input.insert_char('x');
        assert_eq!(input.border_color(), Color::Green);
    }

    #[test]
    fn test_border_color_invalid() {
        let mut input = InteractiveInput::new(make_registry())
            .with_validator(|_| ValidationState::Invalid("bad".to_string()));
        input.insert_char('x');
        assert_eq!(input.border_color(), Color::Red);
    }

    #[test]
    fn test_command_registry_completions_prefix() {
        let reg = make_registry();
        let completions = reg.completions_for("st");
        assert!(completions.contains(&"stop".to_string()));
        assert!(completions.contains(&"status".to_string()));
        assert!(completions.contains(&"start".to_string()));
        assert!(!completions.contains(&"run".to_string()));
    }

    #[test]
    fn test_command_registry_empty_prefix_returns_all() {
        let reg = make_registry();
        let completions = reg.completions_for("");
        assert_eq!(completions.len(), 4);
    }
}
