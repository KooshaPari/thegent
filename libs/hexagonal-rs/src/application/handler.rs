//! Application Handlers
//!
//! Handlers coordinate use cases and manage the flow of data
//! between input ports and output ports.

use std::marker::PhantomData;
use std::sync::Arc;
use crate::HexagonalResult;
use crate::application::usecase::{AsyncUseCase, UseCase};
use crate::application::dto::Command;

/// Command handler that executes use cases.
pub struct ApplicationCommandHandler<UC>
where
    UC: UseCase<Command, HexagonalResult<()>>,
{
    use_case: Arc<UC>,
}

impl<UC> ApplicationCommandHandler<UC>
where
    UC: UseCase<Command, HexagonalResult<()>> + 'static,
{
    pub fn new(use_case: Arc<UC>) -> Self {
        Self { use_case }
    }

    pub fn handle(&self, command: Command) -> HexagonalResult<()> {
        self.use_case.execute(command)
    }
}

/// Query handler that executes use cases.
pub struct ApplicationQueryHandler<UC, Q, R>
where
    UC: UseCase<Q, HexagonalResult<R>>,
{
    use_case: Arc<UC>,
    _phantom: PhantomData<(Q, R)>,
}

impl<UC, Q, R> ApplicationQueryHandler<UC, Q, R>
where
    UC: UseCase<Q, HexagonalResult<R>> + 'static,
{
    pub fn new(use_case: Arc<UC>) -> Self {
        Self {
            use_case,
            _phantom: PhantomData,
        }
    }

    pub fn handle(&self, query: Q) -> HexagonalResult<R> {
        self.use_case.execute(query)
    }
}

/// Async query handler.
pub struct AsyncQueryHandler<UC, Q, R>
where
    UC: AsyncUseCase<Q, HexagonalResult<R>>,
{
    use_case: Arc<UC>,
    _phantom: PhantomData<(Q, R)>,
}

impl<UC, Q, R> AsyncQueryHandler<UC, Q, R>
where
    UC: AsyncUseCase<Q, HexagonalResult<R>> + 'static,
{
    pub fn new(use_case: Arc<UC>) -> Self {
        Self {
            use_case,
            _phantom: PhantomData,
        }
    }

    pub async fn handle(&self, query: Q) -> HexagonalResult<R> {
        self.use_case.execute(query).await
    }
}

/// Request handler trait for HTTP/REST adapters.
pub trait RequestHandler<Req, Res>: Send + Sync {
    fn handle(&self, request: Req) -> Res;
}

/// Presenter trait for formatting responses.
pub trait Presenter<O, V>: Send + Sync {
    fn present(&self, output: O) -> V;
}

/// Default presenter that returns output as-is.
pub struct IdentityPresenter;

impl<T> Presenter<T, T> for IdentityPresenter {
    fn present(&self, output: T) -> T {
        output
    }
}
