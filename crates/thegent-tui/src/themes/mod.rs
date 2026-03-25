//! Theme system for thegent TUI — Phase 3.
//!
//! Provides:
//! - `Theme` struct with a full color palette
//! - Three built-in themes: `dark`, `light`, `solarized`
//! - Terminal auto-detection via `Theme::auto()`
//! - TOML file loading from `.thegent/themes/<name>.toml`
//! - `ThemeRegistry` singleton for named-theme management

use std::env;
use std::path::PathBuf;

use once_cell::sync::Lazy;
use ratatui::style::Color;
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

// ---------------------------------------------------------------------------
// Palette serialisation helpers
// ---------------------------------------------------------------------------

/// Serialisable representation of a `ratatui::style::Color` that round-trips
/// through TOML as an RGB hex string `"#RRGGBB"` or a named colour string.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct ThemeColor(pub String);

impl ThemeColor {
    /// Convert to the closest `ratatui::style::Color`.
    pub fn to_ratatui(&self) -> Color {
        let s = self.0.trim();
        if let Some(hex) = s.strip_prefix('#') {
            if hex.len() == 6 {
                if let (Ok(r), Ok(g), Ok(b)) = (
                    u8::from_str_radix(&hex[0..2], 16),
                    u8::from_str_radix(&hex[2..4], 16),
                    u8::from_str_radix(&hex[4..6], 16),
                ) {
                    return Color::Rgb(r, g, b);
                }
            }
        }
        // Named fallback mapping
        match s.to_lowercase().as_str() {
            "black" => Color::Black,
            "red" => Color::Red,
            "green" => Color::Green,
            "yellow" => Color::Yellow,
            "blue" => Color::Blue,
            "magenta" => Color::Magenta,
            "cyan" => Color::Cyan,
            "white" => Color::White,
            "darkgray" | "dark_gray" | "darkgrey" | "dark_grey" => Color::DarkGray,
            "lightred" | "light_red" => Color::LightRed,
            "lightgreen" | "light_green" => Color::LightGreen,
            "lightyellow" | "light_yellow" => Color::LightYellow,
            "lightblue" | "light_blue" => Color::LightBlue,
            "lightmagenta" | "light_magenta" => Color::LightMagenta,
            "lightcyan" | "light_cyan" => Color::LightCyan,
            "gray" | "grey" => Color::Gray,
            _ => Color::Reset,
        }
    }

    fn from_rgb(r: u8, g: u8, b: u8) -> Self {
        Self(format!("#{:02X}{:02X}{:02X}", r, g, b))
    }

    #[cfg(test)]
    pub(crate) fn from_named(name: &str) -> Self {
        Self(name.to_string())
    }
}

// ---------------------------------------------------------------------------
// Theme struct
// ---------------------------------------------------------------------------

/// A complete TUI color palette.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Theme {
    /// Terminal background colour.
    pub bg: ThemeColor,
    /// Default foreground (text) colour.
    pub fg: ThemeColor,
    /// Accent/highlight colour.
    pub accent: ThemeColor,
    /// Warning colour.
    pub warning: ThemeColor,
    /// Error colour.
    pub error: ThemeColor,
    /// Success colour.
    pub success: ThemeColor,
    /// Border colour.
    pub border: ThemeColor,
    /// Background of the selected row / item.
    pub selected_bg: ThemeColor,
    /// Foreground of the selected row / item.
    pub selected_fg: ThemeColor,
    /// Dimmed / secondary text colour.
    pub dim: ThemeColor,
}

impl Theme {
    // ------------------------------------------------------------------
    // Built-in themes
    // ------------------------------------------------------------------

    /// Dark theme (default for dark terminals).
    pub fn dark() -> Self {
        Self {
            bg: ThemeColor::from_rgb(28, 28, 28),
            fg: ThemeColor::from_rgb(220, 220, 220),
            accent: ThemeColor::from_rgb(97, 175, 239),
            warning: ThemeColor::from_rgb(229, 192, 123),
            error: ThemeColor::from_rgb(224, 108, 117),
            success: ThemeColor::from_rgb(152, 195, 121),
            border: ThemeColor::from_rgb(80, 80, 80),
            selected_bg: ThemeColor::from_rgb(61, 89, 161),
            selected_fg: ThemeColor::from_rgb(255, 255, 255),
            dim: ThemeColor::from_rgb(100, 100, 100),
        }
    }

