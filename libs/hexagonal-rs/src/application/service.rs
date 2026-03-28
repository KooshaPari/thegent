//! Application Services
//!
//! Application services orchestrate use cases and manage
//! the flow of data in the application layer.

use std::marker::PhantomData;
use std::sync::Arc;
use crate::HexagonalResult;
use crate::application::dto::{DTO, Query};
use crate::application::usecase::{UseCase, UseCaseMarker};

/// Application service that coordinates use cases.
pub struct ApplicationService<C, Q, CQ, QR>
where
    C: UseCase<CQ, HexagonalResult<()>>,
    Q: UseCase<Query, HexagonalResult<DTO<QR>>>,
{
    command_use_case: Arc<C>,
    query_use_case: Arc<Q>,
    _phantom: PhantomData<(CQ, QR)>,
}

impl<C, Q, CQ, QR> ApplicationService<C, Q, CQ, QR>
where
    C: UseCase<CQ, HexagonalResult<()>> + 'static,
    Q: UseCase<Query, HexagonalResult<DTO<QR>>> + 'static,
{
    pub fn new(command_use_case: Arc<C>, query_use_case: Arc<Q>) -> Self {
        Self {
            command_use_case,
            query_use_case,
            _phantom: PhantomData,
        }
    }

    pub fn execute_command(&self, command: CQ) -> HexagonalResult<()> {
        self.command_use_case.execute(command)
    }

    pub fn execute_query(&self, query: Query) -> HexagonalResult<DTO<QR>> {
        self.query_use_case.execute(query)
    }
}

/// Builder for application services.
pub struct ApplicationServiceBuilder {
    use_cases: Vec<Arc<dyn UseCaseMarker + Send + Sync>>,
}

impl ApplicationServiceBuilder {
    pub fn new() -> Self {
        Self {
            use_cases: Vec::new(),
        }
    }

    pub fn with_use_case<U: UseCaseMarker + Send + Sync + 'static>(mut self, use_case: Arc<U>) -> Self {
        self.use_cases.push(use_case);
        self
    }

    pub fn build(self) -> Vec<Arc<dyn UseCaseMarker + Send + Sync>> {
        self.use_cases
    }
}

impl Default for ApplicationServiceBuilder {
    fn default() -> Self {
        Self::new()
    }
}

/// Marker trait for application services.
pub trait ApplicationServiceMarker: Send + Sync {}

/// Saga orchestrator for coordinating distributed transactions.
pub struct SagaOrchestrator<H, E, S> {
    steps: Vec<SagaStep<H, E>>,
    compensation: Vec<SagaCompensation<H, E>>,
    _phantom: PhantomData<S>,
}

struct SagaStep<H, E> {
    name: String,
    handler: Arc<H>,
    _phantom: PhantomData<E>,
}

struct SagaCompensation<H, E> {
    step_name: String,
    handler: Arc<H>,
    _phantom: PhantomData<E>,
}

impl<H, E, S> SagaOrchestrator<H, E, S>
where
    H: Send + Sync,
    E: Send + Sync,
{
    pub fn new() -> Self {
        Self {
            steps: Vec::new(),
            compensation: Vec::new(),
            _phantom: PhantomData,
        }
    }

    pub fn add_step(mut self, name: impl Into<String>, handler: Arc<H>) -> Self {
        self.steps.push(SagaStep {
            name: name.into(),
            handler,
            _phantom: PhantomData,
        });
        self
    }

    pub fn add_compensation(mut self, step_name: impl Into<String>, handler: Arc<H>) -> Self {
        self.compensation.push(SagaCompensation {
            step_name: step_name.into(),
            handler,
            _phantom: PhantomData,
        });
        self
    }
}
