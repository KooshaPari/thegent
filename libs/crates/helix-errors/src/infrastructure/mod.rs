//! Infrastructure layer - Error handling integrations

#[cfg(feature = "trace")]
pub mod tracing;

#[cfg(feature = "std")]
pub mod logging;

#[cfg(feature = "serde")]
pub mod serialization;
