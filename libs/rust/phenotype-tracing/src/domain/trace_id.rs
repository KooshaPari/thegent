//! TraceId - Unique identifier for a trace.
//!
//! A TraceId is a unique identifier that links together all spans
//! in a distributed trace.

use std::fmt;
use std::str::FromStr;

/// Length of trace ID in bytes.
pub const TRACE_ID_LEN: usize = 16;

/// TraceId represents a unique identifier for a trace.
///
/// TraceIds are 16-byte random values that uniquely identify
/// a trace across services and processes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TraceId([u8; TRACE_ID_LEN]);

impl TraceId {
    /// Generate a new random TraceId.
    pub fn generate() -> Self {
        Self(uuid::Uuid::new_v4().as_bytes()[..TRACE_ID_LEN].try_into().unwrap())
    }

    /// Create a TraceId from bytes.
    ///
    /// # Panics
    ///
    /// Panics if the slice is not exactly 16 bytes.
    pub fn from_bytes(bytes: [u8; TRACE_ID_LEN]) -> Self {
        Self(bytes)
    }

    /// Get the bytes of the TraceId.
    pub fn as_bytes(&self) -> &[u8; TRACE_ID_LEN] {
        &self.0
    }

    /// Convert to hex string.
    pub fn to_hex(&self) -> String {
        hex::encode(self.0)
    }

    /// Check if this is a null/nil trace ID.
    pub fn is_null(&self) -> bool {
        self.0.iter().all(|&b| b == 0)
    }

    /// Get the null/nil TraceId.
    pub fn nil() -> Self {
        Self([0u8; TRACE_ID_LEN])
    }
}

impl Default for TraceId {
    fn default() -> Self {
        Self::nil()
    }
}

impl fmt::Display for TraceId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.to_hex())
    }
}

impl FromStr for TraceId {
    type Err = hex::FromHexError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let bytes = hex::decode(s)?;
        if bytes.len() != TRACE_ID_LEN {
            return Err(hex::FromHexError::InvalidLength);
        }
        let mut arr = [0u8; TRACE_ID_LEN];
        arr.copy_from_slice(&bytes);
        Ok(TraceId(arr))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate() {
        let trace_id = TraceId::generate();
        assert!(!trace_id.is_null());
    }

    #[test]
    fn test_hex_roundtrip() {
        let trace_id = TraceId::generate();
        let hex = trace_id.to_hex();
        let parsed: TraceId = hex.parse().unwrap();
        assert_eq!(trace_id, parsed);
    }

    #[test]
    fn test_nil() {
        let nil = TraceId::nil();
        assert!(nil.is_null());
    }
}
