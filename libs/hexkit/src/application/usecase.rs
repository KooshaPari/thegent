//! Use Cases - Application-Specific Business Rules
//!
//! Use cases represent the application-specific business rules. They orchestrate
//! domain objects and ports to accomplish a specific task.
//!
//! ## Naming Conventions
//!
//! - Commands: Imperative mood (CreateOrder, CancelReservation)
//! - Queries: Question form (GetOrder, ListProducts)
//!
//! ## Example
//!
//! ```rust
//! use hexkit::application::usecase::UseCase;
//! use hexkit::HexResult;
//!
//! struct SimpleUseCase;
//!
//! impl UseCase<String, String> for SimpleUseCase {
//!     async fn execute(&self, input: String) -> HexResult<String> {
//!         Ok(format!("Processed: {}", input))
//!     }
//! }
//! ```

use crate::ports::inbound::{InputPort, CommandHandler, QueryHandler};
use crate::HexResult;

/// Base use case trait
pub trait UseCase<I, O> {
    fn execute(&self, input: I) -> impl std::future::Future<Output = HexResult<O>> + Send;
}

/// Command use case marker
pub trait CommandUseCase<C>: UseCase<C, ()> {}

/// Query use case marker
pub trait QueryUseCase<Q, R>: UseCase<Q, R> {}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug)]
    struct TestUseCase;

    impl UseCase<String, String> for TestUseCase {
        async fn execute(&self, input: String) -> HexResult<String> {
            Ok(format!("Processed: {}", input))
        }
    }

    #[test]
    fn test_use_case_sync() {
        // Test that UseCase trait can be implemented
        let use_case = TestUseCase;
        assert!(true, "UseCase can be implemented");
    }
}
