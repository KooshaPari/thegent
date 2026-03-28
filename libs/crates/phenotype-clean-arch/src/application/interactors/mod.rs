//! Interactors
//! 
//! Objects that implement use cases.

/// Base interactor trait
pub trait Interactor<I, O>: Send + Sync {
    fn act(&self, input: I) -> O;
}