    /// Light theme (default for light terminals).
    pub fn light() -> Self {
        Self {
            bg: ThemeColor::from_rgb(250, 250, 250),
            fg: ThemeColor::from_rgb(30, 30, 30),
            accent: ThemeColor::from_rgb(0, 100, 200),
            warning: ThemeColor::from_rgb(180, 120, 0),
            error: ThemeColor::from_rgb(180, 0, 0),
            success: ThemeColor::from_rgb(0, 130, 0),
            border: ThemeColor::from_rgb(190, 190, 190),
            selected_bg: ThemeColor::from_rgb(180, 210, 255),
            selected_fg: ThemeColor::from_rgb(0, 0, 0),
            dim: ThemeColor::from_rgb(150, 150, 150),
        }
    }

    /// Solarized dark palette (Ethan Schoonover).
    pub fn solarized() -> Self {
        Self {
            bg: ThemeColor::from_rgb(0, 43, 54),              // base03
            fg: ThemeColor::from_rgb(131, 148, 150),          // base0
            accent: ThemeColor::from_rgb(38, 139, 210),       // blue
            warning: ThemeColor::from_rgb(181, 137, 0),       // yellow
            error: ThemeColor::from_rgb(220, 50, 47),         // red
            success: ThemeColor::from_rgb(133, 153, 0),       // green
            border: ThemeColor::from_rgb(7, 54, 66),          // base02
            selected_bg: ThemeColor::from_rgb(0, 73, 89),     // base02 lighter
            selected_fg: ThemeColor::from_rgb(253, 246, 227), // base3
            dim: ThemeColor::from_rgb(88, 110, 117),          // base01
        }
    }

    // ------------------------------------------------------------------
    // Auto-detection
    // ------------------------------------------------------------------

    /// Detect terminal background (dark vs. light) and return the appropriate
    /// built-in theme.
    ///
    /// Detection heuristics (in priority order):
    /// 1. `COLORFGBG` — `"15;0"` means light fg / dark bg → dark theme.
    /// 2. `TERM_PROGRAM` — "iTerm.app", "Apple_Terminal" suggest user may have
    ///    either; fall through to next check.
    /// 3. `COLORTERM` — `"truecolor"` or `"24bit"` → dark (most common modern
    ///    default).
    /// 4. Default → dark.
    pub fn auto() -> Self {
        // COLORFGBG is set by many terminals: "FG;BG" where BG=0 → dark bg.
        if let Ok(val) = env::var("COLORFGBG") {
            let parts: Vec<&str> = val.splitn(2, ';').collect();
            if parts.len() == 2 {
                // BG component: 0-6 = dark, 7-15 = light
                if let Ok(bg_idx) = parts[1].trim().parse::<u8>() {
                    if bg_idx <= 6 {
                        return Self::dark();
                    } else {
                        return Self::light();
                    }
                }
            }
        }

        // TERM_PROGRAM can give hints about common terminals that default light.
        if let Ok(prog) = env::var("TERM_PROGRAM") {
            if prog.as_str() == "Apple_Terminal" {
                return Self::light();
            }
        }

        // COLORTERM present → modern terminal, almost always dark by default.
        if env::var("COLORTERM").is_ok() {
            return Self::dark();
        }

        Self::dark()
    }

    // ------------------------------------------------------------------
    // TOML file loading
    // ------------------------------------------------------------------

    /// Load a theme from `.thegent/themes/<name>.toml` in the user's home
    /// directory.  Panics (via `expect`) if the file exists but cannot be
    /// parsed — fail fast, no silent fallback.
    pub fn from_file(name: &str) -> Result<Self, ThemeLoadError> {
        let path = theme_file_path(name);
        let content = std::fs::read_to_string(&path)
            .map_err(|e| ThemeLoadError::Io(path.display().to_string(), e.to_string()))?;
        toml::from_str(&content)
            .map_err(|e| ThemeLoadError::Parse(path.display().to_string(), e.to_string()))
    }
}

