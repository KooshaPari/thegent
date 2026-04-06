//! # VesselRs
//!
//! Shared memory primitives for multi-agent orchestration.
//!
//! ## Architecture
//!
//! This crate follows **Hexagonal Architecture** (Ports & Adapters) with **Clean Architecture** layers.

pub mod domain;
pub mod application;
pub mod ports;
pub mod adapters;

// Re-export for convenience
pub use domain::entities::*;
pub use domain::value_objects::*;
pub use domain::events::*;
pub use application::commands::*;
pub use application::queries::*;
pub use application::use_cases::*;
pub use ports::driven::CommandCachePort;
pub use ports::driven::CircuitBreakerPort;
pub use ports::driven::HealthPort;

/// Shared memory interface for process coordination.
pub mod shm {
    pub use crate::adapters::sharedmemory::SharedMemoryAdapter;
}

#[cfg(feature = "python")]
mod python_bridge {
    use pyo3::prelude::*;

    #[pymodule]
    fn vesselpy(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_class::<crate::domain::entities::SharedMemoryBlock>()?;
        m.add_class::<crate::ports::driven::CommandCachePort>()?;
        m.add("__version__", env!("CARGO_PKG_VERSION"))?;
        Ok(())
    }
}
