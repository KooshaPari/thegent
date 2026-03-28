//! Domain Service - Stateless Domain Operations
//!
//! Domain services are used when an operation conceptually belongs to a domain
//! service rather than an entity or value object. They encapsulate business
//! logic that doesn't naturally fit within a single entity.
//!
//! ## When to Use Domain Services
//!
//! - The operation involves multiple aggregates
//! - The operation is a standalone domain concept
//! - The operation doesn't have identity
//! - The operation is stateless
//!
//! ## Example
//!
//! ```rust
//! use hexkit::domain::service::*;
//!
//! pub struct PricingService;
//!
//! impl PricingService {
//!     pub fn calculate_total(&self, items: &[i32]) -> i32 {
//!         items.iter().sum()
//!     }
//! }
//!
//! impl DomainService for PricingService {}
//! ```

/// Marker trait for domain services
pub trait DomainService: Send + Sync {}

/// Trait for calculation services
pub trait CalculationService<T, R>: DomainService {
    fn calculate(&self, input: T) -> R;
}

/// Trait for transformation services
pub trait TransformationService<T, U>: DomainService {
    fn transform(&self, input: T) -> U;
}

/// Trait for validation services
pub trait ValidationService<T>: DomainService {
    fn validate(&self, input: &T) -> Result<(), String>;
}

#[cfg(test)]
mod tests {
    use super::*;

    struct TestCalculationService;

    impl DomainService for TestCalculationService {}

    impl CalculationService<Vec<i32>, i32> for TestCalculationService {
        fn calculate(&self, input: Vec<i32>) -> i32 {
            input.iter().sum()
        }
    }

    #[test]
    fn test_calculation_service() {
        let service = TestCalculationService;
        let result = service.calculate(vec![1, 2, 3, 4, 5]);
        assert_eq!(result, 15);
    }
}