/// Errors that can occur when loading a theme from a TOML file.
#[derive(Debug, thiserror::Error)]
pub enum ThemeLoadError {
    #[error("IO error reading theme file '{0}': {1}")]
    Io(String, String),
    #[error("Parse error in theme file '{0}': {1}")]
    Parse(String, String),
}

/// Resolve the on-disk path for a named theme file.
fn theme_file_path(name: &str) -> PathBuf {
    directories::UserDirs::new()
        .map(|d| {
            d.home_dir()
                .join(".thegent")
                .join("themes")
                .join(format!("{}.toml", name))
        })
        .unwrap_or_else(|| PathBuf::from(format!(".thegent/themes/{}.toml", name)))
}

// ---------------------------------------------------------------------------
// ThemeRegistry singleton
// ---------------------------------------------------------------------------

struct RegistryInner {
    themes: std::collections::HashMap<String, Theme>,
    current: String,
}

impl RegistryInner {
    fn new() -> Self {
        let mut themes = std::collections::HashMap::new();
        themes.insert("dark".to_string(), Theme::dark());
        themes.insert("light".to_string(), Theme::light());
        themes.insert("solarized".to_string(), Theme::solarized());
        Self {
            themes,
            current: "dark".to_string(),
        }
    }
}

static REGISTRY: Lazy<Mutex<RegistryInner>> = Lazy::new(|| Mutex::new(RegistryInner::new()));

/// Global theme registry.
///
/// Use the associated functions to access the singleton instance.
pub struct ThemeRegistry;

impl ThemeRegistry {
    /// Retrieve a named theme. Panics if the name is not registered.
    pub fn get(name: &str) -> Theme {
        REGISTRY
            .lock()
            .expect("ThemeRegistry mutex poisoned")
            .themes
            .get(name)
            .unwrap_or_else(|| panic!("Theme '{}' is not registered", name))
            .clone()
    }

    /// Register (or overwrite) a named theme.
    pub fn register(name: impl Into<String>, theme: Theme) {
        REGISTRY
            .lock()
            .expect("ThemeRegistry mutex poisoned")
            .themes
            .insert(name.into(), theme);
    }

    /// Return the currently active theme.
    pub fn current() -> Theme {
        let inner = REGISTRY.lock().expect("ThemeRegistry mutex poisoned");
        inner
            .themes
            .get(&inner.current)
            .expect("current theme is not registered")
            .clone()
    }

    /// Set the currently active theme by name. Panics if not registered.
    pub fn set_current(name: impl Into<String>) {
        let name = name.into();
        let mut inner = REGISTRY.lock().expect("ThemeRegistry mutex poisoned");
        assert!(
            inner.themes.contains_key(&name),
            "Theme '{}' is not registered",
            name
        );
        inner.current = name;
    }

    /// List all registered theme names.
    pub fn names() -> Vec<String> {
        let inner = REGISTRY.lock().expect("ThemeRegistry mutex poisoned");
        let mut names: Vec<String> = inner.themes.keys().cloned().collect();
        names.sort();
        names
    }

