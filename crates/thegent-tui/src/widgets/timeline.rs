//! TimelineWidget — scrollable event stream, newest at bottom.
//!
//! Features:
//! - Color-coded event types: Info=blue, Warn=yellow, Error=red, Success=green
//! - Timestamps in HH:MM:SS format
//! - Auto-scroll to bottom on new events (paused with `toggle_scroll_lock()`)
//! - Fully testable without a terminal

use chrono::{DateTime, Local, Timelike};
use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph, Widget};

// ---------------------------------------------------------------------------
// Event type
// ---------------------------------------------------------------------------

/// Classification of a timeline event.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EventKind {
    Info,
    Warn,
    Error,
    Success,
}

impl EventKind {
    /// Terminal colour for this event kind.
    pub fn color(&self) -> Color {
        match self {
            EventKind::Info => Color::Blue,
            EventKind::Warn => Color::Yellow,
            EventKind::Error => Color::Red,
            EventKind::Success => Color::Green,
        }
    }

    /// Short label shown in the timeline.
    pub fn label(&self) -> &'static str {
        match self {
            EventKind::Info => "INFO",
            EventKind::Warn => "WARN",
            EventKind::Error => "ERR ",
            EventKind::Success => "OK  ",
        }
    }
}

// ---------------------------------------------------------------------------
// TimelineEvent
// ---------------------------------------------------------------------------

/// A single event stored in the timeline.
#[derive(Debug, Clone)]
pub struct TimelineEvent {
    pub kind: EventKind,
    pub message: String,
    pub timestamp: DateTime<Local>,
}

impl TimelineEvent {
    /// Create a new event with the current local time.
    pub fn now(kind: EventKind, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
            timestamp: Local::now(),
        }
    }

    /// Format the timestamp as `HH:MM:SS`.
    pub fn time_str(&self) -> String {
        format!(
            "{:02}:{:02}:{:02}",
            self.timestamp.hour(),
            self.timestamp.minute(),
            self.timestamp.second()
        )
    }
}

// ---------------------------------------------------------------------------
// TimelineWidget
// ---------------------------------------------------------------------------

/// Scrollable event-stream widget.
pub struct TimelineWidget {
    events: Vec<TimelineEvent>,
    /// Maximum events to retain.
    max_events: usize,
    /// When `true`, the widget does NOT auto-scroll on new events.
    scroll_locked: bool,
    /// Scroll offset from the bottom (0 = at bottom).
    scroll_offset: usize,
}

impl Default for TimelineWidget {
    fn default() -> Self {
        Self::new(1000)
    }
}

impl TimelineWidget {
    /// Create a timeline that retains at most `max_events` entries.
    pub fn new(max_events: usize) -> Self {
        Self {
            events: Vec::new(),
            max_events,
            scroll_locked: false,
            scroll_offset: 0,
        }
    }

    /// Push a new event. Auto-scrolls to bottom unless scroll-locked.
    pub fn push(&mut self, event: TimelineEvent) {
        self.events.push(event);
        if self.events.len() > self.max_events {
            self.events.remove(0);
        }
        if !self.scroll_locked {
            self.scroll_offset = 0;
        }
    }

    /// Convenience push helpers.
    pub fn info(&mut self, msg: impl Into<String>) {
        self.push(TimelineEvent::now(EventKind::Info, msg));
    }

    pub fn warn(&mut self, msg: impl Into<String>) {
        self.push(TimelineEvent::now(EventKind::Warn, msg));
    }

    pub fn error(&mut self, msg: impl Into<String>) {
        self.push(TimelineEvent::now(EventKind::Error, msg));
    }

    pub fn success(&mut self, msg: impl Into<String>) {
        self.push(TimelineEvent::now(EventKind::Success, msg));
    }

    /// Toggle scroll lock (Space bar).
    pub fn toggle_scroll_lock(&mut self) {
        self.scroll_locked = !self.scroll_locked;
        if !self.scroll_locked {
            self.scroll_offset = 0;
        }
    }

    /// Whether auto-scroll is paused.
    pub fn is_scroll_locked(&self) -> bool {
        self.scroll_locked
    }

    /// Scroll up (toward older events).
    pub fn scroll_up(&mut self) {
        self.scroll_offset = self
            .scroll_offset
            .saturating_add(1)
            .min(self.events.len().saturating_sub(1));
    }

    /// Scroll down (toward newer events).
    pub fn scroll_down(&mut self) {
        self.scroll_offset = self.scroll_offset.saturating_sub(1);
    }

    /// Number of events stored.
    pub fn event_count(&self) -> usize {
        self.events.len()
    }

    /// All stored events (oldest first).
    pub fn events(&self) -> &[TimelineEvent] {
        &self.events
    }

    /// Render the widget into `buf` at `area`.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let lock_indicator = if self.scroll_locked { " [PAUSED]" } else { "" };
        let title = format!(" Timeline{} ", lock_indicator);
        let block = Block::default().borders(Borders::ALL).title(title);
        let inner = block.inner(area);
        block.render(area, buf);

        let visible_height = inner.height as usize;
        if visible_height == 0 || self.events.is_empty() {
            return;
        }

        // Build all rendered lines newest-at-bottom.
        let all_lines: Vec<Line> = self
            .events
            .iter()
            .map(|ev| {
                let time_span = Span::styled(
                    format!("[{}] ", ev.time_str()),
                    Style::default().fg(Color::DarkGray),
                );
                let kind_span = Span::styled(
                    format!("{} ", ev.kind.label()),
                    Style::default()
                        .fg(ev.kind.color())
                        .add_modifier(Modifier::BOLD),
                );
                let msg_span = Span::styled(ev.message.clone(), Style::default().fg(Color::White));
                Line::from(vec![time_span, kind_span, msg_span])
            })
            .collect();

