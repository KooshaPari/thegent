//! AgilePlus P2P — Git-backed state export
//!
//! This crate provides functionality to export SQLite state to deterministic,
//! git-friendly JSON files for P2P synchronization.
//!
//! # Example
//!
//! ```ignore
//! use agileplus_p2p::export::export_state;
//!
//! let stats = export_state(&event_store, &snapshot_store, &device_store,
//!     &entities, output_dir).await?;
//! println!("Exported {} events", stats.events_exported);
//! ```

pub mod device;
pub mod domain;
pub mod error;
pub mod events;
pub mod export;

pub use device::{DeviceNode, DeviceStore, InMemoryDeviceStore};
pub use export::{export_state, ExportError, ExportStats};