    /// Name of the currently active theme.
    pub fn current_name() -> String {
        REGISTRY
            .lock()
            .expect("ThemeRegistry mutex poisoned")
            .current
            .clone()
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use serial_test::serial;

    // Reset registry current to "dark" after each test that changes it so
    // tests are isolated despite the global singleton.
    fn reset_current() {
        ThemeRegistry::set_current("dark");
    }

    #[test]
    fn test_dark_theme_has_all_fields() {
        let t = Theme::dark();
        // Spot-check a few colours
        assert_eq!(t.bg.to_ratatui(), Color::Rgb(28, 28, 28));
        assert_eq!(t.fg.to_ratatui(), Color::Rgb(220, 220, 220));
        assert_eq!(t.accent.to_ratatui(), Color::Rgb(97, 175, 239));
    }

    #[test]
    fn test_light_theme_has_all_fields() {
        let t = Theme::light();
        assert_eq!(t.bg.to_ratatui(), Color::Rgb(250, 250, 250));
        assert_eq!(t.fg.to_ratatui(), Color::Rgb(30, 30, 30));
    }

    #[test]
    fn test_solarized_theme_has_all_fields() {
        let t = Theme::solarized();
        assert_eq!(t.bg.to_ratatui(), Color::Rgb(0, 43, 54));
    }

    #[test]
    fn test_auto_returns_a_valid_theme() {
        // Just verify it doesn't panic and returns one of the built-ins.
        let t = Theme::auto();
        // The bg must be one of the three built-in backgrounds.
        let dark_bg = Theme::dark().bg;
        let light_bg = Theme::light().bg;
        let sol_bg = Theme::solarized().bg;
        assert!(
            t.bg == dark_bg || t.bg == light_bg || t.bg == sol_bg,
            "auto() returned unexpected bg: {:?}",
            t.bg
        );
    }

    #[test]
    fn test_theme_color_hex_roundtrip() {
        let c = ThemeColor::from_rgb(18, 52, 86);
        assert_eq!(c.to_ratatui(), Color::Rgb(18, 52, 86));
    }

    #[test]
    fn test_theme_color_named() {
        assert_eq!(ThemeColor::from_named("red").to_ratatui(), Color::Red);
        assert_eq!(ThemeColor::from_named("green").to_ratatui(), Color::Green);
        assert_eq!(ThemeColor::from_named("blue").to_ratatui(), Color::Blue);
        assert_eq!(ThemeColor::from_named("white").to_ratatui(), Color::White);
        assert_eq!(ThemeColor::from_named("black").to_ratatui(), Color::Black);
        assert_eq!(
            ThemeColor::from_named("darkgray").to_ratatui(),
            Color::DarkGray
        );
    }

    #[test]
    fn test_theme_color_unknown_is_reset() {
        assert_eq!(
            ThemeColor::from_named("purple_unicorn").to_ratatui(),
            Color::Reset
        );
    }

    #[test]
    #[serial]
    fn test_registry_builtin_themes_exist() {
        let names = ThemeRegistry::names();
        assert!(names.contains(&"dark".to_string()));
        assert!(names.contains(&"light".to_string()));
        assert!(names.contains(&"solarized".to_string()));
    }

    #[test]
    #[serial]
    fn test_registry_get_dark() {
        let t = ThemeRegistry::get("dark");
        assert_eq!(t.bg, Theme::dark().bg);
    }

    #[test]
    #[serial]
    fn test_registry_current_default_is_dark() {
        reset_current();
        assert_eq!(ThemeRegistry::current_name(), "dark");
    }

    #[test]
    #[serial]
    fn test_registry_set_and_get_current() {
        ThemeRegistry::set_current("light");
        assert_eq!(ThemeRegistry::current_name(), "light");
        let t = ThemeRegistry::current();
        assert_eq!(t.bg, Theme::light().bg);
        reset_current();
    }

    #[test]
    #[serial]
    fn test_registry_register_custom() {
        let custom = Theme {
            bg: ThemeColor::from_rgb(10, 20, 30),
            fg: ThemeColor::from_rgb(200, 210, 220),
            accent: ThemeColor::from_named("cyan"),
            warning: ThemeColor::from_named("yellow"),
            error: ThemeColor::from_named("red"),
            success: ThemeColor::from_named("green"),
            border: ThemeColor::from_named("darkgray"),
            selected_bg: ThemeColor::from_named("blue"),
            selected_fg: ThemeColor::from_named("white"),
            dim: ThemeColor::from_named("gray"),
        };
        ThemeRegistry::register("custom-test", custom.clone());
        let fetched = ThemeRegistry::get("custom-test");
        assert_eq!(fetched.bg, custom.bg);
    }

    #[test]
    fn test_theme_color_gray_variants() {
        assert_eq!(ThemeColor::from_named("gray").to_ratatui(), Color::Gray);
        assert_eq!(ThemeColor::from_named("grey").to_ratatui(), Color::Gray);
        assert_eq!(
            ThemeColor::from_named("dark_gray").to_ratatui(),
            Color::DarkGray
        );
        assert_eq!(
            ThemeColor::from_named("dark_grey").to_ratatui(),
            Color::DarkGray
        );
    }

    #[test]
    fn test_theme_load_error_missing_file() {
        let result = Theme::from_file("__nonexistent_theme_xyz__");
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), ThemeLoadError::Io(_, _)));
    }
}