        // Determine slice to show based on scroll offset.
        let total = all_lines.len();
        let end = total.saturating_sub(self.scroll_offset);
        let start = end.saturating_sub(visible_height);
        let visible_lines: Vec<Line> = all_lines[start..end].to_vec();

        Paragraph::new(visible_lines).render(inner, buf);
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_push_increases_count() {
        let mut tl = TimelineWidget::new(100);
        tl.info("hello");
        tl.warn("world");
        assert_eq!(tl.event_count(), 2);
    }

    #[test]
    fn test_max_events_evicts_oldest() {
        let mut tl = TimelineWidget::new(3);
        tl.info("a");
        tl.info("b");
        tl.info("c");
        tl.info("d"); // should evict "a"
        assert_eq!(tl.event_count(), 3);
        assert_eq!(tl.events()[0].message, "b");
    }

    #[test]
    fn test_auto_scroll_reset_on_push() {
        let mut tl = TimelineWidget::new(100);
        tl.scroll_offset = 5;
        tl.info("new event");
        // Not locked, so offset resets
        assert_eq!(tl.scroll_offset, 0);
    }

    #[test]
    fn test_scroll_lock_preserves_offset_on_push() {
        let mut tl = TimelineWidget::new(100);
        tl.toggle_scroll_lock();
        tl.scroll_offset = 3;
        tl.info("new event");
        assert_eq!(tl.scroll_offset, 3);
    }

    #[test]
    fn test_toggle_scroll_lock() {
        let mut tl = TimelineWidget::new(100);
        assert!(!tl.is_scroll_locked());
        tl.toggle_scroll_lock();
        assert!(tl.is_scroll_locked());
        tl.toggle_scroll_lock();
        assert!(!tl.is_scroll_locked());
    }

    #[test]
    fn test_toggle_scroll_lock_off_resets_offset() {
        let mut tl = TimelineWidget::new(100);
        tl.toggle_scroll_lock(); // lock
        tl.scroll_offset = 5;
        tl.toggle_scroll_lock(); // unlock
        assert_eq!(tl.scroll_offset, 0);
    }

    #[test]
    fn test_scroll_up_increases_offset() {
        let mut tl = TimelineWidget::new(100);
        for i in 0..10 {
            tl.info(format!("event {}", i));
        }
        tl.scroll_up();
        assert_eq!(tl.scroll_offset, 1);
        tl.scroll_up();
        assert_eq!(tl.scroll_offset, 2);
    }

    #[test]
    fn test_scroll_down_decreases_offset() {
        let mut tl = TimelineWidget::new(100);
        for i in 0..10 {
            tl.info(format!("event {}", i));
        }
        tl.scroll_up();
        tl.scroll_up();
        tl.scroll_down();
        assert_eq!(tl.scroll_offset, 1);
    }

    #[test]
    fn test_scroll_down_clamps_at_zero() {
        let mut tl = TimelineWidget::new(100);
        tl.info("a");
        tl.scroll_down();
        assert_eq!(tl.scroll_offset, 0);
    }

    #[test]
    fn test_scroll_up_clamps_at_event_count() {
        let mut tl = TimelineWidget::new(100);
        tl.info("only one");
        // Can't scroll past index 0
        tl.scroll_up();
        tl.scroll_up();
        assert_eq!(tl.scroll_offset, 0);
    }

    #[test]
    fn test_convenience_helpers_set_correct_kinds() {
        let mut tl = TimelineWidget::new(100);
        tl.info("i");
        tl.warn("w");
        tl.error("e");
        tl.success("s");
        assert_eq!(tl.events()[0].kind, EventKind::Info);
        assert_eq!(tl.events()[1].kind, EventKind::Warn);
        assert_eq!(tl.events()[2].kind, EventKind::Error);
        assert_eq!(tl.events()[3].kind, EventKind::Success);
    }

    #[test]
    fn test_event_time_str_format() {
        let ev = TimelineEvent::now(EventKind::Info, "test");
        let ts = ev.time_str();
        // Must be HH:MM:SS (8 chars, two colons)
        assert_eq!(ts.len(), 8);
        let parts: Vec<&str> = ts.split(':').collect();
        assert_eq!(parts.len(), 3);
        // Each part must be 2 digits
        for part in &parts {
            assert_eq!(part.len(), 2);
            assert!(part.chars().all(|c| c.is_ascii_digit()));
        }
    }

    #[test]
    fn test_event_kind_colors() {
        assert_eq!(EventKind::Info.color(), Color::Blue);
        assert_eq!(EventKind::Warn.color(), Color::Yellow);
        assert_eq!(EventKind::Error.color(), Color::Red);
        assert_eq!(EventKind::Success.color(), Color::Green);
    }

    #[test]
    fn test_event_kind_labels() {
        assert_eq!(EventKind::Info.label(), "INFO");
        assert_eq!(EventKind::Warn.label(), "WARN");
        assert_eq!(EventKind::Error.label(), "ERR ");
        assert_eq!(EventKind::Success.label(), "OK  ");
    }

    #[test]
    fn test_default_is_unlocked_empty() {
        let tl = TimelineWidget::default();
        assert_eq!(tl.event_count(), 0);
        assert!(!tl.is_scroll_locked());
    }
}
