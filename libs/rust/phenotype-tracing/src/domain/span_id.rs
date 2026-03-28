//! SpanId - Unique identifier for a span.

/// Length of span ID in bytes.
pub const SPAN_ID_LEN: usize = 8;

/// SpanId represents a unique identifier for a span within a trace.
///
/// SpanIds are 8-byte random values that uniquely identify
/// a span within a trace.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct SpanId([u8; SPAN_ID_LEN]);

impl SpanId {
    /// Generate a new random SpanId.
    pub fn generate() -> Self {
        let mut bytes = [0u8; SPAN_ID_LEN];
        // Use first 8 bytes of UUID
        let uuid_bytes = uuid::Uuid::new_v4().as_bytes();
        bytes.copy_from_slice(&uuid_bytes[..SPAN_ID_LEN]);
        Self(bytes)
    }

    /// Create a SpanId from bytes.
    ///
    /// # Panics
    ///
    /// Panics if the slice is not exactly 8 bytes.
    pub fn from_bytes(bytes: [u8; SPAN_ID_LEN]) -> Self {
        Self(bytes)
    }

    /// Get the bytes of the SpanId.
    pub fn as_bytes(&self) -> &[u8; SPAN_ID_LEN] {
        &self.0
    }

    /// Convert to hex string.
    pub fn to_hex(&self) -> String {
        hex::encode(self.0)
    }

    /// Check if this is a null/nil span ID.
    pub fn is_null(&self) -> bool {
        self.0.iter().all(|&b| b == 0)
    }

    /// Get the null/nil SpanId.
    pub fn nil() -> Self {
        Self([0u8; SPAN_ID_LEN])
    }
}

impl Default for SpanId {
    fn default() -> Self {
        Self::nil()
    }
}

impl std::fmt::Display for SpanId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.to_hex())
    }
}

impl std::str::FromStr for SpanId {
    type Err = hex::FromHexError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let bytes = hex::decode(s)?;
        if bytes.len() != SPAN_ID_LEN {
            return Err(hex::FromHexError::InvalidLength);
        }
        let mut arr = [0u8; SPAN_ID_LEN];
        arr.copy_from_slice(&bytes);
        Ok(SpanId(arr))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate() {
        let span_id = SpanId::generate();
        assert!(!span_id.is_null());
    }

    #[test]
    fn test_hex_roundtrip() {
        let span_id = SpanId::generate();
        let hex = span_id.to_hex();
        let parsed: SpanId = hex.parse().unwrap();
        assert_eq!(span_id, parsed);
    }
}
