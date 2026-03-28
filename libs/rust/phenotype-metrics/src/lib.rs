//! # Phenotype Metrics Library
//!
//! A comprehensive metrics library for Rust following:
//!   - Hexagonal Architecture (Ports & Adapters)
//!   - Clean Architecture principles
//!   - SOLID principles
//!   - xDD methodologies (TDD)
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         ADAPTERS                                     │
//! │  ┌─────────────────┐  ┌─────────────────┐                          │
//! │  │  PrometheusAdapter│  │  StatsdAdapter  │                          │
//! │  └────────┬────────┘  └────────┬────────┘                          │
//! └───────────┼────────────────────┼──────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                      APPLICATION LAYER                              │
//! │  ┌─────────────────┐  ┌─────────────────┐                         │
//! │  │  MetricsCollector│  │  MetricRecorder │                         │
//! │  └────────┬────────┘  └────────┬────────┘                         │
//! └───────────┼────────────────────┼──────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         DOMAIN LAYER                                │
//! │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
//! │  │  Metric         │  │  MetricType     │  │  MetricError   │   │
//! │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
//! └─────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! # License
//! MIT

#![forbid(unsafe_code)]
#![warn(missing_docs, missing_debug_implementations)]

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;
pub use adapters::*;
