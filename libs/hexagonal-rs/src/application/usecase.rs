//! Use Case implementation
//!
//! Use cases represent the application-specific business rules.
//! They orchestrate the flow of data and coordinate domain objects.

use crate::ports::InputPort;
use std::marker::PhantomData;

/// Marker trait for use cases.
pub trait UseCaseMarker: Send + Sync {}

/// Base use case trait.
pub trait UseCase<I, O>: InputPort + UseCaseMarker {
    fn execute(&self, input: I) -> O;
}

/// Async use case trait.
pub trait AsyncUseCase<I, O>: InputPort + UseCaseMarker {
    async fn execute(&self, input: I) -> O;
}

/// Command use case.
pub trait CommandUseCase<C, R>: UseCase<C, R> {}

/// Query use case.
pub trait QueryUseCase<Q, R>: UseCase<Q, R> {}

/// Command handler for CQRS.
pub struct CommandHandler<UC, C, R>
where
    UC: CommandUseCase<C, R>,
{
    use_case: UC,
    _phantom: PhantomData<(C, R)>,
}

impl<UC, C, R> CommandHandler<UC, C, R>
where
    UC: CommandUseCase<C, R>,
{
    pub fn new(use_case: UC) -> Self {
        Self {
            use_case,
            _phantom: PhantomData,
        }
    }

    pub fn execute(&self, command: C) -> R {
        self.use_case.execute(command)
    }
}

/// Query handler for CQRS.
pub struct QueryHandler<UC, Q, R>
where
    UC: QueryUseCase<Q, R>,
{
    use_case: UC,
    _phantom: PhantomData<(Q, R)>,
}

impl<UC, Q, R> QueryHandler<UC, Q, R>
where
    UC: QueryUseCase<Q, R>,
{
    pub fn new(use_case: UC) -> Self {
        Self {
            use_case,
            _phantom: PhantomData,
        }
    }

    pub fn execute(&self, query: Q) -> R {
        self.use_case.execute(query)
    }
}
