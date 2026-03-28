//! Phenotype Tracing Library
//!
//! A comprehensive distributed tracing library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - OpenTelemetry standards
//! - xDD methodologies (TDD, BDD)
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer   |  <-- Pure tracing concepts
//! |  - Span          |
//! |  - TraceId       |
//! |  - SpanId        |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Tracing services
//! |  - Tracer        |
//! |  - SpanBuilder   |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- Export adapters
//! |  - OTLP          |
//! |  - Jaeger        |
//! |  - Zipkin        |
//! +------------------+
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs, missing_debug_implementations)]

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;
pub use adapters::*;
