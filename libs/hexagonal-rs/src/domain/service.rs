//! Domain Services
//!
//! Domain services are operations that don't naturally belong to a single
//! entity or value object but are part of the domain model.

use std::sync::Arc;

/// Domain service trait - operations that don't belong to a single entity.
pub trait DomainService: Send + Sync {}

/// Specification pattern for domain logic.
pub trait Specification<T>: Send + Sync
where
    T: Send + Sync + 'static,
{
    fn is_satisfied_by(&self, candidate: &T) -> bool;

    fn and(self: Arc<Self>, other: Arc<dyn Specification<T>>) -> Arc<dyn Specification<T>>
    where
        Self: Sized + 'static,
    {
        Arc::new(AndSpecification::new(self, other))
    }

    fn or(self: Arc<Self>, other: Arc<dyn Specification<T>>) -> Arc<dyn Specification<T>>
    where
        Self: Sized + 'static,
    {
        Arc::new(OrSpecification::new(self, other))
    }

    fn not(self: Arc<Self>) -> Arc<dyn Specification<T>>
    where
        Self: Sized + 'static,
    {
        Arc::new(NotSpecification::new(self))
    }
}

pub struct AndSpecification<T>
where
    T: Send + Sync + 'static,
{
    left: Arc<dyn Specification<T>>,
    right: Arc<dyn Specification<T>>,
}

impl<T> AndSpecification<T>
where
    T: Send + Sync + 'static,
{
    pub fn new(left: Arc<dyn Specification<T>>, right: Arc<dyn Specification<T>>) -> Self {
        Self { left, right }
    }
}

impl<T> Specification<T> for AndSpecification<T>
where
    T: Send + Sync + 'static,
{
    fn is_satisfied_by(&self, candidate: &T) -> bool {
        self.left.is_satisfied_by(candidate) && self.right.is_satisfied_by(candidate)
    }
}

pub struct OrSpecification<T>
where
    T: Send + Sync + 'static,
{
    left: Arc<dyn Specification<T>>,
    right: Arc<dyn Specification<T>>,
}

impl<T> OrSpecification<T>
where
    T: Send + Sync + 'static,
{
    pub fn new(left: Arc<dyn Specification<T>>, right: Arc<dyn Specification<T>>) -> Self {
        Self { left, right }
    }
}

impl<T> Specification<T> for OrSpecification<T>
where
    T: Send + Sync + 'static,
{
    fn is_satisfied_by(&self, candidate: &T) -> bool {
        self.left.is_satisfied_by(candidate) || self.right.is_satisfied_by(candidate)
    }
}

pub struct NotSpecification<T>
where
    T: Send + Sync + 'static,
{
    inner: Arc<dyn Specification<T>>,
}

impl<T> NotSpecification<T>
where
    T: Send + Sync + 'static,
{
    pub fn new(inner: Arc<dyn Specification<T>>) -> Self {
        Self { inner }
    }
}

impl<T> Specification<T> for NotSpecification<T>
where
    T: Send + Sync + 'static,
{
    fn is_satisfied_by(&self, candidate: &T) -> bool {
        !self.inner.is_satisfied_by(candidate)
    }
}

/// Factory trait for creating domain objects.
pub trait Factory<T>: Send + Sync {
    fn create(&self) -> Result<T, String>;
}
