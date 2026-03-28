//! TraceFlags - Flags for a trace.

/// TraceFlags represents the flags for a trace.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TraceFlags(u8);

impl TraceFlags {
    /// Create new trace flags.
    pub fn new(flags: u8) -> Self {
        Self(flags & 0x01)
    }

    /// Create default flags (sampled).
    pub fn default() -> Self {
        Self(0x01)
    }

    /// Create unsampled flags.
    pub fn unsampled() -> Self {
        Self(0x00)
    }

    /// Check if sampled.
    pub fn is_sampled(&self) -> bool {
        (self.0 & 0x01) != 0
    }

    /// Set sampled flag.
    pub fn with_sampled(self, sampled: bool) -> Self {
        if sampled {
            Self(self.0 | 0x01)
        } else {
            Self(self.0 & !0x01)
        }
    }

    /// Get the raw flags.
    pub fn bits(&self) -> u8 {
        self.0
    }
}

impl Default for TraceFlags {
    fn default() -> Self {
        Self::default()
    }
}
