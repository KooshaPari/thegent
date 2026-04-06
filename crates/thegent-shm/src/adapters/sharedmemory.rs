//! # Shared Memory Adapter
//!
//! Production implementation using memory-mapped files.
//!
//! ## Architecture
//!
//! Uses `memmap2` for cross-process shared state.
//! Based on the original thegent SHM implementation.


/// Shared memory adapter for production use
///
/// Uses memory-mapped files for cross-process state sharing.
/// This is a stub - the full implementation will be extracted from thegent.
pub struct SharedMemoryAdapter {
    // TODO: Implement with memmap2
    _placeholder: (),
}

impl SharedMemoryAdapter {
    /// Create a new shared memory adapter
    pub fn new() -> Self {
        Self { _placeholder: () }
    }
}

impl Default for SharedMemoryAdapter {
    fn default() -> Self {
        Self::new()
    }
}

// Implement ports for SharedMemoryAdapter
// These will be implemented when the actual SHM logic is migrated
